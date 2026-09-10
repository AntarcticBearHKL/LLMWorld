import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root
from dataset import (list_dates, list_houses, read_household,
                     household_features, discover_policy_tags,
                     population_profile)


def load_household_labels(world_id):
    labels = {}
    for date in list_dates(world_id):
        for house_id in list_houses(world_id, world_id, date):
            if house_id in labels:
                continue
            household = read_household(world_id, house_id)
            if not household:
                labels[house_id] = "Unknown"
                continue
            awareness = household_features(household).get("energy_awareness")
            labels[house_id] = awareness if awareness not in (None, "?") else "Unknown"
    return labels


def load_variability_labels(world_id, scenario="baseline"):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(sim_root(world_id), "analysis",
                        f"variability_{scenario}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    labels = {}
    for house_id in data.get("regular_half", []):
        labels[house_id] = "Regular"
    for house_id in data.get("variable_half", []):
        labels[house_id] = "Variable"
    return labels


def load_scenario_house_kwh(world_id):
    dates = list_dates(world_id)
    policies = set()
    for date in dates:
        for house_id in list_houses(world_id, world_id, date):
            house_dir = os.path.join(sim_root(world_id), date, house_id)
            for tag in discover_policy_tags(house_dir):
                policies.add(tag)

    scenarios = {}
    for policy in ["baseline"] + sorted(policies):
        totals = {}
        for date in dates:
            profile = population_profile(world_id, policy, date)
            for item in profile.get("per_house", []):
                totals.setdefault(item["house_id"], []).append(item["total_energy_kwh"])
        per_house = {house_id: sum(values) / len(values)
                     for house_id, values in totals.items() if values}
        if per_house:
            scenarios[policy] = per_house
    return scenarios


def group_stats(labels, scenarios):
    group_names = []
    for house_id, label in labels.items():
        if label not in group_names:
            group_names.append(label)

    rows = []
    for group in group_names:
        house_ids = [h for h, lab in labels.items() if lab == group]
        if not house_ids:
            continue
        row = {"group": group, "households": len(house_ids)}
        base_kwh = None
        if "baseline" in scenarios:
            base_kwh = sum(scenarios["baseline"].get(h, 0) for h in house_ids) / len(house_ids)
        row["baseline_mean_kwh"] = round(base_kwh, 3) if base_kwh is not None else None
        for scenario in scenarios:
            if scenario == "baseline":
                continue
            vals = [scenarios[scenario].get(h, 0) for h in house_ids]
            mean = sum(vals) / len(vals)
            row[f"{scenario}_mean_kwh"] = round(mean, 3)
            if base_kwh:
                row[f"{scenario}_change_pct"] = round((mean / base_kwh - 1) * 100, 2)
            else:
                row[f"{scenario}_change_pct"] = None
        rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description="Grouped policy response analysis")
    parser.add_argument("--world", required=True)
    parser.add_argument("--label-source", default="awareness",
                        choices=["awareness", "variability"],
                        help="Label source: awareness = energy awareness / variability = behavior variability")
    args = parser.parse_args()

    if args.label_source == "variability":
        labels = load_variability_labels(args.world)
        if not labels:
            print(f"No variability labels found for {args.world} (run analyze_variability.py first)")
            sys.exit(1)
    else:
        labels = load_household_labels(args.world)
        if not labels:
            print(f"No household data found for {args.world}")
            sys.exit(1)
    scenarios = load_scenario_house_kwh(args.world)

    if not scenarios:
        print(f"No aggregated data found for {args.world}")
        sys.exit(1)
    if "baseline" not in scenarios:
        print(f"No baseline data found for {args.world}")
        sys.exit(1)

    print(f"Household labels: {labels}")
    print(f"Available scenarios: {list(scenarios.keys())}")

    rows = group_stats(labels, scenarios)

    print("\n=== Grouped policy response (total kWh; parentheses show % vs baseline) ===")
    header = f"{'Group':<6}{'N':<4}{'Baseline':<10}"
    for s in scenarios:
        if s != "baseline":
            header += f"{s:<18}"
    print(header)
    for r in rows:
        line = f"{r['group']:<6}{r['households']:<4}{str(r['baseline_mean_kwh']):<10}"
        for s in scenarios:
            if s != "baseline":
                line += f"{r[s + '_mean_kwh']} ({r[s + '_change_pct']:+.1f}%)".ljust(18)
        print(line)

    out_dir = os.path.join(sim_root(args.world), "analysis")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"groups_{args.label_source}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"label_source": args.label_source,
                   "labels": labels, "scenarios": {k: v for k, v in scenarios.items()},
                   "groups": rows}, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
