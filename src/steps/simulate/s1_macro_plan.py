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
from engine.json_parse import parse as parse_llm_json
from engine.prompt import Prompt
from engine.environment import Time
from simulate import create_home_from_household
from steps.simulate import day_state
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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


def load_home(world_id, house="house_0001"):
    path = os.path.join(gw.WORLDS_DIR, world_id, "3168", house, "household.json")
    if not os.path.exists(path):
        alt = os.path.join(gw.WORLDS_DIR, world_id, "household.json")
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


def run_step(world_id, member_arg, date=None, env=None, house="house_0001", prev_state=None):
    home = load_home(world_id, house)
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
    carry_over_context = day_state.carry_over_text(prev_state, member.name)

    base_prompt = Prompt().load("simulate_step1_macro_plan",
                           member_name=member.name, member_age=member.age,
                           member_occupation=member.occupation, member_personality=member.personality,
                           member_work_schedule=json.dumps(member.work_schedule, ensure_ascii=False),
                           member_habits=json.dumps(member.habits, ensure_ascii=False),
                           member_health=json.dumps(member.health, ensure_ascii=False),
                           member_bedroom=member.bedroom,
                           time_context=time_context,
                           home_structure=home_structure, members_info=members_info,
                           memory_context="", world_news="", community_notice="",
                           carry_over_context=carry_over_context)

    log_dir = os.path.join(gw.SIMULATION_DIR, env, date, house, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    print("================ INPUT: PROMPT ================")
    print(base_prompt)
    print("================ INPUT: JSON SCHEMA ================")
    print(json.dumps(PLAN_SCHEMA, ensure_ascii=False, indent=2))
    resp = SubAgent.single_call(base_prompt, json_mode=True, json_schema=PLAN_SCHEMA)
    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])
    try:
        data = parse_llm_json(resp["content"])
    except Exception as exc:
        logger.record("s1_macro_plan", base_prompt, resp["content"], reasoning="",
                      ok=False, error=f"JSON parse failed: {exc}", attempt=1, prefix=f"{member.name}_")
        return False, {"stage": "s1_macro_plan", "issues": [f"JSON parsing failed: {exc}"]}
    activities = data.get("activities") if isinstance(data, dict) else []
    logger.record("s1_macro_plan", base_prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=f"{member.name}_")

    if isinstance(data, dict):
        repair_log = []
        data["activities"] = utils.normalize_activity_times(
            data.get("activities", []), repair_log=repair_log)
        activities = data["activities"]
        for note in repair_log:
            print(f"[TimeRepair] {note}")
        print(f"[TimeRepair] repaired {len(repair_log)} timestamps")

    if isinstance(data, dict):
        reconciled = day_state.reconcile_boundary(activities, prev_state)
        if reconciled is not activities:
            print(f"[Continuity] day boundary rewritten for {member.name}: starts "
                  f"{reconciled[0].get('time')} @ {reconciled[0].get('location')}")
            data["activities"] = reconciled
            activities = reconciled

    print(f"[Check] {len(activities)} activity segments")
    for a in activities[:5]:
        print(f"  {a.get('time')} | {a.get('location')} | {str(a.get('activity'))[:60]}")

    out_dir = os.path.join(gw.SIMULATION_DIR, env, date, house)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"s1_macro_{member.name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
    day_state.save_day_state(out_dir, member.name, day_state.end_state(activities))
    return True, data


def main():
    parser = argparse.ArgumentParser(description="Simulate step 1: macro plan (one member)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--member", required=True, help="member name or index")
    parser.add_argument("--date", default=None, help="start date (default config)")
    parser.add_argument("--env", default=None, help="simulation env id (default: world id)")
    parser.add_argument("--house", default="house_0001", help="house id (default: house_0001)")
    args = parser.parse_args()
    ok, result = run_step(args.world, args.member, args.date, args.env, args.house)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
