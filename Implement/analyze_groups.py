"""节能意识分组分析（论文 Costa & Kahn 2010 对齐，0 token 离线分析）。

从 worlds/<world>/ 读每户 energy_awareness 标签（第一成员），
从 outputs/<world>/population/ 各场景聚合曲线的 per_house 明细读每户总 kWh，
统计"高/中/低节能意识"三组对 baseline/TOU/nudge 的响应差异。

用法：
    python Implement/analyze_groups.py --world pop02
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_household_labels(world_id):
    """读 worlds/<world_id>/3168/house_XXXX/household.json 的节能意识标签。"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.join(project_root, "worlds", world_id, "3168")
    labels = {}
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
            # 取第一成员的节能意识作为家庭标签
            awareness = members[0].get("personality", {}).get("energy_awareness", "中")
        else:
            awareness = "中"
        labels[house_id] = awareness
    return labels


def load_scenario_house_kwh(world_id):
    """读各场景聚合曲线的 per_house 明细 → {scenario: {house_id: kwh}}。

    兼容两种目录结构：
    - 新：population/<policy>/<date>/*.json（policy 字段已写入）
    - 旧：population/<date>/*.json 或根目录 aggregate_only.json（按 policy 字段/文件名归类）
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pop_dir = os.path.join(project_root, "outputs", world_id, "population")
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
    """三组 × 各场景的均值与相对基线变化。"""
    groups = {"高": [], "中": [], "低": []}
    for house_id, awareness in labels.items():
        if awareness in groups:
            groups[awareness].append(house_id)

    rows = []
    for group, house_ids in groups.items():
        if not house_ids:
            continue   # 跳过空组
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
    parser = argparse.ArgumentParser(description="节能意识分组分析")
    parser.add_argument("--world", required=True)
    args = parser.parse_args()

    labels = load_household_labels(args.world)
    scenarios = load_scenario_house_kwh(args.world)

    if not labels:
        print(f"没有找到 {args.world} 的 household 数据")
        sys.exit(1)
    if not scenarios:
        print(f"没有找到 {args.world} 的聚合数据")
        sys.exit(1)

    print(f"家庭标签: {labels}")
    print(f"可用场景: {list(scenarios.keys())}")

    rows = group_stats(labels, scenarios)

    print("\n=== 节能意识分组响应（总 kWh，括号为 vs 基线%）===")
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
    out_dir = os.path.join(project_root, "outputs", args.world, "analysis")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "groups.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"labels": labels, "scenarios": {k: v for k, v in scenarios.items()},
                   "groups": rows}, f, ensure_ascii=False, indent=2)
    print(f"\n已保存: {out_path}")


if __name__ == "__main__":
    main()
