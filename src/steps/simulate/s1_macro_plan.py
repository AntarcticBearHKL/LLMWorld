"""Simulate step 1: macro activity plan for ONE member.

Standalone:  python -m steps.simulate.s1_macro_plan --world W --member <name|idx> [--date D] [--env E]
Or imported: run_step(world_id, member, date=None, env=None)

Reads the household (world step 3/4 output), builds the member's plan prompt,
prints full INPUT/OUTPUT, reports errors, and saves the raw timeline to
simulation/<env>/<date>/house_0001/s1_macro_<member>.json
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
from engine.environment import Time
from simulate import create_home_from_household
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PLAN_SCHEMA = {
    "type": "object",
    "required": ["member", "activities"],
    "properties": {
        "member": {"type": "string"},
        "activities": {
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
        },
    },
}


def load_home(world_id):
    path = os.path.join(PROJECT_ROOT, "worlds", world_id, "3168", "house_0001", "household.json")
    if not os.path.exists(path):
        alt = os.path.join(PROJECT_ROOT, "worlds", world_id, "household.json")
        if not os.path.exists(alt):
            print(f"[Error] household.json not found (checked {path} and {alt})")
            return None
        path = alt
    with open(path, encoding="utf-8") as f:
        household = json.load(f)
    return create_home_from_household(household)


def resolve_member(home, member_arg):
    members = list(home.members.values()) if isinstance(home.members, dict) else home.members
    if isinstance(member_arg, int) or (isinstance(member_arg, str) and member_arg.isdigit()):
        idx = int(member_arg)
        if 0 <= idx < len(members):
            return members[idx]
        print(f"[Error] member index {idx} out of range (0-{len(members)-1})")
        return None
    for m in members:
        if m.name == member_arg:
            return m
    print(f"[Error] member '{member_arg}' not found in {[m.name for m in members]}")
    return None


def run_step(world_id, member_arg, date=None, env=None):
    home = load_home(world_id)
    if home is None:
        return False, "household missing"
    member = resolve_member(home, member_arg)
    if member is None:
        return False, f"member {member_arg} not found"

    date = date or config.DEFAULT_START_DATE
    env = env or world_id
    t = Time(date)
    time_context = t.get_prompt_string()

    home_structure = json.dumps(home.get_home_structure(), ensure_ascii=False, indent=2)
    members_info = json.dumps(home.get_members_info(), ensure_ascii=False, indent=2)

    prompt = Prompt().load("simulate_step1_macro_plan",
                           member_name=member.name, member_age=member.age,
                           member_occupation=member.occupation, member_personality=member.personality,
                           time_context=time_context,
                           home_structure=home_structure, members_info=members_info,
                           memory_context="", world_news="", community_notice="")

    print("================ INPUT: PROMPT ================")
    print(prompt)
    print("================ INPUT: JSON SCHEMA ================")
    print(json.dumps(PLAN_SCHEMA, ensure_ascii=False, indent=2))

    resp = SubAgent.single_call(prompt, json_mode=True, json_schema=PLAN_SCHEMA)

    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])

    log_dir = os.path.join(PROJECT_ROOT, "simulation", env, date, "house_0001", "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    logger.record("s1_macro_plan", prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=f"{member.name}_")

    try:
        data = utils.parse_json_response(resp["content"])
    except Exception as e:
        print(f"[Parse error] strict JSON parse failed: {e}")
        data = gw._parse_json_lenient(resp["content"])
        print("[Parse] lenient parse succeeded")

    activities = data.get("activities") if isinstance(data, dict) else None
    if not isinstance(activities, list) or not activities:
        print("[Error] no activities list in response")
        return False, "no activities"

    print(f"[Check] {len(activities)} activity segments")
    for a in activities[:5]:
        print(f"  {a.get('time')} | {a.get('location')} | {str(a.get('activity'))[:60]}")

    out_dir = os.path.join(PROJECT_ROOT, "simulation", env, date, "house_0001")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"s1_macro_{member.name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
    return True, data


def main():
    parser = argparse.ArgumentParser(description="Simulate step 1: macro plan (one member)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--member", required=True, help="member name or index")
    parser.add_argument("--date", default=None, help="start date (default config)")
    parser.add_argument("--env", default=None, help="simulation env id (default: world id)")
    args = parser.parse_args()
    ok, result = run_step(args.world, args.member, args.date, args.env)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
