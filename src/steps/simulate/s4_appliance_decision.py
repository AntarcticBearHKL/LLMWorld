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

DECISION_SCHEMA = {
    "type": "object",
    "required": ["member", "appliance_decisions"],
    "properties": {
        "member": {"type": "string"},
        "appliance_decisions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["time", "location", "activity", "operations"],
                "properties": {
                    "time": {"type": "string"},
                    "location": {"type": "string"},
                    "activity": {"type": "string"},
                    "operations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["unique_id", "action"],
                            "properties": {
                                "unique_id": {"type": "string"},
                                "action": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    },
}


def load_timeline(world_id, member_name, date, env):
    path = os.path.join(gw.SIMULATION_DIR, env, date, "house_0001",
                        f"s3_enrich_{member_name}.json")
    if not os.path.exists(path):
        print(f"[Error] {path} not found; run step s3 first")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_step(world_id, member_arg, date=None, env=None):
    home = load_home(world_id)
    if home is None:
        return False, "household missing"
    member = resolve_member(home, member_arg)
    if member is None:
        return False, f"member {member_arg} not found"

    date = date or config.DEFAULT_START_DATE
    env = env or world_id

    own = load_timeline(world_id, member.name, date, env)
    if own is None:
        return False, "member s3 output missing"
    activities = own.get("enriched_activities", []) if isinstance(own, dict) else []

    home_with_appl = json.dumps(home.get_home_structure_with_details(), ensure_ascii=False, indent=2)
    base_prompt = Prompt().load("simulate_step4_batch_appliance_decision",
                           member_name=member.name, member_age=member.age,
                           member_occupation=member.occupation, member_habits=member.habits,
                           member_timeline=json.dumps(activities, ensure_ascii=False, indent=2),
                           home_structure_with_appliances=home_with_appl,
                           season=config.DEFAULT_SEASON, weather=config.DEFAULT_WEATHER,
                           temperature=config.DEFAULT_TEMPERATURE,
                           policy_context="", world_news="")

    log_dir = os.path.join(gw.SIMULATION_DIR, env, date, "house_0001", "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    data = None
    print("================ INPUT: PROMPT ================")
    print(base_prompt)
    print("================ INPUT: JSON SCHEMA ================")
    print(json.dumps(DECISION_SCHEMA, ensure_ascii=False, indent=2))
    resp = SubAgent.single_call(base_prompt, json_mode=True, json_schema=DECISION_SCHEMA)
    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])
    try:
        data = utils.parse_json_response(resp["content"])
    except Exception as exc:
        logger.record("s4_appliance_decision", base_prompt, resp["content"], reasoning="",
                      ok=False, error=f"JSON parse failed: {exc}", attempt=1, prefix=f"{member.name}_")
        return False, {"stage": "s4_appliance_decision", "issues": [f"JSON parsing failed: {exc}"]}
    decisions = data.get("appliance_decisions", []) if isinstance(data, dict) else []
    logger.record("s4_appliance_decision", base_prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=f"{member.name}_")

    print(f"[Check] {len(decisions)} decision segments")
    for d in decisions[:5]:
        ops = len(d.get("operations", []))
        print(f"  {d.get('time')} | {d.get('location')} | {str(d.get('activity'))[:40]} | ops={ops}")

    out_dir = os.path.join(gw.SIMULATION_DIR, env, date, "house_0001")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"s4_decisions_{member.name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
    return True, data


def main():
    parser = argparse.ArgumentParser(description="Simulate step 4: appliance decisions (one member)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--member", required=True, help="member name or index")
    parser.add_argument("--date", default=None)
    parser.add_argument("--env", default=None)
    args = parser.parse_args()
    ok, result = run_step(args.world, args.member, args.date, args.env)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
