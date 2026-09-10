import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
from engine import SubAgent, utils, weather
from engine.json_parse import parse as parse_llm_json
from engine.prompt import Prompt
from steps.simulate.s1_macro_plan import load_home, resolve_member
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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


def load_timeline(world_id, member_name, date, env, prefix, house):
    path = os.path.join(gw.SIMULATION_DIR, env, date, house,
                        f"{prefix}_{member_name}.json")
    if not os.path.exists(path):
        print(f"[Error] {path} not found; run the previous step first")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def timeline_activities(data, key):
    return data.get(key, []) if isinstance(data, dict) else []


def run_step(world_id, member_arg, date=None, env=None, house="house_0001"):
    home = load_home(world_id, house)
    if home is None:
        return False, "household missing"
    member = resolve_member(home, member_arg)
    if member is None:
        return False, f"member {member_arg} not found"

    date = date or config.DEFAULT_START_DATE
    env = env or world_id
    members = list(home.members.values()) if isinstance(home.members, dict) else home.members

    own = load_timeline(world_id, member.name, date, env, "s2_coord", house)
    if own is None:
        return False, "member s2 output missing"
    own_activities = timeline_activities(own, "coordinated_activities")

    others = {}
    for other_name in [m.name for m in members if m.name != member.name]:
        other = load_timeline(world_id, other_name, date, env, "s2_coord", house)
        if other is not None:
            others[other_name] = timeline_activities(other, "coordinated_activities")

    home_structure = json.dumps(home.get_home_structure(), ensure_ascii=False, indent=2)
    w = weather.get_weather(date)
    base_prompt = Prompt().load("simulate_step3_enrich_activities",
                           member_name=member.name, member_age=member.age,
                           member_occupation=member.occupation, member_personality=member.personality,
                           member_timeline=json.dumps(own_activities, ensure_ascii=False, indent=2),
                           other_members_timelines=json.dumps(others, ensure_ascii=False, indent=2),
                           home_structure=home_structure,
                           season=w["season"], weather=w["weather"],
                           temperature=w["temperature"])

    log_dir = os.path.join(gw.SIMULATION_DIR, env, date, house, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    print("================ INPUT: PROMPT ================")
    print(base_prompt)
    print("================ INPUT: JSON SCHEMA ================")
    print(json.dumps(ENRICH_SCHEMA, ensure_ascii=False, indent=2))
    resp = SubAgent.single_call(base_prompt, json_mode=True, json_schema=ENRICH_SCHEMA)
    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])
    try:
        data = parse_llm_json(resp["content"])
    except Exception as exc:
        logger.record("s3_enrich", base_prompt, resp["content"], reasoning="",
                      ok=False, error=f"JSON parse failed: {exc}", attempt=1, prefix=f"{member.name}_")
        return False, {"stage": "s3_enrich", "issues": [f"JSON parsing failed: {exc}"]}
    enriched = data.get("enriched_activities", []) if isinstance(data, dict) else []
    logger.record("s3_enrich", base_prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=f"{member.name}_")

    print(f"[Check] {len(enriched)} enriched segments")
    for a in enriched[:5]:
        print(f"  {a.get('time')} | {a.get('location')} | {str(a.get('activity'))[:50]} | desc {len(str(a.get('desc', '')))} chars")

    out_dir = os.path.join(gw.SIMULATION_DIR, env, date, house)
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
    parser.add_argument("--house", default="house_0001", help="house id (default: house_0001)")
    args = parser.parse_args()
    ok, result = run_step(args.world, args.member, args.date, args.env, args.house)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
