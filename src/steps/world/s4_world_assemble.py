import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _load_json_optional(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as exc:
        print(f"[Warning] could not read {path}: {exc}")
        return None


def run_step(world_id, house=0, seed=42):
    world_dir = os.path.join(gw.WORLDS_DIR, world_id)
    if not os.path.isdir(world_dir):
        print(f"[Error] world directory not found: {world_dir}")
        return False, "world dir missing"

    house_dir = os.path.join(world_dir, gw.CLAYTON_POSTCODE, f"house_{house + 1:04d}")
    hpath = os.path.join(house_dir, "household.json")
    if not os.path.exists(hpath):
        print(f"[Error] {hpath} not found; run step s3 first")
        return False, "household.json missing"
    with open(hpath, encoding="utf-8") as f:
        household = json.load(f)

    ht_path = os.path.join(world_dir, gw.CLAYTON_POSTCODE, "household_types.json")
    with open(ht_path, encoding="utf-8") as f:
        ht = json.load(f)
    types = ht["household_types"] if isinstance(ht, dict) else ht
    t = types[house]
    expected = int(t.get("typical_members", t.get("typical_member_count", t.get("members_min", 2))))

    household.setdefault("type", types[house].get("type", "?"))
    household["llm_generated"] = household.get("llm_generated", True)
    with open(hpath, "w", encoding="utf-8") as f:
        json.dump(household, f, ensure_ascii=False, indent=2)

    aligned = _load_json_optional(os.path.join(house_dir, "aligned_texts.json"))
    if not isinstance(aligned, list):
        aligned = []
    provenance = _load_json_optional(os.path.join(house_dir, "persona_provenance.json"))
    if isinstance(provenance, dict):
        canonical = provenance.get("canonical_persona_texts")
        if not isinstance(canonical, list):
            canonical = []
        persona_seed = provenance.get("seed")
        if not isinstance(persona_seed, int) or isinstance(persona_seed, bool):
            persona_seed = 0
        if not aligned and isinstance(provenance.get("aligned_texts"), list):
            aligned = provenance["aligned_texts"]
    else:
        canonical = []
        persona_seed = 0
        print(f"[Warning] persona_provenance.json missing for house {house}; "
              f"personas.json will use seed 0 and no canonical texts")
    if not aligned:
        print(f"[Warning] no aligned persona texts found for house {house}; personas.json will be empty")

    gw.save_household_artifacts(world_id, house, aligned, canonical, persona_seed, household)
    house_meta = {
        "house_id": f"house_{house + 1:04d}",
        "type": household.get("type", "?"),
        "members_count": len(household.get("members", [])),
        "rooms_count": len(household.get("home", {}).get("rooms", [])),
        "llm_generated": household.get("llm_generated", True),
    }
    gw.update_world_meta(world_id, house_meta)

    print(f"[House {house}] type={household.get('type')}")
    for r in household.get("home", {}).get("rooms", []):
        print(f"  room: {r.get('name')} appliances={len(r.get('appliances', []))}")
    for m in household.get("members", []):
        print(f"  member: {m.get('name')} {m.get('age')} {m.get('gender')}")
    print(f"[Done] house assembled: {house_dir}")
    return True, house_dir


def main():
    parser = argparse.ArgumentParser(description="World step 4: assemble (per house)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--house", type=int, default=0, help="household index (0-based)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    ok, result = run_step(args.world, args.house, args.seed)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
