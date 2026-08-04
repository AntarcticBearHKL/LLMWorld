"""人口生成叠加 LLM（计划37）：程序化骨架 + LLM 多样化细节。

设计：
1. 程序化基线：复用 population._build_template 生成"默认家庭"（成员数/年龄/性别/
   Big Five/电器 确定性且 census 校准——这部分绝不让 LLM 自由发挥，保证物理一致）
2. LLM 差异化重写：把基线家庭 + 社区语境 + 已有家庭摘要 给 LLM，
   让它生成更丰富独特的细节（多元文化姓名/职业/作息/爱好/性格行为描述/家庭故事）
3. 校验合并：成员数与年龄以程序化为准（LLM 不可改）；LLM 输出缺失/非法 → 回退基线
4. 防重复：每户 prompt 含"社区已有家庭摘要"，LLM 看到社区全貌避免同质化

用法：
    python Implement/population_llm.py pop06 --count 3 --seed 7
"""

import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from population import (_build_template, _quota_distribution, CLAYTON_POSTCODE,
                        CLAYTON_CITY, CLAYTON_DISTRICT, build_population)
from engine import utils, SubAgent
from engine.prompt import Prompt
import config


def community_context(rng, existing_households):
    """社区已有家庭摘要（防重复：名字/职业/习惯）。"""
    if not existing_households:
        return "（暂无其他家庭——你是这个社区的第一个家庭）"
    lines = []
    for h in existing_households[-8:]:   # 只给最近 8 户，控制 token
        members = h.get("members", [])
        brief = "、".join(f"{m.get('name','?')}({m.get('occupation','?')})" for m in members[:3])
        habits = "; ".join(f"{m.get('name','?')}：{m.get('habits',{}).get('hobbies',[])}"
                           for m in members[:2])
        lines.append(f"- {h.get('type','?')}：{brief}；爱好：{habits}")
    return "\n".join(lines)


def llm_fill_details(base_household, community_text, prompt, rng):
    """用 LLM 差异化重写基线家庭细节。返回 (household, warnings)。

    成员数/年龄/性别/Big Five/电器 以基线为准；LLM 输出非法时逐字段回退基线。
    """
    warnings = []
    household = json.loads(json.dumps(base_household))   # 深拷贝基线

    rendered = prompt.load("generate_step4_household_details",
                           household_json=json.dumps(base_household, ensure_ascii=False, indent=2),
                           community_summary=community_text)

    try:
        result = SubAgent.single_call(rendered, json_mode=True, thinking=config.THINKING)
        content = result["content"] if isinstance(result, dict) else result
        data = utils.parse_json_response(content)
    except Exception as e:
        warnings.append(f"LLM 生成失败（回退基线）：{e}")
        return household, warnings

    # 住宅名与家庭故事（可选）
    if data.get("home_name"):
        household["home"]["name"] = str(data["home_name"])
    if data.get("story"):
        household["story"] = str(data["story"])
    household["llm_generated"] = True

    # 成员：数量必须与基线一致；逐字段合并（缺失回退基线）
    llm_members = data.get("members", [])
    if len(llm_members) != len(household["members"]):
        warnings.append(f"LLM 成员数 {len(llm_members)} != 基线 {len(household['members'])}，成员保持基线")
        return household, warnings

    for i, (base_m, llm_m) in enumerate(zip(household["members"], llm_members)):
        if not isinstance(llm_m, dict):
            warnings.append(f"成员 {i} LLM 输出非法，保持基线")
            continue
        # 名字（必须非空）
        name = str(llm_m.get("name", "")).strip()
        if name and len(name) >= 2:
            base_m["name"] = name
        # 职业
        occ = str(llm_m.get("occupation", "")).strip()
        if occ:
            base_m["occupation"] = occ
        # 作息/运动/爱好（可选项，缺失回退基线）
        for field, key in [("wake_time", "habits"), ("sleep_time", "habits"),
                           ("exercise", "habits"), ("hobbies", "habits")]:
            if field in llm_m and key == "habits":
                base_m.setdefault("habits", {})
                if field == "hobbies" and isinstance(llm_m[field], list):
                    base_m["habits"]["hobbies"] = [str(x) for x in llm_m[field]][:3]
                elif llm_m[field]:
                    base_m["habits"][field] = str(llm_m[field])
        # 性格行为描述（基于基线的 Big Five，LLM 只写叙事不写分数）
        bt = str(llm_m.get("behavior_text", "")).strip()
        if bt:
            base_m["personality"]["behavior_text"] = bt

    return household, warnings


def build_population_llm(world_id, count, seed=42, household_types=None):
    """混合生成：程序化骨架（配额/类型/成员关联/Big Five/电器）+ LLM 细节。"""
    rng = random.Random(seed)
    utils.set_seed(seed)

    if household_types is None:
        type_counts = _quota_distribution(count, rng)
        household_types = [t for t, n in type_counts.items() for _ in range(n)]
        rng.shuffle(household_types)

    prompt = Prompt()
    existing = []          # 已生成家庭（防重复上下文）
    all_households = []    # 完整家庭列表（落盘用）

    print(f"LLM 混合人口生成：world={world_id}，{count} 户，种子 {seed}")
    for i in range(count):
        htype = household_types[i % len(household_types)]
        # 1) 程序化基线（确定性骨架）
        base = _build_template(htype, rng)
        # 2) LLM 差异化细节（带社区上下文防重复）
        community = community_context(rng, existing)
        household, warnings = llm_fill_details(base, community, prompt, rng)
        for w in warnings:
            print(f"  [警告] {w}")
        all_households.append(household)
        existing.append(household)
        print(f"  [{i + 1}/{count}] {household.get('type','?')} → "
              f"{'、'.join(m['name'] for m in household['members'])}"
              f"{'（LLM）' if household.get('llm_generated') else '（基线）'}")

    # 3) 复用 build_population 的落盘逻辑（household.json + world.json）
    meta = _save_world(world_id, all_households, rng, seed)
    return meta


def _save_world(world_id, households, rng, seed):
    """落盘：复用与 build_population 相同的目录结构与 world.json 格式。"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    world_dir = os.path.join(project_root, "worlds", world_id)
    district_dir = os.path.join(world_dir, CLAYTON_POSTCODE)
    os.makedirs(district_dir, exist_ok=True)

    households_meta = []
    for i, household in enumerate(households):
        house_id = f"house_{i + 1:04d}"
        house_dir = os.path.join(district_dir, house_id)
        os.makedirs(house_dir, exist_ok=True)
        with open(os.path.join(house_dir, "household.json"), "w", encoding="utf-8") as f:
            json.dump(household, f, ensure_ascii=False, indent=2)
        households_meta.append({
            "house_id": house_id,
            "type": household.get("type", "?"),
            "members_count": len(household.get("members", [])),
            "rooms_count": len(household.get("home", {}).get("rooms", [])),
            "llm_generated": household.get("llm_generated", False),
        })

    district = {
        "postcode": CLAYTON_POSTCODE,
        "location": {"city": CLAYTON_CITY, "district": CLAYTON_DISTRICT,
                     "coordinates": {"lat": -37.916, "lon": 145.123}},
        "economic_level": "中",
    }
    with open(os.path.join(district_dir, "district.json"), "w", encoding="utf-8") as f:
        json.dump(district, f, ensure_ascii=False, indent=2)

    world_meta = {
        "world_id": world_id,
        "created_at": "",
        "user_prompt": f"人口生成 LLM 混合模式（seed={seed}，程序化骨架 + LLM 细节）",
        "generator": "population_llm.py",
        "district": {
            "postcode": CLAYTON_POSTCODE,
            "city": CLAYTON_CITY,
            "district": CLAYTON_DISTRICT,
            "economic_level": "中",
        },
        "households": households_meta,
    }
    with open(os.path.join(world_dir, "world.json"), "w", encoding="utf-8") as f:
        json.dump(world_meta, f, ensure_ascii=False, indent=2)
    return world_meta


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="人口生成 LLM 混合模式")
    parser.add_argument("world_id", help="新世界ID，如 pop06")
    parser.add_argument("--count", type=int, default=3, help="家庭数量（≤10）")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    build_population_llm(args.world_id, args.count, args.seed)
    print(f"完成：worlds/{args.world_id}/")
