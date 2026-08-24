"""World step 2: sample personas + align them to the household type (per house).

Standalone:  python -m steps.world.s2_persona_align --world W [--house 0] [--seed S]
Or imported: run_step(world_id, house=0, seed=42)

Reads household_types.json (step 1), samples personas for household `house`,
sends the alignment prompt, prints full INPUT/OUTPUT, reports parse/validation
errors, logs the LLM call, and saves the per-house aligned_texts.json under
worlds/<world_id>/3168/house_XXXX/.
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
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def align_members_schema(member_count):
    # minLength 200 rejects placeholder strings like "member2"
    return {
        "type": "object",
        "required": ["members"],
        "properties": {
            "members": {
                "type": "array",
                "minItems": member_count,
                "maxItems": member_count,
                "items": {"type": "string", "minLength": 200},
            }
        },
    }


def load_household_types(world_id):
    path = os.path.join(PROJECT_ROOT, "worlds", world_id, "household_types.json")
    if not os.path.exists(path):
        print(f"[Error] {path} not found; run step s1 first")
        return None
    with open(path, encoding="utf-8") as f:
        ht = json.load(f)
    types = ht["household_types"] if isinstance(ht, dict) else ht
    if not types:
        print("[Error] household_types.json is empty")
        return None
    return types


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


def run_step(world_id, house=0, seed=42):
    """Align personas for household `house`. Returns (ok, aligned_or_error)."""
    types = load_household_types(world_id)
    if types is None:
        return False, "household_types.json missing"
    if house >= len(types):
        print(f"[Error] house index {house} out of range (0-{len(types)-1})")
        return False, f"house {house} out of range"
    htype = normalize_type(types[house])

    print(f"[House {house}] {htype.get('type')} | members {htype.get('typical_members')}")

    persona_texts, rows = gw.sample_personas(htype, seed)
    print(f"[Sample] member count: {len(persona_texts)}")
    for i, p in enumerate(persona_texts):
        print(f"  ---- Member {i + 1} (len={len(p)}) ----")
        print(p)
        print("  ------------------------------")

    prompt = Prompt().load("generate_world_step2_align",
                           household_type=htype["type"],
                           household_description=htype["description"],
                           member_count=htype["typical_members"],
                           persona_texts="\n\n".join(persona_texts))
    schema = align_members_schema(htype["typical_members"])

    print("================ INPUT: PROMPT ================")
    print(prompt)
    print("================ INPUT: JSON SCHEMA ================")
    print(json.dumps(schema, ensure_ascii=False, indent=2))

    resp = SubAgent.single_call(prompt, json_mode=True, json_schema=schema)

    print("================ OUTPUT: RESPONSE ================")
    print(resp["content"])

    house_dir = os.path.join(PROJECT_ROOT, "worlds", world_id, "3168", f"house_{house + 1:04d}")
    os.makedirs(house_dir, exist_ok=True)
    log_dir = os.path.join(PROJECT_ROOT, "worlds", world_id, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    logger.record("step2_align", prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=f"house_{house + 1:04d}_")

    try:
        data = utils.parse_json_response(resp["content"])
    except Exception as e:
        print(f"[Parse error] strict JSON parse failed: {e}")
        data = gw._parse_json_lenient(resp["content"])
        print("[Parse] lenient parse succeeded")

    raw = data.get("members") if isinstance(data, dict) else None
    if isinstance(raw, list):
        aligned = [str(m).strip() for m in raw if str(m).strip()]
    elif isinstance(raw, dict):
        aligned = [str(m).strip() for m in raw.values() if str(m).strip()]
        print("[Parse] members was a dict; took values")
    else:
        aligned = []

    expected = htype["typical_members"]
    if len(aligned) != expected:
        print(f"[Error] member count mismatch: got {len(aligned)}, required {expected}")
        return False, f"member count {len(aligned)} != {expected}"

    short = [i for i, a in enumerate(aligned) if len(a) < 200]
    if short:
        print(f"[Error] members too short (placeholders?): indices {short}")
        return False, f"short members at {short}"

    print(f"[Check] aligned member count: {len(aligned)} (required {expected})")
    for i, a in enumerate(aligned):
        print(f"  ---- Aligned member {i + 1} (len={len(a)}) ----")
        print(a[:800])
        print("  ------------------------------")

    out_path = os.path.join(house_dir, "aligned_texts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(aligned, f, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
    return True, aligned


def main():
    parser = argparse.ArgumentParser(description="World step 2: persona align (per house)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--house", type=int, default=0, help="household index (0-based)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    ok, result = run_step(args.world, args.house, args.seed)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
