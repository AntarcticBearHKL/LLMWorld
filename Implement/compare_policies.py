"""政策对比：基线 vs 干预场景的聚合负荷差异（论文 RQ2 的量化证据）。

用法：
    python Implement/compare_policies.py --world pop02 --intervention tou

读取 outputs/<world>/population/ 下的聚合曲线（baseline 与干预各一份），计算：
- 晚峰时段(16-21点)用电量变化%
- 峰值负荷削减%
- 谷时段(22-7点)变化%
- 逐小时差值表 + 对比图
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd


# ---------- 时段定义（与 TOU 一致）----------
PEAK_HOURS = (16, 21)      # 晚峰 16:00-21:00
VALLEY_HOURS = (22, 7)     # 谷段 22:00-次日 7:00


def energy_of_hours(profile_watts, hours):
    """给定小时区间内的总耗电（kWh）。支持跨天区间如 (22,7)。"""
    start, end = hours
    total_wh = 0.0   # 瓦·时
    for h in range(24):
        in_window = False
        if start < end:
            in_window = start <= h < end
        else:
            in_window = h >= start or h < end
        if in_window:
            # 该小时平均瓦数 × 1 小时 = 瓦·时
            total_wh += sum(profile_watts[h * 60:(h + 1) * 60]) / 60.0
    return total_wh / 1000.0   # → 千瓦时


def load_population(world_id, policy_filter=None):
    """加载 outputs/<world>/population/ 下所有聚合曲线（policy 字段匹配）。"""
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
    """两条聚合曲线 → 干预效果报告。"""
    b, i = baseline["load_profile_watts"], intervention["load_profile_watts"]

    # 各时段用电（kWh）
    b_peak = energy_of_hours(b, PEAK_HOURS)
    i_peak = energy_of_hours(i, PEAK_HOURS)
    b_valley = energy_of_hours(b, VALLEY_HOURS)
    i_valley = energy_of_hours(i, VALLEY_HOURS)

    # 峰值
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
        "hourly_diff_kwh": [
            round((i[h * 60:(h + 1) * 60] and sum(i[h * 60:(h + 1) * 60]) / 60.0
                   - sum(b[h * 60:(h + 1) * 60]) / 60.0) / 1000.0, 4)
            for h in range(24)
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="政策干预对比")
    parser.add_argument("--world", required=True)
    parser.add_argument("--intervention", default="tou", help="干预 policy 名（默认 tou）")
    args = parser.parse_args()

    baselines = load_population(args.world, "baseline")
    interventions = load_population(args.world, args.intervention)

    if not baselines:
        print(f"没有找到 baseline 聚合曲线（outputs/{args.world}/population/）")
        sys.exit(1)
    if not interventions:
        print(f"没有找到 {args.intervention} 干预曲线，请先用 --policy {args.intervention} 跑模拟")
        sys.exit(1)

    baseline = baselines[0][2]
    intervention = interventions[-1][2]   # 取最新一次干预运行

    report = compare(baseline, intervention)
    report["baseline_source"] = baselines[0][1]
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

    # 出图：逐小时差值
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
