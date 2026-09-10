"""Aggregate one metric across repeated runs (envs) into mean +/- spread.

Run-to-run variance dominates single-run results in this platform (see
reports/R047, R054), so credible magnitudes require averaging repeats. This tool
summarizes per-house or per-member total energy across a list of simulation envs.

Usage:
    python src/analyze/aggregate_runs.py --world <w> --house house_0001 \
        --date 2026-09-11 --envs run1 run2 run3 \
        [--member "Member 1"] [--tag tou]
"""

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from load_model import build_load_profile  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
WORLDS_DIR = os.path.join(PROJECT_ROOT, "output", "worlds")
SIMULATION_DIR = os.path.join(PROJECT_ROOT, "output", "simulation")


def summarize(values):
    """Mean/std/min/max of the non-None values (std is population std)."""
    clean = [float(v) for v in values if v is not None]
    n = len(clean)
    if n == 0:
        return {"n": 0, "mean": None, "std": None, "min": None, "max": None}
    mean = sum(clean) / n
    std = (sum((v - mean) ** 2 for v in clean) / n) ** 0.5
    return {"n": n, "mean": round(mean, 4), "std": round(std, 4),
            "min": round(min(clean), 4), "max": round(max(clean), 4)}


def _read_household(world, house):
    primary = os.path.join(WORLDS_DIR, world, "3168", house, "household.json")
    path = primary if os.path.exists(primary) else os.path.join(WORLDS_DIR, world, "household.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def env_total_kwh(env, world, house, date, member, tag=None):
    household = _read_household(world, house)
    suffix = ("_" + tag) if tag else ""
    path = os.path.join(SIMULATION_DIR, env, date, house, "s4_decisions_%s%s.json" % (member, suffix))
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    decisions = {member: data.get("appliance_decisions", []) if isinstance(data, dict) else []}
    return round(build_load_profile(household, decisions)[2], 4)


def main():
    parser = argparse.ArgumentParser(description="Average a metric across repeated runs")
    parser.add_argument("--world", required=True)
    parser.add_argument("--house", default="house_0001")
    parser.add_argument("--member", default="Member 1")
    parser.add_argument("--date", required=True)
    parser.add_argument("--envs", nargs="+", required=True)
    parser.add_argument("--tag", default=None, help="policy tag suffix (e.g. tou)")
    args = parser.parse_args()

    totals = {}
    for env in args.envs:
        totals[env] = env_total_kwh(env, args.world, args.house, args.date, args.member, args.tag)
    summary = summarize(list(totals.values()))
    print(json.dumps({"world": args.world, "house": args.house, "member": args.member,
                      "date": args.date, "per_env": totals, "summary": summary},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
