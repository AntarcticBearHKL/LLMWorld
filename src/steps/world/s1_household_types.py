import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
from engine import SubAgent, utils
from engine.json_parse import parse as parse_llm_json
from engine.subagent import LLMCallError
from engine.prompt import Prompt
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def _household_types_schema(count):
    return {
        "type": "object",
        "required": ["household_types"],
        "properties": {
            "household_types": {
                "type": "array",
                "minItems": count,
                "maxItems": count,
                "items": {
                    "type": "object",
                    "required": ["type", "description", "members_min", "members_max", "housing_hint"],
                    "properties": {
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "members_min": {"type": "integer", "minimum": 1, "maximum": 8},
                        "members_max": {"type": "integer", "minimum": 1, "maximum": 8},
                        "housing_hint": {"type": "string"},
                    },
                },
            }
        },
    }


def _contract_household_types(types):
    out = []
    for t in types:
        if not isinstance(t, dict):
            continue
        lo = t.get("members_min", t.get("typical_members", 2))
        hi = t.get("members_max", t.get("typical_members", lo))
        if isinstance(lo, str):
            m = re.search(r"\d+", lo)
            lo = int(m.group()) if m else 2
        if isinstance(hi, str):
            m = re.search(r"\d+", hi)
            hi = int(m.group()) if m else lo
        try:
            lo = int(lo)
        except (TypeError, ValueError):
            lo = 2
        try:
            hi = int(hi)
        except (TypeError, ValueError):
            hi = lo
        lo = max(1, min(8, lo))
        hi = max(1, min(8, hi))
        if hi < lo:
            hi = lo
        t["members_min"] = lo
        t["members_max"] = hi
        out.append(t)
    return out


def run_step(world_id, count=1, seed=config.DEFAULT_SEED, world_config=None):
    world_dir = os.path.join(gw.WORLDS_DIR, world_id)
    if not os.path.isdir(world_dir):
        world_dir, _ = gw.init_world(world_id, world_config, seed)
        print(f"[Info] world directory created: {world_dir}")

    log_dir = os.path.join(world_dir, gw.CLAYTON_POSTCODE, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    prompt = Prompt().load(
        "generate_world_step1_types",
        district_info=gw.load_district_text(gw.CLAYTON_POSTCODE, world_config),
        count=count,
    )

    print("================ INPUT: PROMPT ================")
    print(prompt)
    print("================ CALL ================")
    try:
        resp = SubAgent.single_call(prompt, json_mode=True, json_schema=_household_types_schema(count))
    except LLMCallError as exc:
        print(f"[JSON output failed] {exc}")
        logger.record("step1_types", prompt, "", reasoning="", ok=False,
                      error=str(exc), attempt=1, prefix="global_",
                      schema=_household_types_schema(count))
        return False, str(exc)
    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])
    try:
        data = parse_llm_json(resp["content"])
    except Exception as exc:
        print(f"[JSON output failed] {exc}")
        logger.record("step1_types", prompt, resp["content"], reasoning="",
                      ok=False, error=f"JSON parse failed: {exc}",
                      attempt=1, prefix="global_",
                      schema=_household_types_schema(count))
        return False, f"JSON parse failed: {exc}"
    if not isinstance(data, dict) or not isinstance(data.get("household_types"), list):
        print("[Content] response lacks household_types list")
        logger.record("step1_types", prompt, resp["content"], reasoning="",
                      ok=False, error="response lacks household_types list",
                      attempt=1, prefix="global_",
                      schema=_household_types_schema(count))
        return False, "response lacks household_types list"
    data["household_types"] = _contract_household_types(data["household_types"])
    logger.record("step1_types", prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix="global_",
                  schema=_household_types_schema(count), parsed=data)
    out_path = os.path.join(world_dir, gw.CLAYTON_POSTCODE, "household_types.json")
    with open(out_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print("=" * 72)
    for t in data["household_types"]:
        print(f"  type={t.get('type')} | members={t.get('members_min')}-{t.get('members_max')} | hint={t.get('housing_hint')}")
    print("=" * 72)
    print(f"[Saved] {out_path}")
    return True, data


def main():
    parser = argparse.ArgumentParser(description="World step 1: household types")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    args = parser.parse_args()
    ok, _ = run_step(args.world, args.count, args.seed)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
