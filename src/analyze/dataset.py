"""Unified reader for the current simulation output layout.

Simulation files (written by run.py --mode simulate):
    output/simulation/<env>/<date>/<house>/s1_macro_<Member>.json
    output/simulation/<env>/<date>/<house>/s2_coord_<Member>.json
    output/simulation/<env>/<date>/<house>/s3_enrich_<Member>.json
    output/simulation/<env>/<date>/<house>/s4_decisions_<Member>.json
    output/simulation/<env>/<date>/<house>/s4_decisions_<Member>_<tag>.json
World files:
    output/worlds/<world_id>/3168/<house>/household.json
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(_HERE)
for _path in (_HERE, _SRC):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from load_model import build_load_profile

PROJECT_ROOT = os.path.dirname(_SRC)
SIMULATION_DIR = os.path.join(PROJECT_ROOT, "output", "simulation")
WORLDS_DIR = os.path.join(PROJECT_ROOT, "output", "worlds")

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_RECORD_CACHE = {}


def sim_root(world_id):
    """Output directory for analysis results of a world."""
    return os.path.join(SIMULATION_DIR, world_id)


def list_dates(world_id, env=None):
    base = os.path.join(SIMULATION_DIR, env or world_id)
    if not os.path.isdir(base):
        return []
    return sorted(name for name in os.listdir(base)
                  if _DATE_RE.match(name) and os.path.isdir(os.path.join(base, name)))


def list_houses(world_id, env, date):
    base = os.path.join(SIMULATION_DIR, env or world_id, date)
    if not os.path.isdir(base):
        return []
    houses = []
    for name in sorted(os.listdir(base)):
        house_dir = os.path.join(base, name)
        if os.path.isdir(house_dir) and _s4_decision_files(house_dir):
            houses.append(name)
    return houses


def household_path(world_id, house_id):
    primary = os.path.join(WORLDS_DIR, world_id, "3168", house_id, "household.json")
    if os.path.isfile(primary):
        return primary
    fallback = os.path.join(WORLDS_DIR, world_id, "household.json")
    if os.path.isfile(fallback):
        return fallback
    return primary


def read_household(world_id, house_id):
    return _load_json(household_path(world_id, house_id))


def read_member_names(world_id, house_id):
    return _household_member_names(read_household(world_id, house_id))


def discover_policy_tags(house_dir):
    members = _member_names_from_dir(house_dir)
    tags = set()
    for name in _s4_decision_files(house_dir):
        stem = name[len("s4_decisions_"):-len(".json")]
        for member in members:
            if stem == member:
                break
            if stem.startswith(member + "_"):
                tags.add(stem[len(member) + 1:])
                break
    return sorted(tags)


def read_activities(house_dir, member):
    data = _load_json(os.path.join(house_dir, "s3_enrich_%s.json" % member))
    if not isinstance(data, dict):
        return []
    return data.get("enriched_activities", []) or []


def read_timeline(house_dir, member):
    data = _load_json(os.path.join(house_dir, "s2_coord_%s.json" % member))
    if not isinstance(data, dict):
        return []
    return data.get("coordinated_activities", []) or []


def read_decisions(house_dir, member, tag=None):
    suffix = "_%s" % tag if tag and tag != "baseline" else ""
    data = _load_json(os.path.join(house_dir, "s4_decisions_%s%s.json" % (member, suffix)))
    if not isinstance(data, dict):
        return []
    return data.get("appliance_decisions", []) or []


def iter_house_days(world_id, env=None, date=None, policy=None, houses=None):
    """Yield one record per (house, date) that has decisions for the requested policy.

    policy=None or "baseline" reads the baseline file; any other value is a policy tag.
    Records are cached per (world, env, date, house, policy) for the process lifetime.
    """
    env = env or world_id
    tag = None if policy in (None, "baseline") else policy
    dates = [date] if date else list_dates(world_id, env)
    for day in dates:
        house_ids = houses if houses is not None else list_houses(world_id, env, day)
        for house_id in house_ids:
            house_dir = os.path.join(SIMULATION_DIR, env, day, house_id)
            if not os.path.isdir(house_dir):
                print("[Warn] house dir missing: %s" % house_dir)
                continue
            cache_key = (world_id, env, day, house_id, tag or "baseline")
            record = _RECORD_CACHE.get(cache_key)
            if record is None:
                record = _build_house_day(world_id, env, day, house_id, house_dir, tag)
                if record is None:
                    continue
                _RECORD_CACHE[cache_key] = record
            yield record


def population_profile(world_id, policy, date, env=None):
    """Aggregate all house load profiles for one (date, policy)."""
    env = env or world_id
    tag = None if policy in (None, "baseline") else policy
    profile = [0.0] * 1440
    per_house = []
    for record in iter_house_days(world_id, env=env, date=date, policy=policy):
        house_profile = record["load_profile_watts"]
        for minute in range(1440):
            profile[minute] += house_profile[minute]
        per_house.append({
            "house_id": record["house_id"],
            "total_energy_kwh": record["total_energy_kwh"],
        })
    return {
        "world_id": world_id,
        "env": env,
        "date": date,
        "policy": tag or "baseline",
        "load_profile_watts": profile,
        "total_energy_kwh": sum(profile) / 60.0 / 1000.0,
        "per_house": per_house,
    }


def household_features(household):
    members = household.get("members", []) if isinstance(household, dict) else []
    first = members[0] if members and isinstance(members[0], dict) else {}
    personality = first.get("personality", {}) or {}
    if not isinstance(personality, dict):
        personality = {}
    return {
        "household_type": household.get("type", "?") if isinstance(household, dict) else "?",
        "members_count": len(members),
        "energy_awareness": personality.get("energy_awareness", "?"),
        "big_five": personality.get("big_five", {}),
        "age": first.get("age", 0),
    }


def _build_house_day(world_id, env, date, house_id, house_dir, tag):
    household = read_household(world_id, house_id)
    if not isinstance(household, dict):
        print("[Warn] household missing for %s/%s" % (world_id, house_id))
        return None

    decisions = {}
    activities = {}
    for member in _household_member_names(household):
        segments = read_decisions(house_dir, member, tag)
        if not segments:
            continue
        decisions[member] = segments
        activities[member] = read_activities(house_dir, member)

    if not decisions:
        print("[Warn] no decisions for %s/%s/%s/%s (policy=%s)"
              % (world_id, env, date, house_id, tag or "baseline"))
        return None

    profile, per_appliance_kwh, total_kwh = build_load_profile(household, decisions)
    return {
        "world_id": world_id,
        "env": env,
        "date": date,
        "house_id": house_id,
        "house_dir": house_dir,
        "household": household,
        "members": list(decisions.keys()),
        "policy": tag or "baseline",
        "decisions": decisions,
        "activities": activities,
        "load_profile_watts": profile,
        "total_energy_kwh": total_kwh,
        "per_appliance_kwh": per_appliance_kwh,
    }


def _load_json(path):
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print("[Warn] failed to read %s: %s" % (path, exc))
        return None


def _s4_decision_files(house_dir):
    try:
        names = os.listdir(house_dir)
    except OSError:
        return []
    files = []
    for name in sorted(names):
        if not name.startswith("s4_decisions_") or not name.endswith(".json"):
            continue
        if name.startswith("s4_decisions_raw_"):
            continue
        files.append(name)
    return files


def _member_names_from_dir(house_dir):
    try:
        names = os.listdir(house_dir)
    except OSError:
        names = []
    members = [name[len("s3_enrich_"):-len(".json")] for name in sorted(names)
               if name.startswith("s3_enrich_") and name.endswith(".json")]
    if members:
        return members
    for name in _s4_decision_files(house_dir):
        stem = name[len("s4_decisions_"):-len(".json")]
        if "_" not in stem and stem not in members:
            members.append(stem)
    return members


def _household_member_names(household):
    if not isinstance(household, dict):
        return []
    return [member.get("name") for member in household.get("members", [])
            if isinstance(member, dict) and member.get("name")]
