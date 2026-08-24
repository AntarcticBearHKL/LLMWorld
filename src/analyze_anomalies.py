import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulation_env import sim_root

from load_profile_cluster import scan_house_profiles
from engine.load_features import (hourly_means, load_factor, peak_to_mean,
                                  peak_overlap_count)


def zscore(values):
    n = len(values)
    if n < 3:
        return [None] * n
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    if var <= 0:
        return [0.0] * n
    std = var ** 0.5
    return [(v - mean) / std for v in values]


def build_report(profiles):
    rows = []
    for p in profiles:
        hourly = hourly_means(p["load_profile_watts"])
        rows.append({
            "house_id": p["house_id"],
            "total_kwh": p["total_energy_kwh"],
            "peak_to_mean": peak_to_mean(hourly),
            "load_factor": load_factor(hourly),
            "overlap_count": peak_overlap_count(p["load_profile_watts"]),
        })
    if not rows:
        raise ValueError("No simulation curves found")

    dims = ["total_kwh", "peak_to_mean", "load_factor", "overlap_count"]
    zs = {dim: zscore([r[dim] for r in rows]) for dim in dims}
    for i, r in enumerate(rows):
        flags = []
        for dim in dims:
            z = zs[dim][i]
            r[f"z_{dim}"] = round(z, 2) if z is not None else None
            if z is not None and abs(z) > 2:
                flag = "High" if z > 0 else "Low"
                flags.append(f"{dim}({flag} z={z:.1f})")
        r["anomaly_flags"] = flags
        r["max_abs_z"] = round(max((abs(z) for z in
                                    [zs[d][i] for d in dims]
                                    if z is not None), default=0.0), 2)

    anomalies = [r for r in rows if r["anomaly_flags"]]
    anomalies.sort(key=lambda r: -r["max_abs_z"])
    return {
        "households": len(rows),
        "anomaly_count": len(anomalies),
        "anomalies": [{"house_id": r["house_id"],
                       "max_abs_z": r["max_abs_z"],
                       "flags": r["anomaly_flags"]} for r in anomalies],
        "per_house": rows,
    }


def main():
    parser = argparse.ArgumentParser(description="Anomalous household detection (consumption pattern z-score)")
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
        args.out = os.path.join(out_dir, f"anomalies_{args.scenario}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Anomalous household detection done ({report['households']} households, "
          f"{report['anomaly_count']} anomalous households)")
    for a in report["anomalies"]:
        print(f"  {a['house_id']}: {', '.join(a['flags'])}")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
