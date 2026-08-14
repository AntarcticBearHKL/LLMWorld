









import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulation_env import sim_root


def load_household_labels(world_id):





    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.join(project_root, "worlds", world_id, "3168")
    labels = {}
    has_any = False
    if not os.path.isdir(base):
        return labels
    for house_id in sorted(os.listdir(base)):
        hpath = os.path.join(base, house_id, "household.json")
        if not os.path.isfile(hpath):
            continue
        with open(hpath, "r", encoding="utf-8") as f:
            household = json.load(f)
        members = household.get("members", [])
        if members:
            awareness = members[0].get("personality", {}).get("energy_awareness")
            if awareness:
                has_any = True
            labels[house_id] = awareness or "未知"
        else:
            labels[house_id] = "未知"
    return labels


def load_variability_labels(world_id, scenario="baseline"):

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(sim_root(world_id), "analysis",
                        f"variability_{scenario}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    labels = {}
    for house_id in data.get("regular_half", []):
        labels[house_id] = "规律"
    for house_id in data.get("variable_half", []):
        labels[house_id] = "波动"
    return labels


def load_scenario_house_kwh(world_id):






    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pop_dir = os.path.join(sim_root(world_id), "population")
    scenarios = {}
    if not os.path.isdir(pop_dir):
        return scenarios

    def classify_and_merge(path):
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        policy = data.get("policy", "baseline")
        per_house = {h["house_id"]: h["total_energy_kwh"] for h in data.get("per_house", [])}
        if per_house:
            scenarios[policy] = per_house

    for root, _, files in os.walk(pop_dir):
        for f in files:
            if f.endswith(".json"):
                classify_and_merge(os.path.join(root, f))
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
    parser = argparse.ArgumentParser(description="分组政策响应分析")
    parser.add_argument("--world", required=True)
    parser.add_argument("--label-source", default="awareness",
                        choices=["awareness", "variability"],
                        help="标签源：awareness=节能意识 / variability=行为变异性")
    args = parser.parse_args()

    if args.label_source == "variability":
        labels = load_variability_labels(args.world)
        if not labels:
            print(f"没有找到 {args.world} 的变异性标签（先跑 analyze_variability.py）")
            sys.exit(1)
    else:
        labels = load_household_labels(args.world)
        if not labels:
            print(f"没有找到 {args.world} 的 household 数据")
            sys.exit(1)
    scenarios = load_scenario_house_kwh(args.world)

    if not scenarios:
        print(f"没有找到 {args.world} 的聚合数据")
        sys.exit(1)

    print(f"家庭标签: {labels}")
    print(f"可用场景: {list(scenarios.keys())}")

    rows = group_stats(labels, scenarios)

    print("\n=== 分组政策响应（总 kWh，括号为 vs 基线%）===")
    header = f"{'组':<6}{'户数':<4}{'基线':<10}"
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

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(sim_root(args.world), "analysis")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"groups_{args.label_source}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"label_source": args.label_source,
                   "labels": labels, "scenarios": {k: v for k, v in scenarios.items()},
                   "groups": rows}, f, ensure_ascii=False, indent=2)
    print(f"\n已保存: {out_path}")


if __name__ == "__main__":
    main()
