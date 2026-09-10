"""Compare one policy/scenario across multiple generated worlds (guide §7).

For RQ3 robustness: the same intervention should yield comparable aggregate
behaviour across different synthetic population structures. Aggregates each
world's population load profile into a small metric set.

Usage:
    python src/analyze/compare_worlds.py --worlds world_A world_B [--scenario tou] [--date YYYY-MM-DD]
"""

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from dataset import list_dates, population_profile  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
MORNING_HOURS = (6, 9)
EVENING_HOURS = (17, 21)


def profile_metrics(profile_watts):
    minutes = len(profile_watts)
    if not minutes:
        return {"total_kwh": 0.0, "peak_watts": 0.0, "peak_hour": 0,
                "peak_to_mean": None, "morning_kwh": 0.0, "evening_kwh": 0.0,
                "evening_morning_ratio": None}
    total_watts = sum(profile_watts)
    peak = max(profile_watts)
    mean = total_watts / minutes
    peak_minute = max(range(minutes), key=lambda m: profile_watts[m])
    morning = sum(profile_watts[MORNING_HOURS[0] * 60:MORNING_HOURS[1] * 60]) / 60.0 / 1000.0
    evening = sum(profile_watts[EVENING_HOURS[0] * 60:EVENING_HOURS[1] * 60]) / 60.0 / 1000.0
    return {
        "total_kwh": round(total_watts / 60.0 / 1000.0, 3),
        "peak_watts": round(peak, 1),
        "peak_hour": peak_minute // 60,
        "peak_to_mean": round(peak / mean, 2) if mean > 0 else None,
        "morning_kwh": round(morning, 3),
        "evening_kwh": round(evening, 3),
        "evening_morning_ratio": round(evening / morning, 2) if morning > 0 else None,
    }


def compare_worlds(worlds, scenario="baseline", date=None):
    results = {}
    for world in worlds:
        dates = list_dates(world)
        day = date or (dates[-1] if dates else None)
        if day is None:
            results[world] = {"error": "no simulation data"}
            continue
        profile = population_profile(world, scenario, day)
        metrics = profile_metrics(profile.get("load_profile_watts", []))
        results[world] = {"date": day, "households": len(profile.get("per_house", [])), **metrics}
    return results


def main():
    parser = argparse.ArgumentParser(description="Compare a scenario across worlds")
    parser.add_argument("--worlds", nargs="+", required=True)
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to each world's latest")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    results = compare_worlds(args.worlds, args.scenario, args.date)
    print(f"=== compare_worlds scenario={args.scenario} ===")
    for world, row in results.items():
        if "error" in row:
            print(f"  {world}: {row['error']}")
            continue
        print(f"  {world} ({row['date']}, {row['households']} houses): "
              f"{row['total_kwh']} kWh, peak {row['peak_watts']}W @{row['peak_hour']}:00, "
              f"peak/mean {row['peak_to_mean']}, eve/morn {row['evening_morning_ratio']}")

    out_path = args.out or os.path.join(PROJECT_ROOT, "output", "analysis",
                                        f"compare_worlds_{args.scenario}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"scenario": args.scenario, "date": args.date, "worlds": results},
                  f, ensure_ascii=False, indent=2)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
