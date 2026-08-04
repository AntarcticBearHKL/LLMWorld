











import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd



PEAK_HOURS = (16, 21)
VALLEY_HOURS = (22, 7)


def energy_of_hours(profile_watts, hours):

    start, end = hours
    total_wh = 0.0
    for h in range(24):
        in_window = False
        if start < end:
            in_window = start <= h < end
        else:
            in_window = h >= start or h < end
        if in_window:

            total_wh += sum(profile_watts[h * 60:(h + 1) * 60]) / 60.0
    return total_wh / 1000.0


def peak_plateau_minutes(profile_watts, ratio=0.8):

    peak = max(profile_watts)
    if peak <= 0:
        return 0
    threshold = peak * ratio
    return sum(1 for w in profile_watts if w >= threshold)


def peak_to_mean_ratio(profile_watts):

    mean = sum(profile_watts) / len(profile_watts)
    peak = max(profile_watts)
    if mean <= 0:
        return None
    return round(peak / mean, 2)


def high_overlap_minutes(profile_watts, threshold=30000):

    return sum(1 for w in profile_watts if w >= threshold)


def load_population(world_id, policy_filter=None):

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pop_dir = os.path.join(project_root, "outputs", world_id, "population")
    results = []
    if not os.path.isdir(pop_dir):
        return results
    for root, _, files in os.walk(pop_dir):
        for f in files:
            if not f.endswith(".json"):
                continue
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            policy = data.get("policy", "baseline")
            if policy_filter and policy != policy_filter:
                continue
            results.append((policy, path, data))
    return results


def compare(baseline, intervention):

    b, i = baseline["load_profile_watts"], intervention["load_profile_watts"]


    b_peak = energy_of_hours(b, PEAK_HOURS)
    i_peak = energy_of_hours(i, PEAK_HOURS)
    b_valley = energy_of_hours(b, VALLEY_HOURS)
    i_valley = energy_of_hours(i, VALLEY_HOURS)


    b_max = max(b)
    i_max = max(i)

    return {
        "intervention": intervention.get("policy", "?"),
        "total_kwh_baseline": round(baseline["total_energy_kwh"], 3),
        "total_kwh_intervention": round(intervention["total_energy_kwh"], 3),
        "total_change_pct": round((intervention["total_energy_kwh"] / baseline["total_energy_kwh"] - 1) * 100, 2),
        "peak_kwh_baseline": round(b_peak, 3),
        "peak_kwh_intervention": round(i_peak, 3),
        "peak_hours_change_pct": round((i_peak / b_peak - 1) * 100, 2) if b_peak else None,
        "valley_kwh_baseline": round(b_valley, 3),
        "valley_kwh_intervention": round(i_valley, 3),
        "valley_hours_change_pct": round((i_valley / b_valley - 1) * 100, 2) if b_valley else None,
        "max_watts_baseline": round(b_max, 2),
        "max_watts_intervention": round(i_max, 2),
        "peak_load_cut_pct": round((i_max / b_max - 1) * 100, 2) if b_max else None,
        "peak_plateau_minutes_baseline": peak_plateau_minutes(b),
        "peak_plateau_minutes_intervention": peak_plateau_minutes(i),
        "peak_plateau_cut_pct": round((peak_plateau_minutes(i) / peak_plateau_minutes(b) - 1) * 100, 2) if peak_plateau_minutes(b) else None,
        "peak_to_mean_baseline": peak_to_mean_ratio(b),
        "peak_to_mean_intervention": peak_to_mean_ratio(i),
        "high_overlap_minutes_baseline": high_overlap_minutes(b),
        "high_overlap_minutes_intervention": high_overlap_minutes(i),
        "hourly_diff_kwh": [
            round((i[h * 60:(h + 1) * 60] and sum(i[h * 60:(h + 1) * 60]) / 60.0
                   - sum(b[h * 60:(h + 1) * 60]) / 60.0) / 1000.0, 4)
            for h in range(24)
        ],
    }


def main_all(args):

    all_pop = load_population(args.world)
    baseline_items = [(p, d) for policy, p, d in all_pop
                      if d.get("policy", "baseline") == "baseline"]
    if not baseline_items:
        print("没有找到 baseline 聚合曲线")
        sys.exit(1)
    baseline_path, baseline = baseline_items[-1]

    rows = [("场景", "总kWh", "晚峰16-21点kWh", "谷段22-7点kWh", "峰值W", "峰值时刻",
             "峰值平台分钟", "峰均比", "叠加分钟(≥30kW)")]
    per_policy = {}
    for policy, path, data in all_pop:
        name = data.get("policy", "baseline")
        if name in ("baseline",):
            continue

        if name not in per_policy or path > per_policy[name][0]:
            per_policy[name] = (path, data)

    for name, (_, data) in per_policy.items():
        report = compare(baseline, data)
        peak_min = data["load_profile_watts"].index(max(data["load_profile_watts"]))
        peak_time = f"{peak_min // 60:02d}:{peak_min % 60:02d}"
        rows.append((
            name,
            f"{report['total_kwh_intervention']:.1f} ({report['total_change_pct']:+.1f}%)",
            f"{report['peak_kwh_intervention']:.1f} ({report['peak_hours_change_pct']:+.1f}%)",
            f"{report['valley_kwh_intervention']:.1f} ({report['valley_hours_change_pct']:+.1f}%)",
            f"{report['max_watts_intervention']:.0f} ({report['peak_load_cut_pct']:+.1f}%)",
            peak_time,
            f"{report['peak_plateau_minutes_intervention']} ({report['peak_plateau_cut_pct']:+.1f}%)" if report['peak_plateau_cut_pct'] is not None else str(report['peak_plateau_minutes_intervention']),
            str(report['peak_to_mean_intervention']),
            str(report['high_overlap_minutes_intervention']),
        ))


    b_peak_kwh = energy_of_hours(baseline["load_profile_watts"], PEAK_HOURS)
    b_valley_kwh = energy_of_hours(baseline["load_profile_watts"], VALLEY_HOURS)
    b_peak_min = baseline["load_profile_watts"].index(max(baseline["load_profile_watts"]))
    rows.insert(1, (
        "baseline",
        f"{baseline['total_energy_kwh']:.1f}",
        f"{b_peak_kwh:.1f}",
        f"{b_valley_kwh:.1f}",
        f"{max(baseline['load_profile_watts']):.0f}",
        f"{b_peak_min // 60:02d}:{b_peak_min % 60:02d}",
        str(peak_plateau_minutes(baseline["load_profile_watts"])),
        str(peak_to_mean_ratio(baseline["load_profile_watts"])),
        str(high_overlap_minutes(baseline["load_profile_watts"])),
    ))

    width = [10, 16, 18, 18, 18, 10, 16, 8, 18]
    header = " | ".join(r.ljust(w) for r, w in zip(rows[0], width))
    print("=== 政策场景对比矩阵（括号内为 vs 基线变化%）===")
    print(header)
    print("-" * len(header))
    for row in rows[1:]:
        print(" | ".join(r.ljust(w) for r, w in zip(row, width)))

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(project_root, "outputs", args.world, "comparison")
    os.makedirs(out_dir, exist_ok=True)
    summary_path = os.path.join(out_dir, "policy_matrix.json")
    summary = {
        "scenarios": [dict(zip(rows[0], r)) for r in rows[1:]],
        "baseline_source": baseline_path,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"汇总表已保存: {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="政策干预对比")
    parser.add_argument("--world", required=True)
    parser.add_argument("--intervention", default="tou", help="干预 policy 名（默认 tou）")
    parser.add_argument("--all", action="store_true", help="基线 + 所有干预场景并排汇总")
    parser.add_argument("--base-date", default=None,
                        help="指定基线日期（连续时间线下同日公平对比，如 2026-04-23）")
    args = parser.parse_args()

    if args.all:
        main_all(args)
        return

    baselines = load_population(args.world, "baseline")
    interventions = load_population(args.world, args.intervention)

    if not baselines:
        print(f"没有找到 baseline 聚合曲线（outputs/{args.world}/population/）")
        sys.exit(1)
    if not interventions:
        print(f"没有找到 {args.intervention} 干预曲线，请先用 --policy {args.intervention} 跑模拟")
        sys.exit(1)

    if args.base_date:

        baseline = next((d for _, p, d in baselines if args.base_date in p), None)
        baseline_path = next((p for _, p, d in baselines if args.base_date in p), None)
        if baseline is None:
            print(f"基线中找不到日期 {args.base_date}")
            sys.exit(1)
    else:
        baseline = baselines[0][2]
        baseline_path = baselines[0][1]
    intervention = interventions[-1][2]

    report = compare(baseline, intervention)
    report["baseline_source"] = baseline_path
    report["intervention_source"] = interventions[-1][1]

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(project_root, "outputs", args.world, "comparison")
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, f"{args.intervention}_vs_baseline.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("=== 政策干预效果报告 ===")
    print(f"干预: {report['intervention']}")
    print(f"总用电: {report['total_kwh_baseline']} → {report['total_kwh_intervention']} kWh"
          f"（{report['total_change_pct']:+.2f}%）")
    print(f"晚峰时段(16-21点)用电: {report['peak_kwh_baseline']} → {report['peak_kwh_intervention']} kWh"
          f"（{report['peak_hours_change_pct']:+.2f}%）")
    print(f"谷时段(22-7点)用电: {report['valley_kwh_baseline']} → {report['valley_kwh_intervention']} kWh"
          f"（{report['valley_hours_change_pct']:+.2f}%）")
    print(f"峰值负荷: {report['max_watts_baseline']} → {report['max_watts_intervention']} W"
          f"（{report['peak_load_cut_pct']:+.2f}%）")
    print(f"报告已保存: {report_path}")


    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False

        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        hours = list(range(24))
        ax.bar(hours, report["hourly_diff_kwh"], color=["#d62728" if v < 0 else "#2ca02c" for v in report["hourly_diff_kwh"]])
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axvspan(PEAK_HOURS[0], PEAK_HOURS[1], color="red", alpha=0.08, label="峰时段")
        ax.axvspan(VALLEY_HOURS[0], 24, color="green", alpha=0.08)
        ax.axvspan(0, VALLEY_HOURS[1], color="green", alpha=0.08, label="谷时段")
        ax.set_xlabel("小时")
        ax.set_ylabel("干预 - 基线 (kWh)")
        ax.set_title(f"{report['intervention']} 干预逐小时用电差（晚峰 {report['peak_hours_change_pct']:+.1f}%）")
        ax.legend()
        ax.grid(alpha=0.3)
        png_path = os.path.join(out_dir, f"{args.intervention}_hourly_diff.png")
        fig.savefig(png_path, dpi=130, bbox_inches="tight")
        plt.close(fig)
        print(f"对比图已保存: {png_path}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
