"""统一世界生成器 v1 —— 单一生成方式。

流程（每户）：
  1. 读取 Data/ 地区描述（clayton_3168_profile.md）
  2. LLM：由地区描述生成 N 种家庭类型（--count 指定）
  3. 每户：按家庭类型从 Persona 合成人格库抽样 N 位成员画像
  4. LLM 校验：画像与家庭类型是否自洽；不合格 -> 换一批重新抽样（--max-retry 次）
  5. LLM：由家庭类型 + 成员画像生成房间布局与家电配置、成员档案
  6. 结构校验失败 -> 重生成（≤2 次）-> 仍失败回退程序化模板（population.py）

用法：
  python src/generate_world.py pop03 --count 3 --seed 42 --max-retry 3
"""
import argparse
import json
import os
import random
import re
import sys
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import utils, SubAgent
from engine.prompt import Prompt
import config
from appliances import get_supported_appliances_text, get_appliance_schemas_text

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA_DIR = os.path.join(PROJECT_ROOT, "Persona")
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
DEFAULT_DISTRICT_FILE = os.path.join(DATA_DIR, "clayton_3168_profile.md")

CLAYTON_POSTCODE = "3168"
CLAYTON_CITY = "墨尔本"
CLAYTON_DISTRICT = "Clayton"

# 回退模板的类型关键词映射（population.py 的程序化 8 类）
FALLBACK_TYPE_KEYWORDS = [
    (["单亲"], "single_parent"),
    (["独居"], "single_living"),
    (["合租", "室友"], "share_house"),
    (["学生", "留学"], "international_student"),
    (["多代", "三代"], "multigenerational"),
    (["退休", "老年"], "retired_couple"),
    (["有孩", "孩子", "家庭"], "family_with_kids"),
]
FALLBACK_DEFAULT = "young_couple"

MAX_BUILD_ATTEMPTS = 3  # 房间家电生成的 LLM 重试次数（含首次）


def load_district_text(path=None):
    path = path or DEFAULT_DISTRICT_FILE
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    print(f"[警告] 未找到地区描述 {path}，使用内置默认描述")
    return ("位于墨尔本东南部的 Clayton 3168 邮编区，是莫纳什大学所在地的多元文化社区。"
            "人口结构年轻（中位年龄 28 岁），学生与年轻专业人士占比高；家庭形态以夫妻无孩、"
            "合租与学生家庭为主；住房以联排、单元房与公寓居多，租房比例高。"
            "家庭周收入中位数约 1778 澳元。")


def _parse_json_lenient(text):
    """容错解析 LLM 输出：容忍代码围栏/首尾噪声/单引号属性与值/尾逗号/注释/JS 字面量。

    策略：逐级修复，每级修复后尝试标准 json.loads；全部失败则抛最后异常。
    """
    text = str(text).strip()
    text = utils.clean_json_text(text)  # 剥 ``` 代码围栏
    if text.startswith("\ufeff"):  # BOM
        text = text[1:].strip()
    # 剥离开头噪声（直到第一个 { 或 [）
    start = None
    for i, ch in enumerate(text):
        if ch in "[{":
            start = i
            break
    if start is not None:
        text = text[start:]
    # 去掉注释
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)

    def _load(t):
        return json.loads(t)

    # 第 1 级：原样
    try:
        return _load(text)
    except Exception:
        pass
    # 第 1.5 级：双花括号归一化（LLM 偶发照抄模板示例的 {{ }} 转义）
    t1 = re.sub(r"\{\{", "{", text)
    t1 = re.sub(r"\}\}", "}", t1)
    try:
        return _load(t1)
    except Exception:
        pass
    # 第 2 级：去掉尾逗号 + JS 字面量 → JSON 字面量
    t2 = re.sub(r",\s*([}\]])", r"\1", text)
    t2 = re.sub(r"\bTrue\b", "true", t2)
    t2 = re.sub(r"\bFalse\b", "false", t2)
    t2 = re.sub(r"\bNone\b", "null", t2)
    try:
        return _load(t2)
    except Exception:
        pass
    # 第 3 级：单引号属性名（{ 'xxx': / , 'xxx': ）、字符串值（: 'xxx' ,），
    #        最后兜底把剩余单引号对整体转双引号（覆盖数组元素 ['a', 'b'] 等场景）
    t3 = re.sub(r"([{,])\s*'([^']+)'\s*:", r'\1"\2":', t2)
    t3 = re.sub(r":\s*'([^']+)'(\s*[,}\]])", r':"\1"\2', t3)
    t3 = re.sub(r"'([^']*)'", r'"\1"', t3)
    try:
        return _load(t3)
    except Exception as e:
        raise ValueError(f"JSON 容错解析失败（原始输出前 300 字符：{text[:300]}）: {e}")


class ChatLogger:
    """LLM 调用记录器：每次调用写一份可读 .md + 追加一条结构化 .jsonl。

    可读文件: log/<prefix><stage>.md   —— 提示词 / 思考(thinking) / 回复全文
              prefix 为调用方所属（如 house_0001_ / global_），同一户的文件后缀一致
    结构化:   log/llm_chat.jsonl        —— 每行一条完整记录（含成败/错误/重试次数）
    """

    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.jsonl_path = os.path.join(log_dir, "llm_chat.jsonl")
        self._seq = 0
        self._lock = threading.Lock()  # 多户并行写日志防交错

    def record(self, stage, prompt, response, reasoning=None, ok=True, error=None,
               attempt=1, prefix=""):
        with self._lock:
            self._seq += 1
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = {
                "seq": self._seq, "time": ts, "prefix": prefix, "stage": stage,
                "attempt": attempt, "ok": ok, "prompt": prompt, "response": response,
                "reasoning": reasoning, "error": error,
            }
            with open(self.jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            # 同一户同一阶段的 md 只保留最终一份（重试覆盖，后缀固定不跳号）
            md_path = os.path.join(self.log_dir, f"{prefix}{stage}.md")
            lines = [f"# [{ts}] {prefix}{stage}",
                     "\n## 提示词（Prompt）\n", prompt or "(空)", ]
            if reasoning:
                lines += ["\n## 思考（Thinking）\n", reasoning]
            lines += ["\n## 回复（Response）\n", response or "(空)"]
            if error:
                lines += ["\n## 错误（Error）\n", str(error)]
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")


def llm_json(prompt, label, attempts=2, logger=None, stage=None, thinking=None,
             prefix=""):
    """调用 LLM 并解析 JSON；失败静默重试 attempts 次，返回 (data, warnings)。

    重试不产生可见提示（工程兜底），最终失败才返回一条警告。
    """
    warnings = []
    if thinking is None:
        thinking = config.THINKING
    content = reasoning = None
    for i in range(attempts):
        try:
            result = SubAgent.single_call(prompt, json_mode=True, thinking=thinking)
            content = result["content"] if isinstance(result, dict) else result
            reasoning = result.get("reasoning_content") if isinstance(result, dict) else None
            try:
                data = utils.parse_json_response(content)
            except Exception:
                data = _parse_json_lenient(content)
            if isinstance(data, dict) or isinstance(data, list):
                if logger:
                    logger.record(stage, prompt, content, reasoning=reasoning,
                                  ok=True, attempt=i + 1, prefix=prefix)
                return data, warnings
            raise ValueError("JSON 顶层必须是对象或数组")
        except Exception as e:
            if logger:
                logger.record(stage, prompt, content, reasoning=reasoning,
                              ok=False, error=str(e), attempt=i + 1, prefix=prefix)
            if i < attempts - 1:
                prompt += ("\n\n重要：你上一次的输出不是合法 JSON。"
                           "请重新输出，只输出一个合法 JSON 对象，不要任何解释。")
    warnings.append(f"{label} 调用异常：{e}")
    return None, warnings


def generate_household_types(district_text, count, prompt_obj, logger=None,
                             thinking=None, prefix=""):
    """步骤 1：地区描述 → count 种家庭类型。返回 [(type, desc, members, housing), ...]"""
    rendered = prompt_obj.load("generate_world_step1_types",
                               district_info=district_text, count=count)
    data, warnings = llm_json(rendered, "家庭类型生成", logger=logger,
                              stage="step1_types", thinking=thinking, prefix=prefix)
    for w in warnings:
        print(f"  [警告] {w}")
    if not isinstance(data, dict) or not isinstance(data.get("household_types"), list):
        print("[错误] 家庭类型生成结果结构非法，终止")
        sys.exit(1)
    types = []
    for t in data["household_types"]:
        if not isinstance(t, dict) or not str(t.get("type", "")).strip():
            continue
        try:
            members = int(t.get("typical_members", 2))
        except (TypeError, ValueError):
            members = 2
        members = max(1, min(8, members))
        types.append({
            "type": str(t["type"]).strip(),
            "description": str(t.get("description", "")).strip(),
            "typical_members": members,
            "housing_hint": str(t.get("housing_hint", "")).strip(),
        })
    if not types:
        print("[错误] 家庭类型列表为空，终止")
        sys.exit(1)
    return types


def sample_personas(household_type, attempt_seed):
    """步骤 3：从 Persona 库按成员数抽样，渲染成中文画像文本。返回 (texts, rows)。"""
    if PERSONA_DIR not in sys.path:
        sys.path.insert(0, PERSONA_DIR)
    from sampler import PersonaSampler
    from persona_render import PersonaRenderer
    n = household_type["typical_members"]
    sampler = PersonaSampler(data_dir=PERSONA_DIR, seed=attempt_seed)
    rows = sampler.sample(n)  # 使用内部 rng（已按 attempt_seed 播种）
    renderer = PersonaRenderer(PERSONA_DIR)
    texts = ["【成员 %d】\n%s" % (i + 1, renderer.render(r)) for i, r in enumerate(rows)]
    return texts, rows


def align_personas(household_type, persona_texts, prompt_obj, logger=None,
                   thinking=None, prefix=""):
    """步骤 2：LLM 直接把抽样画像对齐到家庭设定——冲突部分改写，无关部分原样保留。

    不校验、不解释"哪里不对"，直接返回符合设定的最终画像。
    返回 (final_texts, warnings)；final_texts 为 None 表示输出异常（调用方沿用原始画像）。
    """
    rendered = prompt_obj.load(
        "generate_world_step2_align",
        household_type=household_type["type"],
        household_description=household_type["description"],
        member_count=household_type["typical_members"],
        persona_texts="\n\n".join(persona_texts),
    )
    data, warnings = llm_json(rendered, "画像对齐", logger=logger,
                              stage="step2_align", thinking=thinking, prefix=prefix)
    if not isinstance(data, dict) or not isinstance(data.get("members"), list):
        return None, warnings + ["画像对齐输出异常，沿用原始画像"]
    aligned = [str(m).strip() for m in data["members"] if str(m).strip()]
    if len(aligned) != len(persona_texts):
        return None, warnings + [f"画像对齐成员数不符，沿用原始画像"]
    return aligned, warnings


def build_household(household_type, persona_texts, district_text, prompt_obj,
                    logger=None, thinking=None, prefix=""):
    """步骤 3：LLM 由对齐后的画像 + 家庭设定生成房间家电与成员档案。返回 household dict。"""
    rendered = prompt_obj.load(
        "generate_world_step3_household",
        district_info=district_text,
        household_type=household_type["type"],
        household_description=household_type["description"],
        housing_hint=household_type["housing_hint"],
        persona_texts="\n\n".join(persona_texts),
        supported_appliances=get_supported_appliances_text(),
        appliance_schemas=get_appliance_schemas_text(),
    )
    data, warnings = llm_json(rendered, "家庭生成", logger=logger,
                              stage="step3_household", thinking=thinking, prefix=prefix)
    return data, warnings


SUPPORTED_APPLIANCES = None


def _supported_set():
    global SUPPORTED_APPLIANCES
    if SUPPORTED_APPLIANCES is None:
        from appliances import get_supported_appliances
        SUPPORTED_APPLIANCES = set(get_supported_appliances())
    return SUPPORTED_APPLIANCES


def _repair_household(h):
    """轻量修补：补齐缺失字段/默认值，过滤非法家电。返回 (ok, problems)。"""
    problems = []
    if not isinstance(h, dict):
        return False, ["顶层不是对象"]
    home = h.get("home")
    if not isinstance(home, dict):
        return False, ["缺少 home"]
    rooms = home.get("rooms")
    if not isinstance(rooms, list) or not rooms:
        return False, ["home.rooms 缺失或为空"]
    supported = _supported_set()
    for room in rooms:
        if not isinstance(room, dict):
            problems.append("房间非法，跳过")
            continue
        room.setdefault("size", 0)
        apps = room.get("appliances")
        if not isinstance(apps, list):
            room["appliances"] = []
            continue
        kept = []
        for app in apps:
            if not isinstance(app, dict) or app.get("type") not in supported:
                problems.append(f"非法家电 {app.get('type') if isinstance(app, dict) else app}，已剔除")
                continue
            app.setdefault("brand", "Generic")
            app.setdefault("power", None)
            app.setdefault("age", 0)
            kept.append(app)
        room["appliances"] = kept
    members = h.get("members")
    if not isinstance(members, list) or not members:
        return False, ["members 缺失或为空"]
    for m in members:
        if not isinstance(m, dict):
            problems.append("成员非法，跳过")
            continue
        m.setdefault("gender", "未知")
        m.setdefault("occupation", "无业")
        m.setdefault("work_schedule", {"start": "09:00", "end": "17:00",
                                       "remote": False, "work_days": [1, 2, 3, 4, 5]})
        pers = m.setdefault("personality", {})
        if not isinstance(pers, dict):
            m["personality"] = {"traits": []}
            pers = m["personality"]
        pers.setdefault("traits", [])
        pers.setdefault("behavior_text", "")
        pers.setdefault("energy_awareness", "低")   # 分析工具分组依赖；缺失兜底
        pers.setdefault("news_sensitivity", "中")   # 模拟提示词拼接；缺失兜底
        if not isinstance(pers.get("big_five"), dict):
            pers["big_five"] = {}                   # 分析工具归因依赖；缺失兜底
        habits = m.setdefault("habits", {})
        if not isinstance(habits, dict):
            m["habits"] = {}
            habits = m["habits"]
        habits.setdefault("wake_time", "07:30")
        habits.setdefault("sleep_time", "23:00")
        habits.setdefault("exercise", "偶尔散步")
        habits.setdefault("hobbies", [])
        health = m.setdefault("health", {})
        if not isinstance(health, dict):
            m["health"] = {}
        health.setdefault("condition", "良好")
        health.setdefault("temperature_preference", {"summer": 26, "winter": 22})
        papps = m.get("personal_appliances")
        if not isinstance(papps, list):
            m["personal_appliances"] = []
        else:
            kept = []
            for app in papps:
                if not isinstance(app, dict) or app.get("type") not in supported:
                    problems.append(f"非法个人家电 {app.get('type') if isinstance(app, dict) else app}，已剔除")
                    continue
                app.setdefault("brand", "Generic")
                app.setdefault("power", None)
                app.setdefault("age", 0)
                kept.append(app)
            m["personal_appliances"] = kept
        if not (str(m.get("name", "")).strip() and isinstance(m.get("age"), int)):
            problems.append(f"成员 {m.get('name', '?')} 缺姓名/年龄")
    return True, problems


def fallback_household(household_type, rng):
    """LLM 多次失败后的程序化回退（population.py 模板）。"""
    from population import _build_template
    key = FALLBACK_DEFAULT
    text = household_type["type"] + household_type["description"]
    for keywords, tkey in FALLBACK_TYPE_KEYWORDS:
        if any(k in text for k in keywords):
            key = tkey
            break
    h = _build_template(key, rng)
    h["llm_generated"] = False
    return h


def generate_one_household(household_type, district_text, rng, prompt_obj,
                           logger=None, thinking=None, prefix=""):
    """单户完整流程：抽样 → LLM 直接对齐画像到家庭设定 → 生成房间电器。直线三步，无分支。

    返回 (household, notes, persona_texts, original_persona_texts, persona_seed)。
    persona_texts 为最终采用的画像（已对齐）；original_persona_texts 为抽样原始画像。
    """
    notes = []
    attempt_seed = rng.randint(0, 2 ** 31 - 1)
    persona_texts, rows = sample_personas(household_type, attempt_seed)
    original_persona_texts = list(persona_texts)

    aligned_texts, warnings = align_personas(household_type, persona_texts, prompt_obj,
                                             logger=logger, thinking=thinking, prefix=prefix)
    notes.extend(warnings)
    if aligned_texts is not None:
        persona_texts = aligned_texts

    for attempt in range(MAX_BUILD_ATTEMPTS):
        household, warnings = build_household(household_type, persona_texts,
                                              district_text, prompt_obj,
                                              logger=logger, thinking=thinking,
                                              prefix=prefix)
        notes.extend(warnings)
        if household is None:
            continue
        ok, problems = _repair_household(household)
        if ok:
            household["llm_generated"] = True
            return household, notes, persona_texts, original_persona_texts, attempt_seed
        notes.append(f"家庭结构校验失败（第 {attempt + 1} 次）：{problems}")

    notes.append("LLM 家庭生成多次失败，回退程序化模板")
    household = fallback_household(household_type, rng)
    return household, notes, persona_texts, original_persona_texts, attempt_seed


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_world(world_id, district_text, seed):
    """建世界目录 + log/ + district.json + world.json 骨架（立即落盘）。返回 (world_dir, log_dir)。"""
    world_dir = os.path.join(PROJECT_ROOT, "worlds", world_id)
    district_dir = os.path.join(world_dir, CLAYTON_POSTCODE)
    log_dir = os.path.join(world_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(district_dir, exist_ok=True)

    district = {
        "postcode": CLAYTON_POSTCODE,
        "location": {"city": CLAYTON_CITY, "district": CLAYTON_DISTRICT,
                     "coordinates": {"lat": -37.916, "lon": 145.123}},
        "economic_level": "中",
        "description": district_text,
    }
    _write_json(os.path.join(district_dir, "district.json"), district)

    world_meta = {
        "world_id": world_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_prompt": f"统一生成器：地区描述 -> 家庭类型 -> Persona 抽样校验 -> 房间家电（seed={seed}）",
        "generator": "generate_world.py v2",
        "district": {
            "postcode": CLAYTON_POSTCODE,
            "city": CLAYTON_CITY,
            "district": CLAYTON_DISTRICT,
            "economic_level": "中",
        },
        "households": [],
    }
    _write_json(os.path.join(world_dir, "world.json"), world_meta)
    return world_dir, log_dir


def save_household_types(world_id, household_types):
    """步骤 1 完成后立即落盘家庭类型清单。"""
    _write_json(os.path.join(PROJECT_ROOT, "worlds", world_id, "household_types.json"),
                {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "household_types": household_types})


def save_household_artifacts(world_id, idx, persona_texts, original_persona_texts,
                             persona_seed, household):
    """每户生成完成后立即落盘：personas.json（原始+最终画像）+ household.json。"""
    district_dir = os.path.join(PROJECT_ROOT, "worlds", world_id, CLAYTON_POSTCODE)
    house_id = f"house_{idx + 1:04d}"
    house_dir = os.path.join(district_dir, house_id)
    os.makedirs(house_dir, exist_ok=True)

    _write_json(os.path.join(house_dir, "personas.json"), {
        "seed": persona_seed,
        "persona_texts": persona_texts,                    # 对齐后的最终画像
        "original_persona_texts": original_persona_texts,  # 抽样原始画像（可对比）
    })
    _write_json(os.path.join(house_dir, "household.json"), household)
    return house_id


def update_world_meta(world_id, house_meta):
    """每户完成后增量更新 world.json 的 households 列表。"""
    world_path = os.path.join(PROJECT_ROOT, "worlds", world_id, "world.json")
    with open(world_path, "r", encoding="utf-8") as f:
        world_meta = json.load(f)
    world_meta.setdefault("households", []).append(house_meta)
    _write_json(world_path, world_meta)
    return world_meta


def _household_worker(idx, htype, world_id, district_text, prompt_obj, log_dir,
                      thinking, base_seed):
    """单户完整流程，在一个独立进程中完成：抽样 → 画像对齐 → 生成房间家电 → 检查 → 落盘。

    返回 (house_meta, household, notes, error, tokens)。多进程参数必须全部可 pickle。
    """
    try:
        rng = random.Random(base_seed * 10007 + idx)  # 每户独立种子，并行/串行均可复现
        prefix = f"house_{idx + 1:04d}_"              # 每户固定 log 文件后缀
        logger = ChatLogger(log_dir)                  # 进程内创建（logger 对象不可跨进程）
        household, notes, personas, original_personas, p_seed = \
            generate_one_household(htype, district_text, rng, prompt_obj,
                                   logger=logger, thinking=thinking, prefix=prefix)
        house_id = save_household_artifacts(world_id, idx, personas, original_personas,
                                            p_seed, household)
        house_meta = {
            "house_id": house_id,
            "type": household.get("type", "?"),
            "members_count": len(household.get("members", [])),
            "rooms_count": len(household.get("home", {}).get("rooms", [])),
            "llm_generated": household.get("llm_generated", False),
        }
        tokens = SubAgent.get_tokens()  # (缓存未命中, 命中, 输出) 本进程累计
        return house_meta, household, notes, None, tokens
    except Exception as e:
        return None, None, [f"进程异常：{e}"], str(e), (0, 0, 0)


def main():
    parser = argparse.ArgumentParser(
        description="统一世界生成器：地区描述 -> 家庭类型 -> Persona 抽样校验 -> 房间家电")
    parser.add_argument("world_id", help="新世界ID（worlds/ 下的文件夹名）")
    parser.add_argument("--count", type=int, default=3, help="家庭数量（1-10，默认 3）")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED, help="随机种子（可复现）")
    parser.add_argument("--district", default=None, help="地区描述文件（默认 Data/clayton_3168_profile.md）")
    parser.add_argument("--think", action="store_true",
                        help="开启深度思考并记录思考内容到 log/（慢约 90 倍，默认关闭）")
    args = parser.parse_args()

    if not (1 <= args.count <= 10):
        print(f"[错误] 每世界最多 10 户（收到 {args.count}）")
        sys.exit(1)
    world_dir = os.path.join(PROJECT_ROOT, "worlds", args.world_id)
    if os.path.isdir(world_dir):
        print(f"[错误] 世界 {args.world_id} 已存在，请使用新世界 ID")
        sys.exit(1)

    utils.set_seed(args.seed)
    prompt_obj = Prompt()
    district_text = load_district_text(args.district)

    # 0. 先建世界目录 + log/，再开始任何步骤（每步产物都会立即落盘）
    world_dir, log_dir = init_world(args.world_id, district_text, args.seed)
    logger = ChatLogger(log_dir)
    print("=" * 60)
    print(f"统一世界生成器 v2：world={args.world_id}，{args.count} 户，种子 {args.seed}"
          f"{'，深度思考开启' if args.think else ''}")
    print("=" * 60)
    print(f"  LLM 聊天记录目录：{log_dir}")
    print(f"  世界目录：{world_dir}")

    print("\n[步骤 1] 由地区描述生成家庭类型...")
    household_types = generate_household_types(district_text, args.count, prompt_obj,
                                               logger=logger, thinking=args.think,
                                               prefix="global_")
    save_household_types(args.world_id, household_types)  # 立即落盘
    print(f"  [OK] 已保存 {args.count} 种家庭类型 -> worlds/{args.world_id}/household_types.json")
    for i, t in enumerate(household_types):
        print(f"    {i + 1}. {t['type']}（{t['typical_members']} 人）— {t['housing_hint']}")

    # 步骤 2-3：每户（抽样+画像对齐+生成房间家电+检查）一个独立进程，最多 12 个进程并行
    max_workers = min(len(household_types), 12)
    print(f"\n[步骤 2-3] 并行生成 {len(household_types)} 户（{max_workers} 个进程同时处理）…")
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_household_worker, idx, htype, args.world_id, district_text,
                        prompt_obj, log_dir, args.think, args.seed): idx
            for idx, htype in enumerate(household_types)
        }
        results = {}
        for fut in as_completed(futures):
            idx = futures[fut]
            try:
                results[idx] = fut.result()
            except Exception as e:  # worker 已兜底，这里仅防御
                results[idx] = (None, None, [f"进程异常：{e}"], str(e), (0, 0, 0))

    # 主进程按家庭顺序输出 + 增量更新 world.json（串行，无并发写冲突）
    total_miss = total_hit = total_completion = 0
    for idx in range(len(household_types)):
        house_meta, household, notes, error, tokens = results[idx]
        total_miss += tokens[0]
        total_hit += tokens[1]
        total_completion += tokens[2]
        if house_meta is None:
            print(f"\n  [失败] house_{idx + 1:04d} 生成失败：{error}")
            continue
        for n in notes:
            print(f"    [备注] {n}")
        update_world_meta(args.world_id, house_meta)  # 增量更新 world.json
        print(f"  [OK] {house_meta['house_id']}：{house_meta['type']}"
              f"{'（LLM 生成）' if house_meta['llm_generated'] else '（程序化回退）'}"
              f" — {'、'.join(m.get('name', '?') for m in household.get('members', []))}"
              f" -> 已落盘")

    total = total_miss + total_hit + total_completion
    print(f"\n=== 完成：worlds/{args.world_id}/ （{len(household_types)} 户）===")
    print(f"  Token 消耗：{total}（缓存未命中 {total_miss} + "
          f"缓存命中 {total_hit} + 输出 {total_completion}，跨 {max_workers} 进程汇总）")
    print(f"  LLM 聊天记录：{log_dir}（每步 .md + llm_chat.jsonl）")
    print(f"  下一步：python src/simulate.py {args.world_id} --days 1 --no-input")


if __name__ == "__main__":
    main()
