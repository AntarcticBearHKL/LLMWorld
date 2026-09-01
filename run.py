import argparse
import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
from steps.world import s1_household_types, s2_persona_align, s3_household_build, s4_world_assemble
from steps.simulate import s1_macro_plan, s2_coordinate, s3_enrich, s4_appliance_decision

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WORLDS_DIR = os.path.join(PROJECT_ROOT, "output", "worlds")


def auto_world_id():
    while True:
        cand = f"world_{random.randint(100000, 999999)}"
        if not os.path.isdir(os.path.join(WORLDS_DIR, cand)):
            return cand


def run_house(world_id, house, seed):
    print(f"\n########## HOUSE {house} ##########")
    ok, r = s2_persona_align.run_step(world_id, house, seed)
    if not ok:
        print(f"[Abort] house {house} s2 failed: {r}")
        return False
    ok, r = s3_household_build.run_step(world_id, house, seed)
    if not ok:
        print(f"[Abort] house {house} s3 failed: {r}")
        return False
    ok, r = s4_world_assemble.run_step(world_id, house, seed)
    if not ok:
        print(f"[Abort] house {house} s4 failed: {r}")
        return False
    return True


def run_world(world_id, count, seed, workers=4):
    print(f"\n########## WORLD {world_id} (count={count}, workers={workers}) ##########")
    ok, r = s1_household_types.run_step(world_id, count, seed)
    if not ok:
        print(f"[Abort] s1 failed: {r}")
        return 1
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda h: run_house(world_id, h, seed), range(count)))
    if not all(results):
        print("[Warn] some households failed")
    print(f"\n########## WORLD {world_id} DONE ##########")
    return 0 if all(results) else 1


def get_member_names(world_id):
    home = s1_macro_plan.load_home(world_id)
    if home is None:
        return []
    members = list(home.members.values()) if isinstance(home.members, dict) else home.members
    return [m.name for m in members]


def run_simulate(world_id, date, env, workers, member=None):
    print(f"\n########## SIMULATE world={world_id} date={date} env={env} workers={workers} ##########")
    names = get_member_names(world_id)
    if not names:
        print("[Abort] no members found")
        return 1
    targets = [member] if member else names
    if member and str(member).isdigit():
        targets = [names[int(member)]]
    for m in targets:
        if m not in names:
            print(f"[Abort] member '{m}' not in {names}")
            return 1
    print(f"[Members] {targets}")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda m: s1_macro_plan.run_step(world_id, m, date, env), targets))
    if any(not r[0] for r in results):
        print("[Abort] s1 failed for some members")
        return 1

    results = [s2_coordinate.run_step(world_id, m, date, env) for m in targets]
    if any(not r[0] for r in results):
        print("[Abort] s2 failed for some members")
        return 1

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda m: s3_enrich.run_step(world_id, m, date, env), targets))
    if any(not r[0] for r in results):
        print("[Abort] s3 failed for some members")
        return 1

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda m: s4_appliance_decision.run_step(world_id, m, date, env), targets))
    if any(not r[0] for r in results):
        print("[Abort] s4 failed for some members")
        return 1

    print(f"\n########## SIMULATE DONE ({len(targets)} members) ##########")
    return 0


def main():
    parser = argparse.ArgumentParser(description="LLMWorld single entry")
    parser.add_argument("--mode", choices=["world", "simulate"], required=True)
    parser.add_argument("--world", default=None, help="world ID (auto if omitted)")
    parser.add_argument("--count", type=int, default=1, help="world: number of household types")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    parser.add_argument("--date", default=None, help="simulate: start date")
    parser.add_argument("--env", default=None, help="simulate: env id (default world id)")
    parser.add_argument("--workers", type=int, default=4, help="simulate: thread count")
    parser.add_argument("--member", default=None, help="simulate: only this member (name or index)")
    args = parser.parse_args()

    world_id = args.world or auto_world_id()
    if args.mode == "world":
        return run_world(world_id, args.count, args.seed, args.workers)
    return run_simulate(world_id, args.date, args.env, args.workers, args.member)


if __name__ == "__main__":
    sys.exit(main())
