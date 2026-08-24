import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulation_env import sim_root

import analyze_population
import analyze_variability
import load_profile_cluster
import analyze_behavior_patterns
import analyze_groups
import compare_policies


def scan_scenarios(world_id):
    pop_dir = os.path.join(sim_root(world_id), "population")
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
    analysis_dir = os.path.join(sim_root(world_id), "analysis")
    os.makedirs(analysis_dir, exist_ok=True)
    path = os.path.join(analysis_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return path


def run_all(world_id, date_arg=None):
    scenarios = scan_scenarios(world_id)
    if not scenarios:
        raise ValueError(f"No aggregated data found for {world_id}")

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
            summary.append(f"  Clustering[{scenario}] k={cluster['k']} {path}")
        else:
            summary.append(f"  Clustering[{scenario}] no curve for that date; skipped")

        daily = analyze_variability.scan_house_daily_profiles(world_id, scenario)
        if daily:
            var = analyze_variability.build_report(daily)
            var["world_id"] = world_id
            var["scenario"] = scenario
            path = save_report(var, world_id, f"variability_{scenario}.json")
            n_days = var["n_days_max"]
            summary.append(f"  Variability[{scenario}] {var['households']} households/"
                           f"{n_days} days {path}")
        else:
            summary.append(f"  Variability[{scenario}] no multi-day curve; skipped")

        samples = analyze_behavior_patterns.scan_household_days(world_id, scenario)
        if samples:
            pattern = analyze_behavior_patterns.build_report(samples, 0)
            pattern["world_id"] = world_id
            pattern["scenario"] = scenario
            path = save_report(pattern, world_id, f"patterns_{scenario}.json")
            summary.append(f"  Pattern transitions[{scenario}] k={pattern['k']} {path}")
        else:
            summary.append(f"  Pattern transitions[{scenario}] no data; skipped")

        try:
            analysis, _ = analyze_population.analyze(world_id, scenario, date)
            path = save_report(analysis, world_id,
                               f"population_{scenario}.json")
            summary.append(f"  Attribution[{scenario}] mean {analysis['mean_household_kwh']}"
                           f"kWh {path}")
        except ValueError as e:
            summary.append(f"  Attribution[{scenario}] skipped: {e}")

        if per_house:
            import analyze_anomalies
            anom = analyze_anomalies.build_report(per_house)
            anom["world_id"] = world_id
            anom["scenario"] = scenario
            anom["date"] = date
            path = save_report(anom, world_id, f"anomalies_{scenario}.json")
            summary.append(f"  Anomalous households[{scenario}] {anom['anomaly_count']} households {path}")

        import analyze_behavior_load
        bl_rows = analyze_behavior_load.scan_world(world_id, scenario, date)
        if bl_rows:
            bl = analyze_behavior_load.build_report(bl_rows)
            bl["world_id"] = world_id
            bl["scenario"] = scenario
            bl["date"] = date
            path = save_report(bl, world_id,
                               f"behavior_load_{scenario}_{date.replace('-', '')}.json")
            summary.append(f"  Behavior-load[{scenario}] anomalous {bl['anomaly_count']} households {path}")

        import analyze_solar
        solar_profiles = [dict(p) for p in per_house]
        for p in solar_profiles:
            p["weather"] = "Sunny"
        if solar_profiles:
            from engine import utils as _utils
            season = _utils.season_for_date(date) if date else "Summer"
            sol = analyze_solar.build_report(solar_profiles, 5000.0, season)
            sol["world_id"] = world_id
            sol["scenario"] = scenario
            sol["date"] = date
            path = save_report(sol, world_id,
                               f"solar_{scenario}_{date.replace('-', '')}.json")
            summary.append(f"  PV self-consumption[{scenario}] coverage {sol['mean_solar_coverage']} {path}")

        if per_house:
            import analyze_electrification
            elec = analyze_electrification.build_report(per_house)
            elec["world_id"] = world_id
            elec["scenario"] = scenario
            elec["date"] = date
            path = save_report(elec, world_id,
                               f"electrification_{scenario}_{date.replace('-', '')}.json")
            summary.append(f"  Electrification[{scenario}] {path}")

        if per_house:
            import analyze_advice
            adv = analyze_advice.build_report(per_house)
            adv["world_id"] = world_id
            adv["scenario"] = scenario
            adv["date"] = date
            path = save_report(adv, world_id,
                               f"advice_{scenario}_{date.replace('-', '')}.json")
            summary.append(f"  Advice[{scenario}] {path}")

        if daily:
            import analyze_seasonal
            seasonal = analyze_seasonal.build_report(daily)
            seasonal["world_id"] = world_id
            seasonal["scenario"] = scenario
            path = save_report(seasonal, world_id, f"seasonal_{scenario}.json")
            summary.append(f"  Seasonal[{scenario}] {len(seasonal['seasons'])} seasons {path}")

        import analyze_weather_sensitivity
        w_points = analyze_weather_sensitivity.load_daily_points(world_id, scenario)
        if w_points:
            weather = analyze_weather_sensitivity.build_report(w_points)
            weather["world_id"] = world_id
            weather["scenario"] = scenario
            path = save_report(weather, world_id, f"weather_{scenario}.json")
            summary.append(f"  Weather sensitivity[{scenario}] correlation {weather['temperature_kwh_corr']} {path}")

    for source in ("awareness", "variability"):
        if source == "variability":
            labels = analyze_groups.load_variability_labels(world_id)
        else:
            labels = analyze_groups.load_household_labels(world_id)
        if not labels:
            summary.append(f"  Groups[{source}] no labels; skipped")
            continue
        scenarios_kwh = analyze_groups.load_scenario_house_kwh(world_id)
        if not scenarios_kwh:
            summary.append(f"  Groups[{source}] no aggregated data; skipped")
            continue
        rows = analyze_groups.group_stats(labels, scenarios_kwh)
        report = {"label_source": source, "labels": labels,
                  "scenarios": scenarios_kwh, "groups": rows}
        path = save_report(report, world_id, f"groups_{source}.json")
        summary.append(f"  Groups[{source}] {len(rows)} groups {path}")

    try:
        compare_policies.main_all(
            argparse.Namespace(world=world_id, all=True, base_date=date_arg))
        summary.append("  Policy matrix policy_matrix.json generated")
    except SystemExit:
        summary.append("  Policy matrix skipped (no baseline)")

    import analyze_world_summary
    ws = analyze_world_summary.build_report(world_id, "baseline")
    if ws["per_house"]:
        ws["world_id"] = world_id
        ws["scenario"] = "baseline"
        path = save_report(ws, world_id, "world_summary_baseline.json")
        summary.append(f"  World summary {ws['households']} households {path}")
    else:
        summary.append("  World summary skipped (no analysis data)")

    import analyze_policy_tradeoffs
    try:
        tradeoffs = analyze_policy_tradeoffs.build_report(world_id)
        tradeoffs["world_id"] = world_id
        path = save_report(tradeoffs, world_id, "policy_tradeoffs.json")
        summary.append(f"  Policy tradeoffs {len(tradeoffs['scenarios'])} policies {path}")
    except ValueError as e:
        summary.append(f"  Policy tradeoffs skipped: {e}")

    import analyze_forecast
    try:
        forecast = analyze_forecast.build_report(daily) if daily else None
        if forecast and forecast["per_house"]:
            forecast["world_id"] = world_id
            forecast["scenario"] = "baseline"
            path = save_report(forecast, world_id, "forecast_baseline.json")
            summary.append(f"  Load forecast {forecast['households']} households {path}")
        else:
            summary.append("  Load forecast skipped (insufficient multi-day data)")
    except ValueError as e:
        summary.append(f"  Load forecast skipped: {e}")

    import analyze_appliance_usage
    try:
        usage = analyze_appliance_usage.build_report(world_id, "baseline",
                                                     date_arg)
        usage["world_id"] = world_id
        usage["scenario"] = "baseline"
        date_tag = date_arg.replace("-", "") if date_arg else "latest"
        path = save_report(usage, world_id,
                           f"appliance_usage_baseline_{date_tag}.json")
        summary.append(f"  Appliance usage {len(usage['ranking'])} types {path}")
    except ValueError as e:
        summary.append(f"  Appliance usage skipped: {e}")

    import export_analysis_csv
    try:
        exported = export_analysis_csv.export_world(world_id)
        summary.append(f"  CSV export {len(exported)} files")
    except ValueError as e:
        summary.append(f"  CSV export skipped: {e}")

    print(f"\n=== One-click analysis complete: {world_id} ===")
    for line in summary:
        print(line)


def main():
    parser = argparse.ArgumentParser(description="Run all analysis tools in one go")
    parser.add_argument("--world", required=True)
    parser.add_argument("--date", default=None, help="Date for clustering/attribution; defaults to the latest")
    args = parser.parse_args()
    run_all(args.world, args.date)


if __name__ == "__main__":
    main()
