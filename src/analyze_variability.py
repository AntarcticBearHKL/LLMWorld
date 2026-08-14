import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
                path = os.path.join(scenario_dir, date_dir, "用电信息",
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
        raise ValueError("没有找到任何多日模拟曲线")
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
    parser = argparse.ArgumentParser(description="跨日行为变异性分析")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--out", default=None, help="输出文件路径，缺省写入 analysis/")
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

    print(f"行为变异性分析完成（{report['households']} 户，最多 {report['n_days_max']} 天）")
    print("  最规律（低变异性）：" + ", ".join(report["regular_half"][:8]))
    print("  最不规律（高变异性）：" + ", ".join(report["variable_half"][:8]))
    for r in report["per_house"][:5]:
        print(f"    {r['house_id']}: 变异指数 {r['variability_index']}, "
              f"峰时漂移 {r['peak_hour_shift']}h, 日kWh CV {r['daily_kwh_cv']}")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
