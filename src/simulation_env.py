"""Simulation environment management: simulation/<world>_<time-id>/ structure + linear time constraint.

Directory layout:
  simulation/<env_id>/            simulation environment root (env_id = <world_id>_<HHMM>, e.g. pop03_1453)
    env.json                     environment state (world_id / start_date / last_date)
    <YYYY-MM-DD>/                simulation date (advances linearly day by day, no skipping)
      <postcode>/                district (e.g. 3168)
        house_XXXX/              per-household simulation data + per-step conversation logs
        population_profile_1440min.json   aggregate load profile (population-level simulation)
    population/<scenario>/<date>/   aggregate artifacts (sub-structure for analysis tools)
    analysis/                    analysis tool artifacts
    comparison/                  policy comparison matrix

Time constraint: a simulation environment can only advance linearly from start_date, one day at a
time (--date defaults to auto-resume); an explicit date must be exactly last_date + 1 day.
To restart from scratch, create a new world.
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
    """Read the environment state dict; return {} if missing."""
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
    """All environment ids belonging to this world under simulation/ (e.g. pop03_1453)."""
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
    """The latest environment id (largest last_date); None if none exist."""
    ids = list_env_ids(world_id)
    if not ids:
        return None
    return max(ids, key=lambda e: env_state(e).get("last_date") or "")


def create_env(world_id):
    """Create a new environment: id = <world_id>_<HHMM>; append seconds on same-minute collision."""
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
    """Normalize an ISO date 'YYYY-MM-DD' or compact 'YYYYMMDD' string to 'YYYY-MM-DD'."""
    from engine.world import parse_world_date
    return _iso(parse_world_date(date_str))


def iso_to_zh(iso_str):
    d = _parse_iso(iso_str)
    return _iso(d)


def resolve_sim_date(world_id, date_arg=None):
    """Simulation entry-point timeline resolution (core of the linear constraint).

    Returns (env_id, date). Rules:
    - No environment or not started -> create one; date = date_arg or the world's default start date
    - Already started -> date_arg defaults to last_date + 1 day; if given, it must equal last_date + 1
    - Violating the linear constraint -> ValueError (prompt to create a new world)
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
                f"Simulation environment {env_id} can only advance linearly: simulated up to "
                f"{last}, so the next run must start from {expected}; to restart, create a new world")
    return env_id, iso_to_zh(expected)


def env_from_id(env_id):
    """Find an environment by exact id; raise ValueError if missing / state missing.
    Returns env_state."""
    if not os.path.isdir(_env_dir(env_id)):
        raise ValueError(f"Simulation environment {env_id} does not exist (look under simulation/)")
    st = env_state(env_id)
    if not st.get("world_id"):
        raise ValueError(f"Simulation environment {env_id} has no state (env.json)")
    return st


def continue_env_date(env_id):
    """Resume an existing environment: start date = last_date + 1 day (linear constraint).
    Returns the date string."""
    st = env_from_id(env_id)
    last = st.get("last_date")
    if not last:
        raise ValueError(f"Simulation environment {env_id} has not started (no last_date in "
                         f"env.json); please use --start to create one")
    return iso_to_zh(_iso(_parse_iso(last) + timedelta(days=1)))


def update_env_date(env_id, date_zh_or_iso):
    """Update the environment's last_date after each simulated day."""
    st = env_state(env_id)
    st["last_date"] = "-" in str(date_zh_or_iso) and str(date_zh_or_iso) or zh_to_iso(date_zh_or_iso)
    _write_env_state(env_id, st)


def env_house_dir(env_id, date_iso, postcode, house_id):
    """House data directory: simulation/<env>/<date>/<postcode>/<house_id>/"""
    return os.path.join(_env_dir(env_id), date_iso, postcode, house_id)


def sim_root(world_id):
    """For analysis tools: return the root directory of the latest simulation environment
    for this world.

    Falls back to simulation/<world_id> when no environment exists (path does not exist;
    callers treat it as "no data" without raising).
    """
    env_id = latest_env(world_id)
    if env_id is None:
        return os.path.join(SIMULATION_DIR, world_id)
    return _env_dir(env_id)
