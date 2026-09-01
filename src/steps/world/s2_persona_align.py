import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from engine import SubAgent, utils
from engine.subagent import LLMCallError
from engine.prompt import Prompt
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def _members_schema(member_count):
    return {
        "type": "object",
        "required": ["members"],
        "properties": {
            "members": {
                "type": "array",
                "minItems": member_count,
                "maxItems": member_count,
                "items": {
                    "type": "object",
                    "required": ["portrait"],
                    "properties": {
                        "portrait": {"type": "string"},
                    },
                },
            }
        },
    }


def load_household_types(world_id):
    path = os.path.join(gw.WORLDS_DIR, world_id, gw.CLAYTON_POSTCODE, "household_types.json")
    if not os.path.exists(path):
        print(f"[Error] {path} not found; run step s1 first")
        return None
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    return data.get("household_types") if isinstance(data, dict) else data


def normalize_type(value):
    value = dict(value)
    if "type" not in value and "household_type" in value:
        value["type"] = value["household_type"]
    if "housing_hint" not in value:
        for key in ("typical_housing", "housing_need", "housing_type", "housing"):
            if key in value:
                value["housing_hint"] = value[key]
                break
    return value


def _call_members(prompt, logger, prefix, member_count):
    print("================ INPUT ================")
    print(prompt)
    resp = SubAgent.single_call(prompt, json_mode=True, json_schema=_members_schema(member_count))
    print("================ OUTPUT ================")
    print(resp["content"])
    try:
        data = utils.parse_json_response(resp["content"])
    except Exception as exc:
        logger.record("step2_members", prompt, resp["content"], reasoning="",
                      ok=False, error=f"JSON parse failed: {exc}", attempt=1, prefix=prefix)
        raise LLMCallError(f"step2 response is not valid JSON: {exc}") from exc
    members = data.get("members") if isinstance(data, dict) else data
    if not isinstance(members, list) or not members:
        logger.record("step2_members", prompt, resp["content"], reasoning="",
                      ok=False, error="response lacks members list", attempt=1, prefix=prefix)
        raise LLMCallError("step2 response lacks members list")
    portraits = []
    for m in members:
        p = m.get("portrait") if isinstance(m, dict) else None
        if not (isinstance(p, str) and p.strip()):
            logger.record("step2_members", prompt, resp["content"], reasoning="",
                          ok=False, error="member entry has no portrait string", attempt=1, prefix=prefix)
            raise LLMCallError("step2 response has a member with no portrait string")
        portraits.append(p.strip())
    logger.record("step2_members", prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=prefix)
    return portraits


def run_step(world_id, house=0, seed=42):
    types = load_household_types(world_id)
    if types is None:
        return False, "household_types.json missing"
    try:
        household_type = normalize_type(types[house])
    except (IndexError, TypeError, KeyError) as exc:
        return False, str(exc)

    lo = int(household_type.get("members_min", household_type.get("typical_members", 2)))
    hi = int(household_type.get("members_max", household_type.get("typical_members", lo)))
    rng = random.Random(f"{world_id}-{house}-{seed}")
    member_count = rng.randint(lo, hi)
    print(f"[House {house}] {household_type.get('type')} | member range {lo}-{hi} -> decided {member_count}")

    persona_texts, _ = gw.sample_personas(household_type, seed, n=member_count)

    world_dir = os.path.join(gw.WORLDS_DIR, world_id)
    house_dir = os.path.join(world_dir, gw.CLAYTON_POSTCODE, f"house_{house + 1:04d}")
    os.makedirs(house_dir, exist_ok=True)
    log_dir = os.path.join(house_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    prefix = f"house_{house + 1:04d}_"

    prompt = Prompt().load(
        "generate_world_step2_align",
        household_type=household_type.get("type", ""),
        household_description=household_type.get("description", ""),
        household_member_count=member_count,
        persona_texts="\n\n".join(persona_texts),
    )
    portraits = _call_members(prompt, logger, prefix, member_count)

    out_path = os.path.join(house_dir, "aligned_texts.json")
    with open(out_path, "w", encoding="utf-8") as file:
        json.dump(portraits, file, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
    for i, p in enumerate(portraits, 1):
        print(f"  member {i}: {len(p)} chars, {len(p.split())} words")
    return True, portraits


def main():
    parser = argparse.ArgumentParser(description="World step 2: persona align (one call for all members)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--house", type=int, default=0, help="household index (0-based)")
    parser.add_argument("--all-houses", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.all_houses:
        types = load_household_types(args.world)
        if types is None:
            sys.exit(1)
        ok = True
        for house in range(len(types)):
            step_ok, _ = run_step(args.world, house, args.seed)
            ok = ok and step_ok
        sys.exit(0 if ok else 1)
    ok, _ = run_step(args.world, args.house, args.seed)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
