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

        if per_house:
            import analyze_anomalies
            anom = analyze_anomalies.build_report(per_house)
            anom["world_id"] = world_id
            anom["scenario"] = scenario
            anom["date"] = date
            path = save_report(anom, world_id, f"anomalies_{scenario}.json")
            summary.append(f"  异常户[{scenario}] {anom['anomaly_count']}户 {path}")

        import analyze_behavior_load
        bl_rows = analyze_behavior_load.scan_world(world_id, scenario, date)
        if bl_rows:
            bl = analyze_behavior_load.build_report(bl_rows)
            bl["world_id"] = world_id
            bl["scenario"] = scenario
            bl["date"] = date
            path = save_report(bl, world_id,
                               f"behavior_load_{scenario}_{date.replace('-', '')}.json")
            summary.append(f"  行为-负荷[{scenario}] 异常{bl['anomaly_count']}户 {path}")

        import analyze_solar
        solar_profiles = [dict(p) for p in per_house]
        for p in solar_profiles:
            p["weather"] = "晴天"
        if solar_profiles:
            from engine import utils as _utils
            season = _utils.season_for_date(date) if date else "夏天"
            sol = analyze_solar.build_report(solar_profiles, 5000.0, season)
            sol["world_id"] = world_id
            sol["scenario"] = scenario
            sol["date"] = date
            path = save_report(sol, world_id,
                               f"solar_{scenario}_{date.replace('-', '')}.json")
            summary.append(f"  光伏自用[{scenario}] 覆盖{sol['mean_solar_coverage']} {path}")

        if per_house:
            import analyze_electrification
            elec = analyze_electrification.build_report(per_house)
            elec["world_id"] = world_id
            elec["scenario"] = scenario
            elec["date"] = date
            path = save_report(elec, world_id,
                               f"electrification_{scenario}_{date.replace('-', '')}.json")
            summary.append(f"  电气化[{scenario}] {path}")

        if per_house:
            import analyze_advice
            adv = analyze_advice.build_report(per_house)
            adv["world_id"] = world_id
            adv["scenario"] = scenario
            adv["date"] = date
            path = save_report(adv, world_id,
                               f"advice_{scenario}_{date.replace('-', '')}.json")
            summary.append(f"  建议[{scenario}] {path}")

        if daily:
            import analyze_seasonal
            seasonal = analyze_seasonal.build_report(daily)
            seasonal["world_id"] = world_id
            seasonal["scenario"] = scenario
            path = save_report(seasonal, world_id, f"seasonal_{scenario}.json")
            summary.append(f"  季节[{scenario}] {len(seasonal['seasons'])}季 {path}")

        import analyze_weather_sensitivity
        w_points = analyze_weather_sensitivity.load_daily_points(world_id, scenario)
        if w_points:
            weather = analyze_weather_sensitivity.build_report(w_points)
            weather["world_id"] = world_id
            weather["scenario"] = scenario
            path = save_report(weather, world_id, f"weather_{scenario}.json")
            summary.append(f"  天气敏感性[{scenario}] 相关{weather['temperature_kwh_corr']} {path}")

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

    import analyze_world_summary
    ws = analyze_world_summary.build_report(world_id, "baseline")
    if ws["per_house"]:
        ws["world_id"] = world_id
        ws["scenario"] = "baseline"
        path = save_report(ws, world_id, "world_summary_baseline.json")
        summary.append(f"  世界总览 {ws['households']}户 {path}")
    else:
        summary.append("  世界总览 跳过（无分析数据）")

    import analyze_policy_tradeoffs
    try:
        tradeoffs = analyze_policy_tradeoffs.build_report(world_id)
        tradeoffs["world_id"] = world_id
        path = save_report(tradeoffs, world_id, "policy_tradeoffs.json")
        summary.append(f"  政策权衡 {len(tradeoffs['scenarios'])}政策 {path}")
    except ValueError as e:
        summary.append(f"  政策权衡 跳过: {e}")

    import analyze_forecast
    try:
        forecast = analyze_forecast.build_report(daily) if daily else None
        if forecast and forecast["per_house"]:
            forecast["world_id"] = world_id
            forecast["scenario"] = "baseline"
            path = save_report(forecast, world_id, "forecast_baseline.json")
            summary.append(f"  负荷预测 {forecast['households']}户 {path}")
        else:
            summary.append("  负荷预测 跳过（多日数据不足）")
    except ValueError as e:
        summary.append(f"  负荷预测 跳过: {e}")

    import analyze_appliance_usage
    try:
        usage = analyze_appliance_usage.build_report(world_id, "baseline",
                                                     date_arg)
        usage["world_id"] = world_id
        usage["scenario"] = "baseline"
        date_tag = date_arg.replace("-", "") if date_arg else "latest"
        path = save_report(usage, world_id,
                           f"appliance_usage_baseline_{date_tag}.json")
        summary.append(f"  电器画像 {len(usage['ranking'])}类 {path}")
    except ValueError as e:
        summary.append(f"  电器画像 跳过: {e}")

    import export_analysis_csv
    try:
        exported = export_analysis_csv.export_world(world_id)
        summary.append(f"  CSV 导出 {len(exported)} 文件")
    except ValueError as e:
        summary.append(f"  CSV 导出 跳过: {e}")

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
