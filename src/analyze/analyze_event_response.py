import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root

from analyze_behavior_patterns import (scan_household_days, build_report)
from engine.load_features import hourly_means, normalize_shape


def load_event_dates(world_id):
    path = os.path.join(PROJECT_ROOT, "output", "worlds", world_id, "events.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    by_date = {}
    for item in data.get("events", []):
        date = item.get("date", "")
        if date:
            by_date.setdefault(date, []).append(item)
    return by_date


def _normalize_date(date_str):
    date_str = date_str.replace("-", "-").replace("-", "-").replace("", "")
    if len(date_str) == 8 and date_str.isdigit():
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return date_str


def build_event_response(samples, event_dates, k=0):
    if not samples:
        raise ValueError("No simulation curves found")
    report = build_report(samples, k)
    by_house = {}
    for s in samples:
        by_house.setdefault(s["house_id"], []).append(s)
    for house_id, days in by_house.items():
        days.sort(key=lambda d: _normalize_date(d["date"]))

    transitions_by_date = {}
    kwh_by_date = {}
    for house_id, days in by_house.items():
        for i in range(1, len(days)):
            prev = days[i - 1]
            cur = days[i]
            date = _normalize_date(cur["date"])
            prev_date = _normalize_date(prev["date"])
            if date == prev_date:
                continue
            bucket = transitions_by_date.setdefault(date, {"n": 0, "moves": 0})
            bucket["n"] += 1
            if cur["cluster"] != prev["cluster"]:
                bucket["moves"] += 1
            kwhs = kwh_by_date.setdefault(date, [])
            kwhs.append(cur["kwh"])

    event_keys = {_normalize_date(d): d for d in event_dates}
    event_dates_norm = set(event_keys.keys())
    per_event = []
    for norm, original in sorted(event_keys.items()):
        around = [d for d in sorted(transitions_by_date.keys()) if d != norm]
        baseline_entries = [d for d in around if d not in event_dates_norm]
        move_rate = _bucket_rate(transitions_by_date.get(norm))
        baseline_rate = _avg_rate([transitions_by_date[d] for d in baseline_entries])
        kwh_now = _mean(kwh_by_date.get(norm))
        kwh_before = _mean([v for d in baseline_entries for v in kwh_by_date.get(d, [])])
        change_pct = None
        if kwh_now is not None and kwh_before:
            change_pct = round((kwh_now / kwh_before - 1) * 100, 2)
        per_event.append({
            "date": original,
            "titles": [e.get("title", "") for e in event_dates.get(original, [])],
            "move_rate": round(move_rate, 4) if move_rate is not None else None,
            "baseline_move_rate": round(baseline_rate, 4) if baseline_rate is not None else None,
            "mean_kwh": kwh_now,
            "baseline_mean_kwh": round(kwh_before, 4) if kwh_before else None,
            "kwh_change_pct": change_pct,
        })

    event_buckets = [transitions_by_date[d] for d in event_dates_norm
                     if d in transitions_by_date]
    event_rate = _avg_rate(event_buckets)
    overall_moves = [transitions_by_date[d] for d in transitions_by_date
                     if d not in event_dates_norm]
    return {
        "households": len(by_house),
        "event_days": len(per_event),
        "event_move_rate": round(event_rate, 4) if event_rate is not None else None,
        "non_event_move_rate": round(_avg_rate(overall_moves), 4) if overall_moves else None,
        "per_event": per_event,
    }


def _bucket_rate(bucket):
    if not bucket or not bucket["n"]:
        return None
    return bucket["moves"] / bucket["n"]


def _avg_rate(buckets):
    buckets = [b for b in buckets if b and b["n"]]
    if not buckets:
        return None
    total_n = sum(b["n"] for b in buckets)
    total_moves = sum(b["moves"] for b in buckets)
    return total_moves / total_n


def _mean(values):
    values = [v for v in (values or []) if v is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def main():
    parser = argparse.ArgumentParser(description="News event x behavior pattern transition analysis")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--k", type=int, default=0)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    samples = scan_household_days(args.world_id, args.scenario)
    events = load_event_dates(args.world_id)
    report = build_event_response(samples, events, args.k)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario

    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir,
                                f"event_response_{args.scenario}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Event response analysis done ({report['households']} households, "
          f"{report['event_days']} event days)")
    print(f"  Event-day move rate {report['event_move_rate']} vs "
          f"non-event days {report['non_event_move_rate']}")
    for e in report["per_event"]:
        print(f"  [{e['date']}] {e['titles'][0] if e['titles'] else ''}: "
              f"move rate {e['move_rate']} (baseline {e['baseline_move_rate']}), "
              f"energy {e['mean_kwh']}kWh ({e['kwh_change_pct']}%)")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
