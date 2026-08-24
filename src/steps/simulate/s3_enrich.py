"""Simulate step 3: enrich ONE member's activities with concrete behaviors.

Standalone:  python -m steps.simulate.s3_enrich --world W --member <name|idx> [--date D] [--env E]
Or imported: run_step(world_id, member, date=None, env=None)

Reads this member's s2_coord_<member>.json and the other members' s2 outputs,
prints full INPUT/OUTPUT, reports errors, and saves s3_enrich_<member>.json.
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

ENRICH_SCHEMA = {
    "type": "object",
    "required": ["member", "enriched_activities"],
    "properties": {
        "member": {"type": "string"},
        "enriched_activities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["time", "location", "activity", "desc"],
                "properties": {
                    "time": {"type": "string"},
                    "location": {"type": "string"},
                    "activity": {"type": "string"},
                    "desc": {"type": "string", "minLength": 50},
                },
            },
        },
    },
}


def load_timeline(world_id, member_name, date, env, prefix):
    path = os.path.join(PROJECT_ROOT, "simulation", env, date, "house_0001",
                        f"{prefix}_{member_name}.json")
    if not os.path.exists(path):
        print(f"[Error] {path} not found; run the previous step first")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def timeline_activities(data, key):
    return data.get(key, []) if isinstance(data, dict) else []


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

    own = load_timeline(world_id, member.name, date, env, "s2_coord")
    if own is None:
        return False, "member s2 output missing"
    own_activities = timeline_activities(own, "coordinated_activities")

    others = {}
    for other_name in [m.name for m in members if m.name != member.name]:
        other = load_timeline(world_id, other_name, date, env, "s2_coord")
        if other is not None:
            others[other_name] = timeline_activities(other, "coordinated_activities")

    home_structure = json.dumps(home.get_home_structure(), ensure_ascii=False, indent=2)
    prompt = Prompt().load("simulate_step3_enrich_activities",
                           member_name=member.name, member_age=member.age,
                           member_occupation=member.occupation, member_personality=member.personality,
                           member_timeline=json.dumps(own_activities, ensure_ascii=False, indent=2),
                           other_members_timelines=json.dumps(others, ensure_ascii=False, indent=2),
                           home_structure=home_structure,
                           season=config.DEFAULT_SEASON, weather=config.DEFAULT_WEATHER,
                           temperature=config.DEFAULT_TEMPERATURE)

    print("================ INPUT: PROMPT ================")
    print(prompt)
    print("================ INPUT: JSON SCHEMA ================")
    print(json.dumps(ENRICH_SCHEMA, ensure_ascii=False, indent=2))

    resp = SubAgent.single_call(prompt, json_mode=True, json_schema=ENRICH_SCHEMA)

    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])

    log_dir = os.path.join(PROJECT_ROOT, "simulation", env, date, "house_0001", "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    logger.record("s3_enrich", prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=f"{member.name}_")

    try:
        data = utils.parse_json_response(resp["content"])
    except Exception as e:
        print(f"[Parse error] strict JSON parse failed: {e}")
        data = gw._parse_json_lenient(resp["content"])
        print("[Parse] lenient parse succeeded")

    enriched = data.get("enriched_activities") if isinstance(data, dict) else None
    if not isinstance(enriched, list) or not enriched:
        print("[Error] no enriched_activities list in response")
        return False, "no enriched_activities"

    print(f"[Check] {len(enriched)} enriched segments")
    for a in enriched[:5]:
        print(f"  {a.get('time')} | {a.get('location')} | {str(a.get('activity'))[:50]} | desc {len(str(a.get('desc', '')))} chars")

    out_dir = os.path.join(PROJECT_ROOT, "simulation", env, date, "house_0001")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"s3_enrich_{member.name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
    return True, data


def main():
    parser = argparse.ArgumentParser(description="Simulate step 3: enrich behaviors (one member)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--member", required=True, help="member name or index")
    parser.add_argument("--date", default=None)
    parser.add_argument("--env", default=None)
    args = parser.parse_args()
    ok, result = run_step(args.world, args.member, args.date, args.env)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
