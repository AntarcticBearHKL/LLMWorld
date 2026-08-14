"""模拟环境管理：simulation/<世界名>_<时间id>/ 结构 + 线性时间约束。

目录结构：
  simulation/<env_id>/           模拟环境根（env_id = <world_id>_<HHMM>，如 pop03_1453）
    env.json                     环境状态（world_id / start_date / last_date）
    <YYYY-MM-DD>/                模拟日期（线性逐日推进，不可跳）
      <postcode>/                地区（如 3168）
        house_XXXX/              各户模拟数据 + 每步对话 log
        population_profile_1440min.json   聚合负荷曲线（人口级模拟时）
    population/<scenario>/<date>/  聚合产物（兼容分析工具子结构）
    analysis/                    分析工具产物
    comparison/                  政策对比矩阵

时间约束：一个模拟环境只能从 start_date 线性逐日向下模拟（--date 缺省自动续跑）；
指定日期必须恰好是 last_date + 1 天。想重新开始 → 新建世界。
"""
import json
import os
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMULATION_DIR = os.path.join(PROJECT_ROOT, "simulation")


def _env_dir(env_id):
    return os.path.join(SIMULATION_DIR, env_id)


def _env_state_path(env_id):
    return os.path.join(_env_dir(env_id), "env.json")


def env_state(env_id):
    """读取环境状态 dict；不存在返回 {}。"""
    p = _env_state_path(env_id)
    if not os.path.exists(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_env_state(env_id, state):
    os.makedirs(_env_dir(env_id), exist_ok=True)
    with open(_env_state_path(env_id), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def list_env_ids(world_id):
    """simulation/ 下属于该世界的所有环境 id（如 pop03_1453）。"""
    if not os.path.isdir(SIMULATION_DIR):
        return []
    prefix = world_id + "_"
    ids = []
    for name in sorted(os.listdir(SIMULATION_DIR)):
        if name.startswith(prefix) and os.path.isdir(os.path.join(SIMULATION_DIR, name)):
            st = env_state(name)
            if st.get("world_id") == world_id or not st:
                ids.append(name)
    return ids


def latest_env(world_id):
    """最新（last_date 最大）的环境 id；无则 None。"""
    ids = list_env_ids(world_id)
    if not ids:
        return None
    return max(ids, key=lambda e: env_state(e).get("last_date") or "")


def create_env(world_id):
    """新建环境：id = <world_id>_<HHMM>；同分钟冲突追加秒。"""
    now = datetime.now()
    env_id = f"{world_id}_{now.strftime('%H%M')}"
    if os.path.isdir(_env_dir(env_id)):
        env_id = f"{world_id}_{now.strftime('%H%M%S')}"
    _write_env_state(env_id, {
        "world_id": world_id,
        "env_id": env_id,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "start_date": None,
        "last_date": None,
    })
    return env_id


def _parse_iso(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _iso(date_obj):
    return date_obj.strftime("%Y-%m-%d")


def zh_to_iso(date_str):
    """'2026年4月21日' 或 '2026-04-21' -> '2026-04-21'。"""
    from engine.world import parse_world_date
    return _iso(parse_world_date(date_str))


def iso_to_zh(iso_str):
    d = _parse_iso(iso_str)
    return f"{d.year}年{d.month}月{d.day}日"


def resolve_sim_date(world_id, date_arg=None):
    """模拟入口时间线解析（线性约束核心）。

    返回 (env_id, date_zh)。规则：
    - 无环境或未开始 → 新建环境，日期 = date_arg 或世界默认开始日期
    - 已开始 → date_arg 缺省 = last_date + 1 天；指定则必须恰好等于 last_date + 1
    - 违反线性约束 → ValueError（提示新建世界）
    """
    env_id = latest_env(world_id)
    if env_id is None:
        env_id = create_env(world_id)
    st = env_state(env_id)
    last = st.get("last_date")

    if not last:
        if date_arg:
            today = _parse_iso(zh_to_iso(date_arg))
        else:
            import config
            today = _parse_iso(zh_to_iso(config.DEFAULT_START_DATE))
        st["start_date"] = _iso(today)
        _write_env_state(env_id, st)
        return env_id, iso_to_zh(_iso(today))

    expected = _iso(_parse_iso(last) + timedelta(days=1))
    if date_arg:
        given = zh_to_iso(date_arg)
        if given != expected:
            raise ValueError(
                f"模拟环境 {env_id} 只能线性向下模拟：上次到 {last}，本次只能从 {expected} 继续；"
                f"想重新开始请新建世界")
    return env_id, iso_to_zh(expected)


def env_from_id(env_id):
    """按 id 精确查找环境；不存在/状态缺失抛 ValueError。返回 env_state。"""
    if not os.path.isdir(_env_dir(env_id)):
        raise ValueError(f"模拟环境 {env_id} 不存在（simulation/ 下查找）")
    st = env_state(env_id)
    if not st.get("world_id"):
        raise ValueError(f"模拟环境 {env_id} 状态缺失（env.json）")
    return st


def continue_env_date(env_id):
    """续跑已有环境：起始日期 = last_date + 1 天（线性约束）。返回 date_zh。"""
    st = env_from_id(env_id)
    last = st.get("last_date")
    if not last:
        raise ValueError(f"模拟环境 {env_id} 尚未开始（env.json 无 last_date），请用 --start 新建")
    return iso_to_zh(_iso(_parse_iso(last) + timedelta(days=1)))


def update_env_date(env_id, date_zh_or_iso):
    """每天模拟完成后更新环境 last_date。"""
    st = env_state(env_id)
    st["last_date"] = "-" in str(date_zh_or_iso) and str(date_zh_or_iso) or zh_to_iso(date_zh_or_iso)
    _write_env_state(env_id, st)


def env_house_dir(env_id, date_iso, postcode, house_id):
    """house 数据目录：simulation/<env>/<date>/<postcode>/<house_id>/"""
    return os.path.join(_env_dir(env_id), date_iso, postcode, house_id)


def sim_root(world_id):
    """分析工具用：返回该世界最新模拟环境的根目录。

    无环境时回退到 simulation/<world_id>（路径不存在，由调用方按"无数据"处理，不抛错）。
    """
    env_id = latest_env(world_id)
    if env_id is None:
        return os.path.join(SIMULATION_DIR, world_id)
    return _env_dir(env_id)
