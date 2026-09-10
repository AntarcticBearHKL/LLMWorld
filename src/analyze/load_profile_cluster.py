import argparse
import json
import os
import sys

import numpy as np
from sklearn.cluster import KMeans

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root
from dataset import iter_house_days, list_dates


# --- Load feature math, moved verbatim from the removed engine/load_features.py ---
def hourly_means(profile_watts):
    if len(profile_watts) < 1440:
        raise ValueError("Load curve length is less than 1440 minutes")
    hourly = []
    for h in range(24):
        seg = profile_watts[h * 60:(h + 1) * 60]
        hourly.append(sum(seg) / 60.0)
    return hourly


def normalize_shape(hourly):
    total = sum(hourly)
    if total <= 0:
        return [0.0] * len(hourly)
    return [v / total for v in hourly]


def load_factor(hourly):
    peak = max(hourly)
    mean = sum(hourly) / len(hourly)
    if peak <= 0:
        return 0.0
    return mean / peak


def peak_hour(hourly):
    return max(range(len(hourly)), key=lambda h: hourly[h])


def valley_hour(hourly):
    return min(range(len(hourly)), key=lambda h: hourly[h])


def peak_to_mean(hourly):
    peak = max(hourly)
    mean = sum(hourly) / len(hourly)
    if mean <= 0:
        return 0.0
    return peak / mean


def hourly_cv_curve(daily_hourly):
    n_days = len(daily_hourly)
    if n_days == 0:
        return []
    curve = []
    for h in range(24):
        values = [day[h] for day in daily_hourly]
        mean = sum(values) / n_days
        if mean <= 0:
            curve.append(0.0)
            continue
        var = sum((v - mean) ** 2 for v in values) / n_days
        curve.append(var ** 0.5 / mean)
    return curve


def variability_index(daily_hourly):
    curve = hourly_cv_curve(daily_hourly)
    if not curve:
        return 0.0
    return sum(curve) / len(curve)


def peak_hour_shift(daily_hourly):
    peaks = []
    for day in daily_hourly:
        peak = max(day)
        if peak > 0:
            peaks.append(max(range(24), key=lambda h: day[h]))
    if len(peaks) < 2:
        return 0.0
    mean = sum(peaks) / len(peaks)
    var = sum((p - mean) ** 2 for p in peaks) / len(peaks)
    return var ** 0.5


def daily_kwh_cv(per_day_kwh):
    n = len(per_day_kwh)
    if n == 0:
        return 0.0
    mean = sum(per_day_kwh) / n
    if mean <= 0:
        return 0.0
    var = sum((k - mean) ** 2 for k in per_day_kwh) / n
    return var ** 0.5 / mean


def peak_overlap_events(profile_watts, threshold=8000):
    events = []
    start = None
    peak = 0.0
    for minute, watts in enumerate(profile_watts):
        if watts >= threshold:
            if start is None:
                start = minute
            peak = max(peak, watts)
        elif start is not None:
            events.append({
                "start_minute": start,
                "end_minute": minute - 1,
                "peak_watts": round(peak, 2),
                "duration_minutes": minute - start,
            })
            start = None
            peak = 0.0
    if start is not None:
        events.append({
            "start_minute": start,
            "end_minute": len(profile_watts) - 1,
            "peak_watts": round(peak, 2),
            "duration_minutes": len(profile_watts) - start,
        })
    for event in events:
        event["start_time"] = f"{event['start_minute'] // 60:02d}:{event['start_minute'] % 60:02d}"
        event["end_time"] = f"{event['end_minute'] // 60:02d}:{event['end_minute'] % 60:02d}"
    return events


def peak_overlap_count(profile_watts, threshold=8000):
    return len(peak_overlap_events(profile_watts, threshold))


def peak_overlap_minutes(profile_watts, threshold=8000):
    return sum(e["duration_minutes"] for e in peak_overlap_events(profile_watts, threshold))


def kmeans(features, k, seed=42, iters=300):
    data = np.asarray(features, dtype=float)
    n = len(data)
    if n < k:
        raise ValueError("Number of samples is less than the number of clusters")
    distinct = np.unique(np.round(data, 6), axis=0).shape[0]
    if distinct < k:
        raise ValueError("Number of distinct-shaped samples is less than the number of clusters")
    model = KMeans(n_clusters=k, init="k-means++", n_init=10,
                   max_iter=iters, random_state=seed)
    model.fit(data)
    labels = model.labels_.tolist()
    centers = model.cluster_centers_.tolist()
    wcss = float(model.inertia_)
    return labels, centers, wcss


def elbow_scores(features, k_max=8):
    n = len(features)
    scores = []
    for k in range(2, min(k_max, n) + 1):
        try:
            _, _, wcss = kmeans(features, k)
        except ValueError:
            break
        scores.append({"k": k, "wcss": round(wcss, 4)})
    return scores


def auto_k(features, k_max=8):
    scores = elbow_scores(features, k_max)
    if not scores:
        return 2
    if len(scores) == 1:
        return scores[0]["k"]
    best_k = scores[0]["k"]
    best_gain = -1.0
    prev = scores[0]["wcss"]
    for s in scores[1:]:
        gain = prev - s["wcss"]
        if gain > best_gain:
            best_gain = gain
            best_k = s["k"]
        prev = s["wcss"]
    return best_k


def _dir_date(date_str):
    return date_str.replace("-", "") if date_str else date_str


def scan_house_profiles(world_id, scenario, date):
    if not date:
        dates = list_dates(world_id)
        date = dates[-1] if dates else None
    profiles = []
    for record in iter_house_days(world_id, date=date, policy=scenario):
        profiles.append({
            "house_id": record["house_id"],
            "total_energy_kwh": record["total_energy_kwh"],
            "load_profile_watts": record["load_profile_watts"],
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
    try:
        report = build_report(profiles, args.k)
    except ValueError as exc:
        print(f"No load profile data found for {args.world_id}: {exc}")
        sys.exit(1)
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
