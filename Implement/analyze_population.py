"""人口行为归因分析：家庭类型/人格维度/成员规模 → 日用电差异（0 token 离线）。

数据源：
- worlds/<world_id>/3168/house_XXXX/household.json（v2 人口含 Big Five）
- outputs/<world_id>/population/<scenario>/<date>/population_profile_1440min.json（per_house）

输出：分组表 + 人格×用电相关性表 + JSON。

用法：
    python Implement/analyze_population.py --world pop03 --scenario baseline --date 2026-04-21
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_households(world_id):
    """worlds/<id>/3168/house_XXXX/household.json → {house_id: household}"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.join(project_root, "worlds", world_id, "3168")
    households = {}
    if not os.path.isdir(base):
        return households
    for house_id in sorted(os.listdir(base)):
        p = os.path.join(base, house_id, "household.json")
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                households[house_id] = json.load(f)
    return households


def load_per_house_kwh(world_id, scenario, date):
    """聚合曲线 per_house → {house_id: kwh}"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(project_root, "outputs", world_id, "population",
                     scenario, date, "population_profile_1440min.json")
    if not os.path.exists(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {h["house_id"]: h["total_energy_kwh"] for h in data.get("per_house", [])}


def household_features(household):
    """提取分析特征：类型/成员数/第一成员人格。"""
    members = household.get("members", [])
    first = members[0] if members else {}
    pers = first.get("personality", {})
    return {
        "household_type": household.get("type", "?"),
        "members_count": len(members),
        "energy_awareness": pers.get("energy_awareness", "?"),
        "big_five": pers.get("big_five", {}),
        "age": first.get("age", 0),
    }


def group_mean(items):
    """items: [(标签, 值)] → {标签: 均值}（按值降序）。"""
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
        raise ValueError("缺数据：请确认 world/scenario/date 正确")

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
        "by_members_count": group_mean([(f"{r['members_count']}人", r["kwh"]) for r in rows]),
    }
    # 节能意识维度（去作弊化后无该字段则跳过）
    aware = [(r["energy_awareness"], r["kwh"]) for r in rows
             if r.get("energy_awareness") not in (None, "?", "未知")]
    if aware:
        report["by_awareness"] = group_mean(aware)

    # 人格维度相关性（第一成员五维 vs 户 kWh）
    dims = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    corr = {}
    for dim in dims:
        pairs = [(r["big_five"].get(dim), r["kwh"]) for r in rows if r["big_five"].get(dim)]
        if pairs:
            a = [p[0] for p in pairs]
            b = [p[1] for p in pairs]
            corr[dim] = pearson(a, b)
    report["big_five_corr_with_kwh"] = corr

    # 成员数 vs kWh 相关性（规模效应）
    report["members_kwh_corr"] = pearson([r["members_count"] for r in rows],
                                         [r["kwh"] for r in rows])

    return report, rows


def main():
    parser = argparse.ArgumentParser(description="人口行为归因分析")
    parser.add_argument("--world", required=True)
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default="2026-04-21")
    parser.add_argument("--dates", nargs="+", default=None,
                        help="多日期对比（如 --dates 2026-04-21 2026-04-22），输出逐日户均/总用电")
    args = parser.parse_args()

    if args.dates:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print("=== 多日轨迹（户均 kWh）===")
        print(f"{'日期':<14}{'户均':<10}{'总用电':<12}逐户数")
        for d in args.dates:
            report, rows = analyze(args.world, args.scenario, d)
            print(f"{d:<14}{report['mean_household_kwh']:<10}{report['total_kwh']:<12}{report['households']}")
        return

    report, rows = analyze(args.world, args.scenario, args.date)

    print("=== 家庭类型 vs 户均用电 ===")
    for k, v in report["by_type"].items():
        print(f"  {k}: {v} kWh")
    print("=== 节能意识 vs 户均用电 ===")
    for k, v in report["by_awareness"].items():
        print(f"  {k}: {v} kWh")
    print("=== 成员数 vs 户均用电 ===")
    for k, v in report["by_members_count"].items():
        print(f"  {k}: {v} kWh")
    print("=== Big Five（第一成员）× 户用电相关性 ===")
    for dim, c in report["big_five_corr_with_kwh"].items():
        print(f"  {dim}: {c}")
    print(f"  成员数×用电相关: {report['members_kwh_corr']}")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(project_root, "outputs", args.world, "analysis")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"population_{args.scenario}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n已保存: {out_path}")


if __name__ == "__main__":
    main()
