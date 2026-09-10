import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root
from dataset import (list_dates, list_houses, read_household,
                     household_features, population_profile)


def load_households(world_id):
    households = {}
    for date in list_dates(world_id):
        for house_id in list_houses(world_id, world_id, date):
            if house_id in households:
                continue
            household = read_household(world_id, house_id)
            if household:
                households[house_id] = household
    return households


def load_per_house_kwh(world_id, scenario, date):
    profile = population_profile(world_id, scenario, date)
    return {h["house_id"]: h["total_energy_kwh"]
            for h in profile.get("per_house", [])}


def group_mean(items):
    buckets = {}
    for label, value in items:
        buckets.setdefault(label, []).append(value)
    return {k: round(sum(v) / len(v), 3) for k, v in sorted(
        buckets.items(), key=lambda kv: -sum(kv[1]) / len(kv[1]))}


def pearson(a, b):
    n = len(a)
    if n < 2:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((y - mb) ** 2 for y in b) ** 0.5
    if va == 0 or vb == 0:
        return None
    return round(cov / (va * vb), 3)


def analyze(world_id, scenario, date):
    households = load_households(world_id)
    kwhs = load_per_house_kwh(world_id, scenario, date)

    if not households or not kwhs:
        raise ValueError("Missing data: verify world/scenario/date are correct")

    rows = []
    for house_id, household in households.items():
        if house_id not in kwhs:
            continue
        feat = household_features(household)
        rows.append({"house_id": house_id, "kwh": kwhs[house_id], **feat})

    report = {
        "world": world_id, "scenario": scenario, "date": date,
        "households": len(rows),
        "total_kwh": round(sum(r["kwh"] for r in rows), 4),
        "mean_household_kwh": round(sum(r["kwh"] for r in rows) / len(rows), 4),
        "by_type": group_mean([(r["household_type"], r["kwh"]) for r in rows]),
        "by_members_count": group_mean([(f"{r['members_count']} persons", r["kwh"]) for r in rows]),
    }

    aware = [(r["energy_awareness"], r["kwh"]) for r in rows
             if r.get("energy_awareness") not in (None, "?", "Unknown")]
    if aware:
        report["by_awareness"] = group_mean(aware)


    dims = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    corr = {}
    for dim in dims:
        pairs = [(r["big_five"].get(dim), r["kwh"]) for r in rows if r["big_five"].get(dim)]
        if pairs:
            a = [p[0] for p in pairs]
            b = [p[1] for p in pairs]
            corr[dim] = pearson(a, b)
    report["big_five_corr_with_kwh"] = corr


    report["members_kwh_corr"] = pearson([r["members_count"] for r in rows],
                                         [r["kwh"] for r in rows])

    return report, rows


def main():
    parser = argparse.ArgumentParser(description="Population behavior attribution analysis")
    parser.add_argument("--world", required=True)
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to the latest simulation date")
    parser.add_argument("--dates", nargs="+", default=None,
                        help="Multi-date comparison (e.g. --dates 2026-04-21 2026-04-22); prints per-day mean/total energy")
    args = parser.parse_args()

    if args.dates:
        print("=== Multi-day trajectory (mean kWh) ===")
        print(f"{'Date':<14}{'Mean':<10}{'Total':<12}Households")
        for d in args.dates:
            try:
                report, rows = analyze(args.world, args.scenario, d)
            except ValueError as exc:
                print(f"[Error] {d}: {exc}")
                continue
            print(f"{d:<14}{report['mean_household_kwh']:<10}{report['total_kwh']:<12}{report['households']}")
        return

    if args.date:
        date = args.date
    else:
        dates = list_dates(args.world)
        if not dates:
            print(f"No simulation data found for {args.world}")
            sys.exit(1)
        date = dates[-1]
    try:
        report, rows = analyze(args.world, args.scenario, date)
    except ValueError as exc:
        print(f"[Error] {exc}")
        sys.exit(1)

    print("=== Household type vs mean energy ===")
    for k, v in report["by_type"].items():
        print(f"  {k}: {v} kWh")
    print("=== Energy awareness vs mean energy ===")
    for k, v in report.get("by_awareness", {}).items():
        print(f"  {k}: {v} kWh")
    print("=== Member count vs mean energy ===")
    for k, v in report["by_members_count"].items():
        print(f"  {k}: {v} kWh")
    print("=== Big Five (first member) x household energy correlation ===")
    for dim, c in report["big_five_corr_with_kwh"].items():
        print(f"  {dim}: {c}")
    print(f"  members x energy correlation: {report['members_kwh_corr']}")

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out_dir = os.path.join(sim_root(args.world), "analysis")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"population_{args.scenario}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
