import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root

from engine.load_features import (hourly_means, variability_index,
                                  peak_hour_shift, daily_kwh_cv,
                                  hourly_cv_curve)


def scan_house_daily_profiles(world_id, scenario):
    simulation_root = os.path.join(sim_root(world_id))
    if not os.path.isdir(simulation_root):
        return []
    per_house = []
    for postcode_dir in sorted(os.listdir(simulation_root)):
        postcode_path = os.path.join(simulation_root, postcode_dir)
        if not os.path.isdir(postcode_path) or postcode_dir == "population":
            continue
        for house_id in sorted(os.listdir(postcode_path)):
            scenario_dir = os.path.join(postcode_path, house_id, scenario)
            if not os.path.isdir(scenario_dir):
                continue
            dates = sorted(d for d in os.listdir(scenario_dir)
                           if os.path.isdir(os.path.join(scenario_dir, d)))
            days = []
            for date_dir in dates:
                path = os.path.join(scenario_dir, date_dir, "ElectricityInfo",
                                    "house_load_profile_1440min.json")
                if not os.path.exists(path):
                    continue
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                days.append({
                    "date": date_dir,
                    "kwh": data.get("total_energy_kwh", 0.0),
                    "hourly": hourly_means(data.get("load_profile_watts", [])),
                })
            if days:
                per_house.append({"house_id": house_id, "days": days})
    return per_house


def build_report(per_house):
    rows = []
    for house in per_house:
        daily_hourly = [d["hourly"] for d in house["days"]]
        rows.append({
            "house_id": house["house_id"],
            "n_days": len(house["days"]),
            "variability_index": round(variability_index(daily_hourly), 4),
            "peak_hour_shift": round(peak_hour_shift(daily_hourly), 2),
            "daily_kwh_cv": round(daily_kwh_cv([d["kwh"] for d in house["days"]]), 4),
            "mean_kwh": round(sum(d["kwh"] for d in house["days"]) / len(house["days"]), 4),
            "hourly_cv_curve": [round(v, 4) for v in hourly_cv_curve(daily_hourly)],
            "daily_kwhs": [round(d["kwh"], 2) for d in house["days"]],
        })
    if not rows:
        raise ValueError("No multi-day simulation curves found")
    rows.sort(key=lambda r: r["variability_index"])
    split = max(1, len(rows) // 2)
    low = rows[:split]
    high = rows[split:]
    return {
        "households": len(rows),
        "n_days_max": max(r["n_days"] for r in rows),
        "regular_half": [r["house_id"] for r in low],
        "variable_half": [r["house_id"] for r in high],
        "per_house": rows,
    }


def main():
    parser = argparse.ArgumentParser(description="Cross-day behavior variability analysis")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--out", default=None, help="Output file path; defaults to analysis/")
    args = parser.parse_args()

    per_house = scan_house_daily_profiles(args.world_id, args.scenario)
    report = build_report(per_house)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario

    if not args.out:
        analysis_dir = os.path.join(sim_root(args.world_id),
                                    "analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        args.out = os.path.join(analysis_dir,
                                f"variability_{args.scenario}.json")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Behavior variability analysis done ({report['households']} households, max {report['n_days_max']} days)")
    print("  Most regular (low variability): " + ", ".join(report["regular_half"][:8]))
    print("  Most variable (high variability): " + ", ".join(report["variable_half"][:8]))
    for r in report["per_house"][:5]:
        print(f"    {r['house_id']}: variability index {r['variability_index']}, "
              f"peak hour shift {r['peak_hour_shift']}h, daily kWh CV {r['daily_kwh_cv']}")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
