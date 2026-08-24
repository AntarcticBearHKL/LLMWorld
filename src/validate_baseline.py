











import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulation_env import sim_root

import math
import pandas as pd




def hourly_normalized(load_watts_or_mw, hours=24):

    n = len(load_watts_or_mw)
    if n == hours * 60:
        hourly = [sum(load_watts_or_mw[h * 60:(h + 1) * 60]) / 60.0 for h in range(hours)]
    else:
        hourly = list(load_watts_or_mw)
    mean = sum(hourly) / len(hourly)
    if mean == 0:
        return [0.0] * len(hourly)
    return [v / mean for v in hourly]


def find_peak_hour(curve):

    peak = max(range(len(curve)), key=lambda h: curve[h])
    return peak, curve[peak]


def find_valley_hour(curve):
    valley = min(range(len(curve)), key=lambda h: curve[h])
    return valley, curve[valley]


def peak_to_mean(curve):
    return max(curve)


def bimodality(curve, morning=(6, 10), evening=(16, 21)):

    m_peak = max(curve[morning[0]:morning[1] + 1])
    e_peak = max(curve[evening[0]:evening[1] + 1])
    valley = min(curve)
    return {
        "morning_peak": round(m_peak, 3),
        "evening_peak": round(e_peak, 3),
        "evening_over_morning": round(e_peak / m_peak, 3) if m_peak else None,
        "valley": round(valley, 3),
    }


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((y - mb) ** 2 for y in b) ** 0.5
    if va == 0 or vb == 0:
        return 0.0
    return cov / (va * vb)


def compare_curves(sim_curve, real_curve):

    sim_h, sim_v = find_peak_hour(sim_curve)
    real_h, real_v = find_peak_hour(real_curve)
    sim_valley, _ = find_valley_hour(sim_curve)
    real_valley, _ = find_valley_hour(real_curve)

    return {
        "sim_peak_hour": sim_h,
        "real_peak_hour": real_h,
        "peak_hour_offset": real_h - sim_h,
        "sim_peak_to_mean": round(peak_to_mean(sim_curve), 3),
        "real_peak_to_mean": round(peak_to_mean(real_curve), 3),
        "sim_bimodality": bimodality(sim_curve),
        "real_bimodality": bimodality(real_curve),
        "sim_valley_hour": sim_valley,
        "real_valley_hour": real_valley,
        "correlation": round(pearson(sim_curve, real_curve), 4),
        "sim_hourly": [round(v, 3) for v in sim_curve],
        "real_hourly": [round(v, 3) for v in real_curve],
    }




def load_real_data(path):

    df = pd.read_csv(path)
    df = df[df["region_id"] == "VIC1"]
    df["interval"] = pd.to_datetime(df["interval"])
    df = df.sort_values("interval")


    df["date"] = df["interval"].dt.date
    full_day = None
    for d, g in df.groupby("date"):
        if len(g) == 24 and g["interval"].min().hour == 0:
            full_day = g
            break
    if full_day is None:
        raise ValueError("No complete natural day (24 hours from 00:00) in the real data")
    df = full_day

    hourly = df["demand"].tolist()
    dates = df["interval"].dt.strftime("%Y-%m-%d %H:%M").tolist()
    return hourly, dates, df


def load_sim_profile(world_id):

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pop_dir = os.path.join(sim_root(world_id), "population")

    candidates = []
    if os.path.isdir(pop_dir):
        for root, _, files in os.walk(pop_dir):
            for f in files:
                if f.endswith(".json"):
                    candidates.append(os.path.join(root, f))

    if not candidates:
        raise FileNotFoundError(f"No population aggregate curve found for {world_id} (run population_runner first)")

    path = sorted(candidates)[-1]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data, path




def main():
    parser = argparse.ArgumentParser(description="Population simulation vs VIC real load baseline comparison")
    parser.add_argument("--world", required=True, help="World ID (uses its population aggregate curve)")
    parser.add_argument("--real", default=None, help="Real-data CSV (default Data/vic_electricity_data.csv)")
    parser.add_argument("--out", default=None, help="Output directory (default simulation/<world>/baseline/)")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    real_path = args.real or os.path.join(project_root, "Data", "vic_electricity_data.csv")


    sim_data, sim_path = load_sim_profile(args.world)
    real_hourly, real_dates, _ = load_real_data(real_path)
    print(f"Simulation data: {sim_path}")
    print(f"  total energy {sim_data.get('total_energy_kwh')} kWh, {sim_data.get('households')} households")
    print(f"Real data: {real_path}")
    print(f"  hourly demand {len(real_hourly)} points, first {real_dates[0]} to last {real_dates[-1]}")


    sim_curve = hourly_normalized(sim_data["load_profile_watts"])
    real_curve = hourly_normalized(real_hourly)

    report = compare_curves(sim_curve, real_curve)
    report["sim_source"] = sim_path
    report["real_source"] = real_path
    report["sim_total_kwh"] = sim_data.get("total_energy_kwh")
    report["real_mean_mw"] = round(sum(real_hourly) / len(real_hourly), 2)


    out_dir = args.out or os.path.join(sim_root(args.world), "baseline")
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "baseline_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


    print("\n=== Shape comparison report ===")
    print(f"Evening peak: sim {report['sim_peak_hour']}:00 vs real {report['real_peak_hour']}:00"
          f" (offset {report['peak_hour_offset']} hours)")
    print(f"Peak-to-mean: sim {report['sim_peak_to_mean']} vs real {report['real_peak_to_mean']}")
    print(f"Bimodality (morning/evening): sim {report['sim_bimodality']['morning_peak']}/{report['sim_bimodality']['evening_peak']}"
          f" vs real {report['real_bimodality']['morning_peak']}/{report['real_bimodality']['evening_peak']}")
    print(f"Valley time: sim {report['sim_valley_hour']}:00 vs real {report['real_valley_hour']}:00")
    print(f"Hourly correlation: {report['correlation']}")
    print(f"Report saved: {report_path}")


    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans", "DejaVu Sans", "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False

        hours = list(range(24))
        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        ax.plot(hours, report["sim_hourly"], "o-", label=f"Simulated population (world {args.world})")
        ax.plot(hours, report["real_hourly"], "s--", label="Real VIC1 demand (2026-06-23 Tuesday)")
        ax.axvline(report["sim_peak_hour"], color="C0", alpha=0.3, linestyle=":")
        ax.axvline(report["real_peak_hour"], color="C1", alpha=0.3, linestyle=":")
        ax.set_xlabel("Hour")
        ax.set_ylabel("Normalized load (daily mean = 1)")
        ax.set_title(f"Population simulation vs VIC real load shape comparison (correlation {report['correlation']})")
        ax.legend()
        ax.grid(alpha=0.3)
        png_path = os.path.join(out_dir, "baseline_shape.png")
        fig.savefig(png_path, dpi=130, bbox_inches="tight")
        plt.close(fig)
        print(f"Comparison chart saved: {png_path}")
    except ImportError:
        print("（matplotlib not installed; skipping plot)")


if __name__ == "__main__":
    main()
