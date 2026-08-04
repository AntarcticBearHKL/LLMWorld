import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_population
import analyze_variability
import load_profile_cluster
import analyze_behavior_patterns
import analyze_groups
import compare_policies


def scan_scenarios(world_id):
    pop_dir = os.path.join(PROJECT_ROOT, "outputs", world_id, "population")
    scenarios = {}
    if not os.path.isdir(pop_dir):
        return scenarios
    for scenario in sorted(os.listdir(pop_dir)):
        sdir = os.path.join(pop_dir, scenario)
        if not os.path.isdir(sdir):
            continue
        dates = sorted(d for d in os.listdir(sdir)
                       if os.path.isdir(os.path.join(sdir, d)))
        if dates:
            scenarios[scenario] = dates
    return scenarios


def latest_date(dates, date_arg):
    if date_arg:
        return date_arg
    return dates[-1] if dates else None


def save_report(report, world_id, filename):
    analysis_dir = os.path.join(PROJECT_ROOT, "outputs", world_id, "analysis")
    os.makedirs(analysis_dir, exist_ok=True)
    path = os.path.join(analysis_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return path


def run_all(world_id, date_arg=None):
    scenarios = scan_scenarios(world_id)
    if not scenarios:
        raise ValueError(f"没有找到 {world_id} 的聚合数据")

    summary = []
    for scenario, dates in scenarios.items():
        date = latest_date(dates, date_arg)
        per_house = load_profile_cluster.scan_house_profiles(
            world_id, scenario, date)
        if per_house:
            cluster = load_profile_cluster.build_report(per_house, 0)
            cluster["world_id"] = world_id
            cluster["scenario"] = scenario
            cluster["date"] = date
            path = save_report(cluster, world_id,
                               f"clusters_{scenario}_{date.replace('-', '')}.json")
            summary.append(f"  聚类[{scenario}] k={cluster['k']} {path}")
        else:
            summary.append(f"  聚类[{scenario}] 无该日期曲线，跳过")

        daily = analyze_variability.scan_house_daily_profiles(world_id, scenario)
        if daily:
            var = analyze_variability.build_report(daily)
            var["world_id"] = world_id
            var["scenario"] = scenario
            path = save_report(var, world_id, f"variability_{scenario}.json")
            n_days = var["n_days_max"]
            summary.append(f"  变异性[{scenario}] {var['households']}户/"
                           f"{n_days}天 {path}")
        else:
            summary.append(f"  变异性[{scenario}] 无多日曲线，跳过")

        samples = analyze_behavior_patterns.scan_household_days(world_id, scenario)
        if samples:
            pattern = analyze_behavior_patterns.build_report(samples, 0)
            pattern["world_id"] = world_id
            pattern["scenario"] = scenario
            path = save_report(pattern, world_id, f"patterns_{scenario}.json")
            summary.append(f"  模式迁移[{scenario}] k={pattern['k']} {path}")
        else:
            summary.append(f"  模式迁移[{scenario}] 无数据，跳过")

        try:
            analysis, _ = analyze_population.analyze(world_id, scenario, date)
            path = save_report(analysis, world_id,
                               f"population_{scenario}.json")
            summary.append(f"  归因[{scenario}] 户均{analysis['mean_household_kwh']}"
                           f"kWh {path}")
        except ValueError as e:
            summary.append(f"  归因[{scenario}] 跳过: {e}")

    for source in ("awareness", "variability"):
        if source == "variability":
            labels = analyze_groups.load_variability_labels(world_id)
        else:
            labels = analyze_groups.load_household_labels(world_id)
        if not labels:
            summary.append(f"  分组[{source}] 无标签，跳过")
            continue
        scenarios_kwh = analyze_groups.load_scenario_house_kwh(world_id)
        if not scenarios_kwh:
            summary.append(f"  分组[{source}] 无聚合数据，跳过")
            continue
        rows = analyze_groups.group_stats(labels, scenarios_kwh)
        report = {"label_source": source, "labels": labels,
                  "scenarios": scenarios_kwh, "groups": rows}
        path = save_report(report, world_id, f"groups_{source}.json")
        summary.append(f"  分组[{source}] {len(rows)}组 {path}")

    try:
        compare_policies.main_all(
            argparse.Namespace(world=world_id, all=True, base_date=date_arg))
        summary.append("  政策矩阵 policy_matrix.json 已生成")
    except SystemExit:
        summary.append("  政策矩阵 跳过（无 baseline）")

    print(f"\n=== 分析一键化完成: {world_id} ===")
    for line in summary:
        print(line)


def main():
    parser = argparse.ArgumentParser(description="全部分析工具一键化")
    parser.add_argument("--world", required=True)
    parser.add_argument("--date", default=None, help="聚类/归因用日期，缺省取最新")
    args = parser.parse_args()
    run_all(args.world, args.date)


if __name__ == "__main__":
    main()
