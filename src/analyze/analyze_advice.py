import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root

from analyze_anomalies import build_report as build_anomaly_report
from load_profile_cluster import scan_house_profiles
from engine.load_features import hourly_means, peak_hour, peak_to_mean


def advice_for(metrics):
    advice = []
    if metrics.get("total_kwh_z") is not None and metrics["total_kwh_z"] > 2:
        advice.append("Energy use significantly above community average: set the AirConditioner above 26 C, "
                      "turn off lights when leaving, switch to LED, and shorten high-power appliance usage time")
    if metrics.get("overlap_count", 0) > 0:
        advice.append("High-power appliance overlap detected: stagger WashingMachine/VacuumCleaner usage away from "
                      "the AirConditioner and InductionCooker to avoid same-hour overlap")
    if metrics.get("peak_hour") is not None and 17 <= metrics["peak_hour"] <= 21:
        advice.append("Evening peak concentration: move WashingMachine/VacuumCleaner/ElectricVehicle charging to "
                      "after 22:00 (off-peak rates are cheaper)")
    if metrics.get("peak_to_mean") is not None and metrics["peak_to_mean"] > 5:
        advice.append("Large peak-to-valley gap: spread electricity usage across hours and avoid instantaneous high power")
    return advice


def build_report(profiles):
    anomaly = build_anomaly_report(profiles)
    rows = []
    for r in anomaly["per_house"]:
        hourly = hourly_means(
            next(p["load_profile_watts"] for p in profiles
                 if p["house_id"] == r["house_id"]))
        metrics = {
            "total_kwh_z": r.get("z_total_kwh"),
            "overlap_count": r.get("overlap_count", 0),
            "peak_hour": peak_hour(hourly),
            "peak_to_mean": peak_to_mean(hourly),
        }
        advice = advice_for(metrics)
        if not advice:
            advice = ["Energy usage pattern is healthy; keep current habits"]
        rows.append({"house_id": r["house_id"], "advice": advice})
    return {"households": len(rows), "per_house": rows}


def main():
    parser = argparse.ArgumentParser(description="Personalized energy-saving advice (advisor)")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to the last day per household")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    profiles = scan_house_profiles(args.world_id, args.scenario, args.date)
    report = build_report(profiles)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    report["date"] = args.date or "latest"

    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        date_tag = args.date.replace("-", "") if args.date else "latest"
        args.out = os.path.join(out_dir,
                                f"advice_{args.scenario}_{date_tag}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Personalized advice generation done ({report['households']} households)")
    for r in report["per_house"]:
        print(f"  {r['house_id']}:")
        for a in r["advice"]:
            print(f"    - {a}")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
