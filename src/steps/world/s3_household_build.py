"""World step 3: generate household (rooms/appliances/member profiles) per house.

Standalone:  python -m steps.world.s3_household_build --world W [--house 0] [--seed S]
Or imported: run_step(world_id, house=0, seed=42)

Reads household_types.json + this house's aligned_texts.json, sends the
generation prompt (up to 3 attempts), prints full INPUT/OUTPUT per attempt,
logs every LLM call, reports validation errors, and saves the per-house
household.json under worlds/<world_id>/3168/house_XXXX/.
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

from engine import SubAgent, utils
from engine.prompt import Prompt
from appliances import get_supported_appliances_text, get_appliance_schemas_text
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HOUSEHOLD_SCHEMA = {
    "type": "object",
    "required": ["home", "members"],
    "properties": {
        "type": {"type": "string"},
        "season": {"type": "string"},
        "story": {"type": "string"},
        "home": {
            "type": "object",
            "required": ["name", "rooms"],
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "size": {"type": "integer"},
                "rooms": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "appliances"],
                        "properties": {
                            "name": {"type": "string"},
                            "size": {"type": "integer"},
                            "appliances": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["type", "brand", "power", "age"],
                                    "properties": {
                                        "type": {"type": "string"},
                                        "brand": {"type": "string"},
                                        "power": {"type": "integer"},
                                        "age": {"type": "integer"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        "members": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "age"],
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "gender": {"type": "string"},
                    "occupation": {"type": "string"},
                    "work_schedule": {"type": "object"},
                    "personality": {"type": "object"},
                    "habits": {"type": "object"},
                    "health": {"type": "object"},
                    "personal_appliances": {"type": "array"},
                },
            },
        },
    },
}


def load_json(path):
    if not os.path.exists(path):
        print(f"[Error] {path} not found; run previous step first")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize_type(t):
    t = dict(t)
    if "type" not in t and "household_type" in t:
        t["type"] = t["household_type"]
    if "housing_hint" not in t:
        for k in ("typical_housing", "housing_need", "housing_type", "housing"):
            if k in t:
                t["housing_hint"] = t[k]
                break
    return t


def build_prompt(htype, aligned):
    return Prompt().load(
        "generate_world_step3_household",
        district_info=gw.load_district_text(None),
        household_type=htype["type"],
        household_description=htype["description"],
        housing_hint=htype["housing_hint"],
        member_count=htype["typical_members"],
        persona_texts="\n\n".join(aligned),
        supported_appliances=get_supported_appliances_text(),
        appliance_schemas=get_appliance_schemas_text(),
    )


def run_step(world_id, house=0, seed=42):
    """Build household `house`. Returns (ok, household_or_error)."""
    types = load_json(os.path.join(PROJECT_ROOT, "worlds", world_id, "household_types.json"))
    if types is None:
        return False, "household_types.json missing"
    types = types["household_types"] if isinstance(types, dict) else types
    if house >= len(types):
        print(f"[Error] house index {house} out of range (0-{len(types)-1})")
        return False, f"house {house} out of range"
    htype = normalize_type(types[house])

    house_dir = os.path.join(PROJECT_ROOT, "worlds", world_id, "3168", f"house_{house + 1:04d}")
    aligned = load_json(os.path.join(house_dir, "aligned_texts.json"))
    if aligned is None:
        return False, "aligned_texts.json missing (run s2 first)"

    log_dir = os.path.join(PROJECT_ROOT, "worlds", world_id, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    prefix = f"house_{house + 1:04d}_"

    print(f"[House {house}] {htype.get('type')} | members {htype.get('typical_members')}")
    problems = []
    data = None
    for attempt in range(gw.MAX_BUILD_ATTEMPTS):
        hint = "; ".join(problems) if attempt > 0 else None
        prompt = build_prompt(htype, aligned)
        if hint:
            prompt += (f"\n\nImportant: your previous output was rejected: {hint}. "
                       "Output a complete JSON object again, containing home (rooms layout) and members.")
        print("=" * 72)
        print(f"[INPUT attempt {attempt + 1}/{gw.MAX_BUILD_ATTEMPTS}] PROMPT (len={len(prompt)})")
        print("-" * 72)
        print(prompt)
        print(f"[INPUT attempt {attempt + 1}] JSON SCHEMA")
        print(json.dumps(HOUSEHOLD_SCHEMA, ensure_ascii=False, indent=2))
        print("=" * 72)

        resp = SubAgent.single_call(prompt, json_mode=True, json_schema=HOUSEHOLD_SCHEMA)

        print(f"[OUTPUT attempt {attempt + 1}] RESPONSE (len={len(resp['content'])})")
        print("-" * 72)
        print(resp["content"])
        print("=" * 72)
        logger.record("step3_household", prompt, resp["content"], reasoning="",
                      ok=True, attempt=attempt + 1, prefix=prefix)

        try:
            data = utils.parse_json_response(resp["content"])
        except Exception:
            try:
                data = gw._parse_json_lenient(resp["content"])
                print("[Parse] lenient succeeded")
            except Exception as e:
                print(f"[Parse error] {str(e)[:200]}")
                data = None
        if not isinstance(data, dict):
            print(f"[Check] attempt {attempt + 1}: JSON parse failed")
            continue
        ok, problems = gw._repair_household(data, htype["typical_members"])
        print(f"[Check] attempt {attempt + 1}: structure valid = {ok}")
        for p in problems:
            print(f"  - {p}")
        if ok:
            break

    if not isinstance(data, dict):
        print("[Error] household generation failed all attempts "
              "(real pipeline falls back to programmatic template)")
        return False, "all attempts failed"
    ok, _ = gw._repair_household(data, htype["typical_members"])
    if not ok:
        print("[Error] household still invalid after all attempts")
        return False, "still invalid"

    data.setdefault("type", htype["type"])
    data["llm_generated"] = True
    out_path = os.path.join(house_dir, "household.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
    print(f"[Overview] rooms: {len(data.get('home', {}).get('rooms', []))} | members: {len(data.get('members', []))}")
    for m in data.get("members", []):
        pa = m.get("personal_appliances", [])
        print(f"  - {m.get('name')} {m.get('age')} | work_schedule={isinstance(m.get('work_schedule'), dict)} "
              f"| personal_appliances={len(pa)}")
    return True, data


def main():
    parser = argparse.ArgumentParser(description="World step 3: household build (per house)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--house", type=int, default=0, help="household index (0-based)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    ok, result = run_step(args.world, args.house, args.seed)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
