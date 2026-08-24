"""World step 1: district description -> household types.

Standalone:  python -m steps.world.s1_household_types --world W [--count N] [--seed S]
Or imported: run_step(world_id, count=1, seed=42)

Prints the full INPUT (prompt + schema) and OUTPUT (response), then parses and
validates, reporting any errors. Saves worlds/<world_id>/household_types.json.
"""
import argparse
import io
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
from engine import SubAgent, utils
from engine.prompt import Prompt
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def household_types_schema(count):
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
                    "required": ["type", "description", "typical_members", "housing_hint"],
                    "properties": {
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "typical_members": {"type": "integer", "minimum": 1, "maximum": 8},
                        "housing_hint": {"type": "string"},
                    },
                },
            }
        },
    }


def run_step(world_id, count=1, seed=config.DEFAULT_SEED):
    """Generate household types. Returns (ok, normalized_types_or_error)."""
    if not (1 <= count <= 10):
        print(f"[Error] at most 10 households per world (received {count})")
        return False, f"count {count} out of range"

    world_dir = os.path.join(PROJECT_ROOT, "worlds", world_id)
    if not os.path.isdir(world_dir):
        district_text = gw.load_district_text(None)
        world_dir, log_dir = gw.init_world(world_id, district_text, seed)
        print(f"[Info] world directory created: {world_dir}")

    log_dir = os.path.join(world_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)

    prompt = Prompt().load("generate_world_step1_types",
                           district_info=gw.load_district_text(None), count=count)
    schema = household_types_schema(count)

    print("================ INPUT: PROMPT ================")
    print(prompt)
    print("================ INPUT: JSON SCHEMA ================")
    print(json.dumps(schema, ensure_ascii=False, indent=2))

    resp = SubAgent.single_call(prompt, json_mode=True, json_schema=schema)

    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])
    logger.record("step1_types", prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix="global_")

    try:
        data = utils.parse_json_response(resp["content"])
    except Exception as e:
        print(f"[Parse error] strict JSON parse failed: {e}")
        data = gw._parse_json_lenient(resp["content"])
        print("[Parse] lenient parse succeeded")

    data = gw._coerce_household_types(data)
    raw_types = data.get("household_types") if isinstance(data, dict) else None
    if not isinstance(raw_types, list) or not raw_types:
        print("[Error] no household_types list in response")
        return False, "no household_types in response"

    normalized = []
    errors = []
    for t in raw_types[:count]:
        if not isinstance(t, dict):
            errors.append("non-dict type entry skipped")
            continue
        if "type" not in t and "household_type" in t:
            t["type"] = t["household_type"]
        if "typical_members" not in t and "typical_member_count" in t:
            t["typical_members"] = t["typical_member_count"]
        if "housing_hint" not in t:
            for k in ("typical_housing", "housing_need", "housing_type", "housing"):
                if k in t:
                    t["housing_hint"] = t[k]
                    break
        if not str(t.get("type", "")).strip():
            errors.append("entry with empty type skipped")
            continue
        try:
            members = int(t.get("typical_members", 2))
        except (TypeError, ValueError):
            m = re.search(r"\d+", str(t.get("typical_members", "")))
            members = int(m.group()) if m else 2
        members = max(1, min(8, members))
        normalized.append({
            "type": str(t["type"]).strip(),
            "description": str(t.get("description", "")).strip(),
            "typical_members": members,
            "housing_hint": str(t.get("housing_hint", "")).strip(),
        })

    if errors:
        print("[Warnings]")
        for e in errors:
            print(f"  - {e}")
    if not normalized:
        print("[Error] household type list empty after normalization")
        return False, "empty after normalization"

    print(f"[Check] {len(normalized)} types (requested {count})")
    for i, t in enumerate(normalized):
        print(f"  [{i}] {t['type']} ({t['typical_members']} members) - {t['housing_hint']}")

    gw.save_household_types(world_id, normalized)
    print(f"[Saved] worlds/{world_id}/household_types.json ({len(normalized)} types)")
    return True, normalized


def main():
    parser = argparse.ArgumentParser(description="World step 1: household types")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    args = parser.parse_args()
    ok, result = run_step(args.world, args.count, args.seed)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
