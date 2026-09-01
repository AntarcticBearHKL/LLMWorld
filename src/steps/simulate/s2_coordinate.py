import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
from engine import SubAgent, utils
from engine.prompt import Prompt
from steps.simulate.s1_macro_plan import load_home, resolve_member
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

COORD_SCHEMA = {
    "type": "object",
    "required": ["member", "coordinated_activities"],
    "properties": {
        "member": {"type": "string"},
        "coordinated_activities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["time", "location", "activity"],
                "properties": {
                    "time": {"type": "string"},
                    "location": {"type": "string"},
                    "activity": {"type": "string"},
                },
            },
        }
    },
}


def load_member_plan(world_id, member_name, date, env):
    path = os.path.join(gw.SIMULATION_DIR, env, date, "house_0001",
                        f"s1_macro_{member_name}.json")
    if not os.path.exists(path):
        print(f"[Error] {path} not found; run s1 for this member first")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def format_timeline(data):
    lines = []
    for a in _timeline_items(data):
        lines.append(f"  {a.get('time')}: {a.get('location')} - {a.get('activity')}")
    return "\n".join(lines)


def _timeline_items(data):
    if not isinstance(data, dict):
        return []
    return data.get("coordinated_activities", data.get("activities", []))


def load_best_member_plan(world_id, member_name, date, env):
    base = os.path.join(gw.SIMULATION_DIR, env, date, "house_0001")
    coordinated = os.path.join(base, f"s2_coord_{member_name}.json")
    if os.path.exists(coordinated):
        with open(coordinated, encoding="utf-8") as source:
            return json.load(source)
    return load_member_plan(world_id, member_name, date, env)


def run_step(world_id, member_arg, date=None, env=None):
    home = load_home(world_id)
    if home is None:
        return False, "household missing"
    member = resolve_member(home, member_arg)
    if member is None:
        return False, f"member {member_arg} not found"

    date = date or config.DEFAULT_START_DATE
    env = env or world_id
    members = list(home.members.values()) if isinstance(home.members, dict) else home.members

    current = load_member_plan(world_id, member.name, date, env)
    if current is None:
        return False, "member s1 plan missing"

    locked_members = []
    locked_texts = []
    provisional_members = []
    provisional_texts = []
    for other_member in members:
        other_name = other_member.name
        if other_name == member.name:
            continue
        base = os.path.join(gw.SIMULATION_DIR, env, date, "house_0001")
        coordinated_path = os.path.join(base, f"s2_coord_{other_name}.json")
        other = load_best_member_plan(world_id, other_name, date, env)
        if other is not None:
            rendered = f"{other_name}:\n" + format_timeline(other)
            if os.path.exists(coordinated_path):
                locked_members.append(other_name)
                locked_texts.append(rendered)
            else:
                provisional_members.append(other_name)
                provisional_texts.append(rendered)
    if not locked_texts and not provisional_texts:
        print("[Info] no other member plans found; coordination will be trivial")

    base_prompt = Prompt().load("simulate_step2_progressive_coordination",
                           current_member_name=member.name,
                           current_member_age=member.age,
                           current_member_occupation=member.occupation,
                           current_member_personality=member.personality,
                           locked_members=", ".join(locked_members) or "None",
                           locked_timelines="\n".join(locked_texts) or "None",
                           provisional_members=", ".join(provisional_members) or "None",
                           provisional_timelines="\n".join(provisional_texts) or "None",
                           current_timeline=f"\n{member.name}'s original timeline:\n" + format_timeline(current),
                           room_names=json.dumps(list(home.rooms), ensure_ascii=False),
                           assigned_bedroom=member.bedroom,
                           exclusive_resources=json.dumps(home.get_exclusive_resources(), ensure_ascii=False, indent=2))
    log_dir = os.path.join(gw.SIMULATION_DIR, env, date, "house_0001", "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    print("================ INPUT: PROMPT ================")
    print(base_prompt)
    print("================ INPUT: JSON SCHEMA ================")
    print(json.dumps(COORD_SCHEMA, ensure_ascii=False, indent=2))
    resp = SubAgent.single_call(base_prompt, json_mode=True, json_schema=COORD_SCHEMA)
    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])
    try:
        data = utils.parse_json_response(resp["content"])
    except Exception as exc:
        logger.record("s2_coordinate", base_prompt, resp["content"], reasoning="",
                      ok=False, error=f"JSON parse failed: {exc}", attempt=1, prefix=f"{member.name}_")
        return False, {"stage": "s2_coordinate", "issues": [f"JSON parsing failed: {exc}"]}
    activities = data.get("coordinated_activities", []) if isinstance(data, dict) else []
    logger.record("s2_coordinate", base_prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=f"{member.name}_")

    print(f"[Check] {len(activities)} coordinated segments")
    for a in activities[:5]:
        print(f"  {a.get('time')} | {a.get('location')} | {str(a.get('activity'))[:60]}")

    out_dir = os.path.join(gw.SIMULATION_DIR, env, date, "house_0001")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"s2_coord_{member.name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
    return True, data


def main():
    parser = argparse.ArgumentParser(description="Simulate step 2: coordinate (one member)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--member", required=True, help="member name or index")
    parser.add_argument("--date", default=None)
    parser.add_argument("--env", default=None)
    args = parser.parse_args()
    ok, result = run_step(args.world, args.member, args.date, args.env)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
