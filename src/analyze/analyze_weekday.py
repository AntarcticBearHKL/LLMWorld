import argparse
import json
import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root
from dataset import iter_house_days


def scan_house_daily_profiles(world_id, scenario):
    per_house = {}
    for record in iter_house_days(world_id, policy=scenario):
        hourly = [sum(record["load_profile_watts"][h * 60:(h + 1) * 60]) / 60.0
                  for h in range(24)]
        per_house.setdefault(record["house_id"], []).append({
            "date": record["date"],
            "kwh": record["total_energy_kwh"],
            "hourly": hourly,
        })
    return [{"house_id": house_id, "days": days}
            for house_id, days in sorted(per_house.items())]


def weekday_group(date_dir):
    if len(date_dir) == 8 and date_dir.isdigit():
        date_str = f"{date_dir[:4]}-{date_dir[4:6]}-{date_dir[6:]}"
    else:
        date_str = date_dir
    weekday = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    return "Weekend" if weekday >= 5 else "Weekday"


def evening_kwh(hourly):
    total_wh = 0.0
    for h in range(16, 21):
        total_wh += sum(hourly[h] * 60 for _ in range(60)) / 60.0
    return total_wh / 1000.0


def build_report(per_house):
    if not per_house:
        raise ValueError("No multi-day simulation curves found")
    groups = {}
    for house in per_house:
        for day in house["days"]:
            group = weekday_group(day["date"])
            groups.setdefault(group, []).append(day)
    rows = []
    for group in ("Weekday", "Weekend"):
        days = groups.get(group, [])
        if not days:
            continue
        totals = [d["kwh"] for d in days]
        peaks = [max(d["hourly"]) for d in days]
        evenings = [evening_kwh(d["hourly"]) for d in days]
        peak_hours = [max(range(24), key=lambda h: d["hourly"][h])
                      for d in days]
        rows.append({
            "group": group,
            "samples": len(days),
            "mean_kwh": round(sum(totals) / len(totals), 4),
            "mean_peak_watts": round(sum(peaks) / len(peaks), 2),
            "mean_evening_kwh": round(sum(evenings) / len(evenings), 4),
            "mean_peak_hour": round(sum(peak_hours) / len(peak_hours), 2),
        })
    if not rows:
        raise ValueError("No usable within-week group data")
    return {"groups": rows}


def main():
    parser = argparse.ArgumentParser(description="Within-week pattern analysis (weekday vs weekend)")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    try:
        per_house = scan_house_daily_profiles(args.world_id, args.scenario)
        report = build_report(per_house)
    except ValueError as exc:
        print(f"[Error] {exc}")
        sys.exit(1)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario

    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, f"weekday_{args.scenario}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Within-week pattern analysis done")
    for r in report["groups"]:
        print(f"  {r['group']}: {r['samples']} samples, mean energy {r['mean_kwh']}kWh "
              f"peak {r['mean_peak_watts']}W evening {r['mean_evening_kwh']}kWh "
              f"peak hour {r['mean_peak_hour']}:00")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
