import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulation_env import sim_root

from engine.load_features import (hourly_means, normalize_shape, load_factor,
                                  peak_hour, valley_hour, peak_to_mean,
                                  kmeans, elbow_scores, auto_k)


def _dir_date(date_str):
    return date_str.replace("-", "") if date_str else date_str


def scan_house_profiles(world_id, scenario, date):
    simulation_root = os.path.join(sim_root(world_id))
    if not os.path.isdir(simulation_root):
        return []
    profiles = []
    for postcode_dir in sorted(os.listdir(simulation_root)):
        postcode_path = os.path.join(simulation_root, postcode_dir)
        if not os.path.isdir(postcode_path) or postcode_dir == "population":
            continue
        for house_id in sorted(os.listdir(postcode_path)):
            house_dir = os.path.join(postcode_path, house_id)
            if not os.path.isdir(house_dir):
                continue
            profile_path = None
            if date:
                date_dir = _dir_date(date)
                candidate = os.path.join(house_dir, scenario, date_dir,
                                         "ElectricityInfo", "house_load_profile_1440min.json")
                if os.path.exists(candidate):
                    profile_path = candidate
            else:
                scenario_dir = os.path.join(house_dir, scenario)
                if os.path.isdir(scenario_dir):
                    dates = sorted(d for d in os.listdir(scenario_dir)
                                   if os.path.isdir(os.path.join(scenario_dir, d)))
                    if dates:
                        candidate = os.path.join(scenario_dir, dates[-1],
                                                 "ElectricityInfo",
                                                 "house_load_profile_1440min.json")
                        if os.path.exists(candidate):
                            profile_path = candidate
            if not profile_path:
                continue
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            profiles.append({
                "house_id": house_id,
                "total_energy_kwh": data.get("total_energy_kwh", 0.0),
                "load_profile_watts": data.get("load_profile_watts", []),
            })
    return profiles


def build_report(profiles, k):
    rows = []
    for p in profiles:
        hourly = hourly_means(p["load_profile_watts"])
        rows.append({
            "house_id": p["house_id"],
            "total_energy_kwh": round(p["total_energy_kwh"], 4),
            "hourly_watts": [round(v, 2) for v in hourly],
            "shape": [round(v, 6) for v in normalize_shape(hourly)],
        })
    if not rows:
        raise ValueError("No saved simulation curves found")

    features = [r["shape"] for r in rows]
    try:
        chosen_k = k if k else auto_k(features)
        labels, centers, wcss = kmeans(features, chosen_k)
    except ValueError:
        chosen_k = 1
        labels = [0] * len(rows)
        centers = [[round(v, 6) for v in features[0]]]
        wcss = 0.0
    scores = elbow_scores(features)

    clusters = []
    for c in range(chosen_k):
        members = [rows[i] for i in range(len(rows)) if labels[i] == c]
        cluster = {
            "label": c,
            "households": len(members),
            "house_ids": [m["house_id"] for m in members],
            "center_shape": [round(v, 6) for v in centers[c]],
            "mean_load_factor": round(sum(load_factor(m["hourly_watts"]) for m in members) / len(members), 4),
            "mean_peak_to_mean": round(sum(peak_to_mean(m["hourly_watts"]) for m in members) / len(members), 4),
            "mean_peak_hour": round(sum(peak_hour(m["hourly_watts"]) for m in members) / len(members), 2),
            "mean_valley_hour": round(sum(valley_hour(m["hourly_watts"]) for m in members) / len(members), 2),
        }
        clusters.append(cluster)

    report = {
        "world_id": None,
        "scenario": None,
        "date": None,
        "households": len(rows),
        "k": chosen_k,
        "wcss": round(wcss, 4),
        "elbow": scores,
        "per_house": [
            {"house_id": rows[i]["house_id"], "cluster": labels[i],
             "total_energy_kwh": rows[i]["total_energy_kwh"]}
            for i in range(len(rows))
        ],
        "clusters": clusters,
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Household load profile clustering analysis")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to the last day per household")
    parser.add_argument("--k", type=int, default=0, help="Number of clusters; defaults to automatic selection via the elbow method")
    parser.add_argument("--out", default=None, help="Output file path; defaults to analysis/")
    args = parser.parse_args()

    profiles = scan_house_profiles(args.world_id, args.scenario, args.date)
    report = build_report(profiles, args.k)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    report["date"] = report["date"] or (args.date or "latest")

    if not args.out:
        date_tag = _dir_date(args.date) if args.date else "latest"
        analysis_dir = os.path.join(sim_root(args.world_id),
                                    "analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        args.out = os.path.join(analysis_dir,
                                f"clusters_{args.scenario}_{date_tag}.json")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Load profile clustering done ({report['households']} households, k={report['k']}, WCSS={report['wcss']})")
    for c in report["clusters"]:
        print(f"  Cluster{c['label']}: {c['households']} households "
              f"(load factor {c['mean_load_factor']}, peak-to-mean {c['mean_peak_to_mean']}, "
              f"mean peak hour {c['mean_peak_hour']}:00, valley hour {c['mean_valley_hour']}:00)")
        print(f"    Households: {', '.join(c['house_ids'])}")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
