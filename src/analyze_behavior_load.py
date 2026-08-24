import argparse
from simulation_env import sim_root
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_household_rooms(world_id, house_id):
    path = os.path.join(PROJECT_ROOT, "worlds", world_id, "3168", house_id,
                        "household.json")
    if not os.path.exists(path):
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            household = json.load(f)
        rooms = set()
        for room in household.get("home", {}).get("rooms", []):
            rooms.add(room.get("name", ""))
        return {r for r in rooms if r}
    except Exception:
        return set()


def _parse_activities(house_dir, house_id, rooms):
    activities = []
    member_count = 0
    if not os.path.isdir(house_dir):
        return activities, member_count
    for name in sorted(os.listdir(house_dir)):
        if not (name.startswith("02_SecondLayer_ProgressiveCoordination_") and name.endswith(".json")):
            continue
        member_count += 1
        try:
            with open(os.path.join(house_dir, name), "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        for item in data.get("coordinated_activities", []):
            time_range = item.get("time", "")
            location = item.get("location", "")
            if not time_range:
                continue
            start, end = _parse_minutes(time_range)
            at_home = location in rooms or "Home" in location
            activities.append({
                "time": time_range, "start": start, "end": end,
                "location": location, "activity": item.get("activity", ""),
                "at_home": at_home,
            })
    return activities, member_count


def _parse_minutes(time_range):
    try:
        from engine import utils
        return utils.parse_time_range(time_range)
    except Exception:
        return 0, 0


def build_report(house_results):
    if not house_results:
        raise ValueError("No activity/load data found")
    rows = []
    for hr in house_results:
        profile = hr["load_profile_watts"]
        at_home_watts = []
        away_watts = []
        at_home_minutes = 0
        activity_by_hour = [0] * 24
        for a in hr["activities"]:
            a_start = a.get("start", 0)
            a_end = a.get("end", 0)
            if a_end <= a_start:
                continue
            if a["at_home"]:
                at_home_minutes += min(a_end, 1440) - min(a_start, 1440)
                for m in range(a_start, min(a_end, 1440)):
                    at_home_watts.append(profile[m])
                for h in range(a_start // 60, (a_end - 1) // 60 + 1):
                    if 0 <= h < 24:
                        activity_by_hour[h] += 1
            else:
                for m in range(a_start, min(a_end, 1440)):
                    away_watts.append(profile[m])

        peak_hour = max(range(24), key=lambda h: sum(profile[h * 60:(h + 1) * 60]))
        busy_hour = max(range(24), key=lambda h: activity_by_hour[h])
        at_home_mean = sum(at_home_watts) / len(at_home_watts) if at_home_watts else 0.0
        away_mean = sum(away_watts) / len(away_watts) if away_watts else 0.0
        consistent = at_home_mean > away_mean
        peak_aligned = abs(peak_hour - busy_hour) <= 2
        rows.append({
            "house_id": hr["house_id"],
            "members": hr["member_count"],
            "at_home_minutes": at_home_minutes,
            "at_home_mean_watts": round(at_home_mean, 2),
            "away_mean_watts": round(away_mean, 2),
            "load_consistent": consistent,
            "peak_hour": peak_hour,
            "busy_hour": busy_hour,
            "peak_aligned": peak_aligned,
            "flags": ([f"at-home load ({at_home_mean:.0f}W) <= away ({away_mean:.0f}W)"
                       if not consistent else ""] +
                      [f"peak {peak_hour}:00 vs activity peak {busy_hour}:00 misaligned"
                       if not peak_aligned else ""]),
        })
    anomalies = [r for r in rows if not r["load_consistent"] or not r["peak_aligned"]]
    return {
        "households": len(rows),
        "consistent_count": len(rows) - len(anomalies),
        "anomaly_count": len(anomalies),
        "per_house": rows,
        "anomalies": [{"house_id": r["house_id"],
                       "flags": [f for f in r["flags"] if f]}
                      for r in anomalies],
    }


def scan_world(world_id, scenario, date_str):
    simulation_root = os.path.join(sim_root(world_id))
    if not os.path.isdir(simulation_root):
        return []
    house_results = []
    for postcode_dir in sorted(os.listdir(simulation_root)):
        postcode_path = os.path.join(simulation_root, postcode_dir)
        if not os.path.isdir(postcode_path) or postcode_dir == "population":
            continue
        for house_id in sorted(os.listdir(postcode_path)):
            scenario_dir = os.path.join(postcode_path, house_id, scenario)
            if not os.path.isdir(scenario_dir):
                continue
            if date_str:
                date_dirs = [d for d in os.listdir(scenario_dir)
                             if d == date_str.replace("-", "")]
            else:
                date_dirs = [d for d in sorted(os.listdir(scenario_dir))
                             if os.path.isdir(os.path.join(scenario_dir, d))]
            if not date_dirs:
                continue
            date_dir = date_dirs[-1]
            house_dir = os.path.join(scenario_dir, date_dir)
            profile_path = os.path.join(house_dir, "ElectricityInfo",
                                        "house_load_profile_1440min.json")
            if not os.path.exists(profile_path):
                continue
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
            rooms = _load_household_rooms(world_id, house_id)
            activities, member_count = _parse_activities(house_dir, house_id, rooms)
            if not activities:
                continue
            house_results.append({
                "house_id": house_id,
                "member_count": member_count,
                "activities": activities,
                "load_profile_watts": profile.get("load_profile_watts", []),
            })
    return house_results


def main():
    parser = argparse.ArgumentParser(description="Activity-load consistency check")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to the last day")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    house_results = scan_world(args.world_id, args.scenario, args.date)
    report = build_report(house_results)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    report["date"] = args.date or "latest"

    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        date_tag = args.date.replace("-", "") if args.date else "latest"
        args.out = os.path.join(out_dir,
                                f"behavior_load_{args.scenario}_{date_tag}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Activity-load consistency check done ({report['households']} households, "
          f"consistent {report['consistent_count']}, anomalous {report['anomaly_count']}）")
    for r in report["per_house"]:
        flags = "；".join(f for f in r["flags"] if f) or "OK"
        print(f"  {r['house_id']}: at home {r['at_home_mean_watts']}W / "
              f"away {r['away_mean_watts']}W, peak {r['peak_hour']}:00 "
              f"activity peak {r['busy_hour']}:00 [{flags}]")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
