"""Simulate step 2: coordinate ONE member's timeline with already-coordinated members.

Standalone:  python -m steps.simulate.s2_coordinate --world W --member <name|idx> [--date D] [--env E]
Or imported: run_step(world_id, member, date=None, env=None)

Reads this member's s1_macro_<member>.json and the s1 outputs of the other
members (treated as already-coordinated), prints full INPUT/OUTPUT, reports
errors, and saves s2_coord_<member>.json.
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
from engine import SubAgent, utils
from engine.prompt import Prompt
from steps.simulate.s1_macro_plan import load_home, resolve_member
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

COORD_SCHEMA = {
    "type": "object",
    "required": ["coordinated_activities"],
    "properties": {
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
    path = os.path.join(PROJECT_ROOT, "simulation", env, date, "house_0001",
                        f"s1_macro_{member_name}.json")
    if not os.path.exists(path):
        print(f"[Error] {path} not found; run s1 for this member first")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def format_timeline(data):
    lines = []
    for a in data.get("activities", []):
        lines.append(f"  {a.get('time')}: {a.get('location')} - {a.get('activity')}")
    return "\n".join(lines)


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

    coordinated_members = [m.name for m in members if m.name != member.name]
    coord_texts = []
    for other_name in coordinated_members:
        other = load_member_plan(world_id, other_name, date, env)
        if other is not None:
            coord_texts.append(f"{other_name}:\n" + format_timeline(other))
    if not coord_texts:
        print("[Info] no other member plans found; coordination will be trivial")

    prompt = Prompt().load("simulate_step2_progressive_coordination",
                           current_member_name=member.name,
                           current_member_age=member.age,
                           current_member_occupation=member.occupation,
                           current_member_personality=member.personality,
                           coordinated_members=", ".join(coordinated_members),
                           coordinated_timelines="\n".join(coord_texts),
                           current_timeline=f"\n{member.name}'s original timeline:\n" + format_timeline(current))

    print("================ INPUT: PROMPT ================")
    print(prompt)
    print("================ INPUT: JSON SCHEMA ================")
    print(json.dumps(COORD_SCHEMA, ensure_ascii=False, indent=2))

    resp = SubAgent.single_call(prompt, json_mode=True, json_schema=COORD_SCHEMA)

    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])

    log_dir = os.path.join(PROJECT_ROOT, "simulation", env, date, "house_0001", "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    logger.record("s2_coordinate", prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=f"{member.name}_")

    try:
        data = utils.parse_json_response(resp["content"])
    except Exception as e:
        print(f"[Parse error] strict JSON parse failed: {e}")
        data = gw._parse_json_lenient(resp["content"])
        print("[Parse] lenient parse succeeded")

    activities = data.get("coordinated_activities") if isinstance(data, dict) else None
    if not isinstance(activities, list) or not activities:
        print("[Error] no coordinated_activities list in response")
        return False, "no coordinated_activities"

    print(f"[Check] {len(activities)} coordinated segments")
    for a in activities[:5]:
        print(f"  {a.get('time')} | {a.get('location')} | {str(a.get('activity'))[:60]}")

    out_dir = os.path.join(PROJECT_ROOT, "simulation", env, date, "house_0001")
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
