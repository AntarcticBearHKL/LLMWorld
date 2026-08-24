"""World step 4: assemble the standard world structure for ONE house (local, no LLM).

Standalone:  python -m steps.world.s4_world_assemble --world W [--house 0] [--seed S]
Or imported: run_step(world_id, house=0, seed=42)

Reads this house's household.json (step 3) + household_types.json, builds the
standard world layout (world.json meta + district files + per-house files)
so the simulation can consume it, prints the assembled structure and reports
any validation errors.
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

import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_step(world_id, house=0, seed=42):
    """Assemble house `house` into the standard world structure."""
    world_dir = os.path.join(PROJECT_ROOT, "worlds", world_id)
    if not os.path.isdir(world_dir):
        print(f"[Error] world directory not found: {world_dir}")
        return False, "world dir missing"

    house_dir = os.path.join(world_dir, "3168", f"house_{house + 1:04d}")
    hpath = os.path.join(house_dir, "household.json")
    if not os.path.exists(hpath):
        print(f"[Error] {hpath} not found; run step s3 first")
        return False, "household.json missing"
    with open(hpath, encoding="utf-8") as f:
        household = json.load(f)

    ht_path = os.path.join(world_dir, "household_types.json")
    with open(ht_path, encoding="utf-8") as f:
        ht = json.load(f)
    types = ht["household_types"] if isinstance(ht, dict) else ht
    expected = int(types[house].get("typical_members", types[house].get("typical_member_count", 2)))

    # LLM-generated households are strictly checked against the member count in
    # s3; fallback templates may differ, so assemble with the lenient repair.
    ok, problems = gw._repair_household(household)
    print(f"[Validate] structure valid = {ok} (expected members {expected})")
    for p in problems:
        print(f"  - {p}")

    household.setdefault("type", types[house].get("type", "?"))
    household["llm_generated"] = household.get("llm_generated", True)
    with open(hpath, "w", encoding="utf-8") as f:
        json.dump(household, f, ensure_ascii=False, indent=2)

    gw.save_household_artifacts(world_id, house, [], [], 0, household)
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
