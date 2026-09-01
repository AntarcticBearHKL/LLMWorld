import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root

from analyze_variability import scan_house_daily_profiles
from engine import utils


def season_of(date_dir):
    if len(date_dir) == 8 and date_dir.isdigit():
        date_str = f"{date_dir[:4]}-{date_dir[4:6]}-{date_dir[6:]}"
    else:
        date_str = date_dir
    return utils.season_for_date(date_str)


def evening_kwh(load_watts):
    total_wh = 0.0
    for h in range(16, 21):
        total_wh += sum(load_watts[h * 60:(h + 1) * 60]) / 60.0
    return total_wh / 1000.0


def build_report(per_house):
    if not per_house:
        raise ValueError("No multi-day simulation curves found")
    groups = {}
    for house in per_house:
        for day in house["days"]:
            season = season_of(day["date"])
            group = groups.setdefault(season, [])
            group.append(day)
    rows = []
    for season in ("Summer", "Autumn", "Winter", "Spring"):
        days = groups.get(season, [])
        if not days:
            continue
        totals = [d["kwh"] for d in days]
        peaks = [max(d["hourly"]) for d in days]
        evenings = [evening_kwh(_to_watts(d["hourly"])) for d in days]
        peak_hours = [max(range(24), key=lambda h: d["hourly"][h])
                      for d in days]
        rows.append({
            "season": season,
            "samples": len(days),
            "mean_kwh": round(sum(totals) / len(totals), 4),
            "mean_peak_watts": round(sum(peaks) / len(peaks), 2),
            "mean_evening_kwh": round(sum(evenings) / len(evenings), 4),
            "mean_peak_hour": round(sum(peak_hours) / len(peak_hours), 2),
        })
    if not rows:
        raise ValueError("No usable seasonal group data")
    return {"seasons": rows}


def _to_watts(hourly):
    watts = []
    for h in range(24):
        watts.extend([hourly[h]] * 60)
    return watts


def main():
    parser = argparse.ArgumentParser(description="Seasonal load analysis")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    per_house = scan_house_daily_profiles(args.world_id, args.scenario)
    report = build_report(per_house)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario

    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, f"seasonal_{args.scenario}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Seasonal load analysis done")
    for r in report["seasons"]:
        print(f"  {r['season']}: {r['samples']} samples, "
              f"mean energy {r['mean_kwh']}kWh peak {r['mean_peak_watts']}W "
              f"evening {r['mean_evening_kwh']}kWh peak hour {r['mean_peak_hour']}:00")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
