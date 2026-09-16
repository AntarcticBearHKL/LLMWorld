"""World step: generate the home (rooms and appliances) for a composed household.

With the district description and the household (type + members) already known,
``generate_world_home.md`` is asked for the physical home only: a name, type,
size and the rooms, each listing the appliances that physically sit in it. The
strict JSON schema reuses ``s3_household_build.HOUSEHOLD_SCHEMA``'s ``home``
definition, so the two can never drift, and the appliance type tokens come from
the shared appliance registry.

The generated ``home`` is merged into the existing
``<district>/house_XXXX/household.json`` (``type``, ``members`` and
``llm_generated`` are preserved) after backing the previous file up to
``household.json.bak.<timestamp>``. The household meta is refreshed so
``rooms_count`` matches the new home.

Additive: the s1-s4 world steps and ``run.py`` are untouched; a later task
switches the pipeline over.

Run:
  .venv\\Scripts\\python.exe src\\steps\\world\\s3_home.py --world <id>
  .venv\\Scripts\\python.exe src\\steps\\world\\s3_home.py --world <id> --house house_0001
  .venv\\Scripts\\python.exe src\\steps\\world\\s3_home.py --world <id> --all
"""

import argparse
import copy
import json
import os
import re
import shutil
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from engine import SubAgent
from engine.json_parse import parse as parse_llm_json
from engine.subagent import LLMCallError
from engine.prompt import Prompt
from appliances import get_supported_appliances_text, get_appliance_schemas_text
from appliances.catalog import backfill_power
from steps.world.s3_household_build import HOUSEHOLD_SCHEMA
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

BACKUP_SUFFIX = ".bak."
HOME_STAGE = "home"

_HOUSE_ID_RE = re.compile(r"^house_(\d{4})$")


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError):
        return None


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def _stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _backup_file(path):
    """Copy *path* to ``<path>.bak.<timestamp>``; same shape as the dashboard copy."""
    backup = "%s%s%s" % (path, BACKUP_SUFFIX, _stamp())
    bump = 0
    while os.path.exists(backup):
        bump += 1
        backup = "%s%s%s_%d" % (path, BACKUP_SUFFIX, _stamp(), bump)
    shutil.copy2(path, backup)
    return backup


def _home_schema(member_count):
    home = copy.deepcopy(HOUSEHOLD_SCHEMA["properties"]["home"])
    home["properties"]["rooms"]["minItems"] = max(1, member_count + 2)
    return {"type": "object", "required": ["home"], "properties": {"home": home}}


def _district_description(world_id, district):
    data = _read_json(os.path.join(gw.district_dir(world_id, district), "district.json"))
    if isinstance(data, dict):
        description = data.get("description")
        if isinstance(description, str):
            return description.strip()
    return ""


def _house_ids(district_path):
    try:
        children = os.listdir(district_path)
    except OSError:
        return []
    return sorted(name for name in children if _HOUSE_ID_RE.match(name))


def _resolve_house_id(district_path, house):
    """Resolve the house selector to a ``house_XXXX`` id.

    ``None`` selects the most recently added household in the district (the
    highest existing ``house_XXXX``); an int is a 0-based index and a
    ``house_XXXX`` string selects that household.
    """
    house_ids = _house_ids(district_path)
    if house is None:
        return house_ids[-1] if house_ids else "house_0001"
    if isinstance(house, bool):
        raise ValueError("invalid house selector %r" % (house,))
    if isinstance(house, int):
        if house < 0:
            raise ValueError("house index must be >= 0; got %d" % house)
        return "house_%04d" % (house + 1)
    token = str(house).strip()
    if not token:
        return house_ids[-1] if house_ids else "house_0001"
    if token.isdigit():
        return "house_%04d" % (int(token) + 1)
    if _HOUSE_ID_RE.match(token):
        return token
    raise ValueError("invalid house selector %r; use an index or house_XXXX" % (house,))


def _members_summary(members):
    lines = []
    for member in members:
        if not isinstance(member, dict):
            continue
        lines.append("- %s | age %s | gender %s | bedroom %s" % (
            member.get("name", "?"), member.get("age", "?"),
            member.get("gender", "?"), member.get("bedroom", "?")))
    return "\n".join(lines) if lines else "(no members)"


def _home_problem(data):
    """Return an error string when the response is not a usable home, else None."""
    if not isinstance(data, dict) or not isinstance(data.get("home"), dict):
        return "home object missing"
    home = data["home"]
    if not isinstance(home.get("name"), str) or not home["name"].strip():
        return "home name missing"
    rooms = home.get("rooms")
    if not isinstance(rooms, list) or not rooms:
        return "home has no rooms"
    for room in rooms:
        if not isinstance(room, dict):
            return "a room entry is not an object"
        if not isinstance(room.get("name"), str) or not room["name"].strip():
            return "a room is missing its name"
        appliances = room.get("appliances")
        if appliances is not None and not isinstance(appliances, list):
            return "a room's appliances must be a list"
    return None


def _backfill_home_power(home):
    """Normalise each room's appliances and guarantee a numeric power value."""
    filled = 0
    for room in home.get("rooms", []):
        if not isinstance(room, dict):
            continue
        appliances = room.get("appliances")
        if not isinstance(appliances, list):
            continue
        normalized = []
        for config in appliances:
            if isinstance(config, str):
                config = {"type": config.strip()} if config.strip() else None
            if not isinstance(config, dict) or not config.get("type"):
                continue
            normalized.append(backfill_power(config, location=room.get("name")))
            filled += 1
        room["appliances"] = normalized
    return filled


def _upsert_household_meta(world_id, house_meta, district):
    """Replace any existing entry for this house, then register the fresh one."""
    path = os.path.join(gw.district_dir(world_id, district), "households.json")
    data = _read_json(path)
    if not isinstance(data, dict):
        data = {}
    entries = data.get("households")
    if not isinstance(entries, list):
        entries = []
    house_id = str(house_meta.get("house_id"))
    data["households"] = [
        entry for entry in entries
        if not (isinstance(entry, dict) and str(entry.get("house_id")) == house_id)
    ]
    _write_json(path, data)
    return gw.update_world_meta(world_id, house_meta, district)


def run_step(world_id, district=None, house=None, *, seed=42) -> tuple[bool, str]:
    """Generate the home for one composed household and merge it in.

    ``house=None`` selects the district's most recently added household; an int
    (0-based) or a ``house_XXXX`` string selects one explicitly. Returns
    ``(True, house_dir)`` on success and ``(False, error)`` otherwise.
    """
    district = district or gw.primary_district(world_id)
    if not district:
        return False, "no districts in world %s" % world_id

    district_path = gw.district_dir(world_id, district)
    try:
        house_id = _resolve_house_id(district_path, house)
    except ValueError as exc:
        return False, str(exc)

    house_dir = os.path.join(district_path, house_id)
    household_path = os.path.join(house_dir, "household.json")
    household = _read_json(household_path)
    members = household.get("members") if isinstance(household, dict) else None
    if not isinstance(household, dict) or not isinstance(members, list) or not members:
        return False, "household.json missing; run the household step first"

    description = _district_description(world_id, district)
    log_dir = os.path.join(house_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    prefix = "%s_" % house_id

    prompt = Prompt().load(
        "generate_world_home",
        district_description=description,
        household_type=household.get("type", "?"),
        member_count=len(members),
        members_summary=_members_summary(members),
        supported_appliances=get_supported_appliances_text(),
        appliance_schemas=get_appliance_schemas_text(),
    )
    schema = _home_schema(len(members))

    print("================ HOME INPUT ================")
    print(prompt)
    try:
        resp = SubAgent.single_call(prompt, json_mode=True, json_schema=schema)
    except LLMCallError as exc:
        print("[Home failed] %s" % exc)
        logger.record(HOME_STAGE, prompt, "", reasoning="", ok=False,
                      error=str(exc), attempt=1, prefix=prefix, schema=schema)
        return False, str(exc)
    print("================ HOME OUTPUT ================")
    print(resp["content"])

    try:
        data = parse_llm_json(resp["content"])
    except Exception as exc:
        logger.record(HOME_STAGE, prompt, resp["content"], reasoning="", ok=False,
                      error="JSON parse failed: %s" % exc, attempt=1, prefix=prefix, schema=schema)
        return False, "home response is not valid JSON: %s" % exc

    problem = _home_problem(data)
    if problem is not None:
        logger.record(HOME_STAGE, prompt, resp["content"], reasoning="", ok=False,
                      error=problem, attempt=1, prefix=prefix, schema=schema)
        return False, problem

    home = data["home"]
    filled = _backfill_home_power(home)
    logger.record(HOME_STAGE, prompt, resp["content"], reasoning="", ok=True,
                  attempt=1, prefix=prefix, schema=schema, parsed=data)
    print("[Appliances] power backfilled for %d room configs" % filled)

    backup = _backup_file(household_path)
    print("[Backup] %s" % backup)

    merged = dict(household)
    merged["home"] = home
    merged["type"] = household.get("type", "?")
    merged["llm_generated"] = household.get("llm_generated", True)
    _write_json(household_path, merged)
    print("[Saved] %s" % household_path)

    house_meta = {
        "house_id": house_id,
        "type": merged["type"],
        "members_count": len(merged.get("members", [])),
        "rooms_count": len(home.get("rooms", [])),
        "llm_generated": merged["llm_generated"],
    }
    _upsert_household_meta(world_id, house_meta, district)

    print("[Overview] home=%s | rooms: %d | members: %d"
          % (home.get("name"), len(home.get("rooms", [])), len(merged.get("members", []))))
    for room in home.get("rooms", []):
        print("  room: %s appliances=%d" % (room.get("name"), len(room.get("appliances", []))))
    return True, house_dir


def main():
    parser = argparse.ArgumentParser(description="World step: generate the home (rooms + appliances) for a household")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--district", default=None, help="district name (default: world's primary district)")
    parser.add_argument("--house", default=None,
                        help="household index (0-based) or house_XXXX; default picks the newest household")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--all", action="store_true", help="generate a home for every district")
    args = parser.parse_args()

    if args.all:
        ok = True
        districts = gw.districts(args.world)
        if not districts:
            print("[Error] no districts in world %s" % args.world)
            sys.exit(1)
        for district in districts:
            step_ok, result = run_step(args.world, district, None, seed=args.seed)
            if step_ok:
                print(result)
            else:
                print("[Error] %s: %s" % (district, result))
            ok = ok and step_ok
        sys.exit(0 if ok else 1)

    ok, result = run_step(args.world, args.district, args.house, seed=args.seed)
    if ok:
        print(result)
    else:
        print("[Error] %s" % result)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
