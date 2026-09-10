"""Compare baseline vs TOU appliance decisions (s4 outputs).

Reads s4_decisions_<member>.json (baseline) and s4_decisions_<member>_<tag>.json
(policy) for every house/member of a simulation date, then reports per-member
usage minutes and estimated kWh by tariff window (peak 16-21, valley 22-07, shoulder).

Usage:
    python src/analyze/compare_tou.py --world world_421160 --date 2026-04-21 --env world_421160 [--tag tou]
"""
import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from dataset import iter_house_days, list_dates, read_decisions
from simulate import create_home_from_household

PEAK_START = 16 * 60
PEAK_END = 21 * 60
VALLEY_START = 22 * 60
VALLEY_END = 7 * 60
WINDOWS = ("peak", "valley", "shoulder")
USD_ACTIONS = {"use", "charge_home", "charge"}


def minutes_of_day(hhmm):
    return int(hhmm[:2]) * 60 + int(hhmm[3:5])


def window_of(minute):
    if PEAK_START <= minute < PEAK_END:
        return "peak"
    if minute >= VALLEY_START or minute < VALLEY_END:
        return "valley"
    return "shoulder"


def segment_minutes(time_str):
    if not time_str or "-" not in time_str:
        return []
    start_raw, end_raw = time_str.split("-", 1)
    start = minutes_of_day(start_raw.strip())
    end = 1440 if end_raw.strip() in ("24:00", "24:0") else minutes_of_day(end_raw.strip())
    return list(range(start, max(start, end)))


def load_appliance_power(household):
    home = create_home_from_household(household)
    power = {}
    for room, details in home.get_home_structure_with_details().items():
        for appliance in details["appliances"]:
            power[appliance["unique_id"]] = float(appliance["power_watts"] or 0)
    return power


def summarize(segments, power):
    minutes = {w: 0.0 for w in WINDOWS}
    kwh = {w: 0.0 for w in WINDOWS}
    per_appliance = {}
    for segment in segments or []:
        ops = [op for op in segment.get("operations", []) if op.get("action") in USD_ACTIONS]
        if not ops:
            continue
        for minute in segment_minutes(segment.get("time", "")):
            window = window_of(minute)
            minutes[window] += 1
            for op in ops:
                watts = power.get(op.get("unique_id"), 0)
                kwh[window] += watts / 1000.0 / 60.0
                entry = per_appliance.setdefault(op.get("unique_id"), {w: 0 for w in WINDOWS})
                entry[window] += 1
    return minutes, kwh, per_appliance


def main():
    parser = argparse.ArgumentParser(description="Compare baseline vs TOU s4 decisions")
    parser.add_argument("--world", required=True)
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to the latest date")
    parser.add_argument("--env", default=None, help="Simulation env directory; defaults to the world id")
    parser.add_argument("--tag", default="tou", help="policy tag suffix of the policy s4 files")
    args = parser.parse_args()

    env = args.env or args.world
    dates = list_dates(args.world, env)
    if not dates:
        print(f"No simulation data found for {args.world} (env {env})")
        sys.exit(1)
    date = args.date or dates[-1]

    records = list(iter_house_days(args.world, env=env, date=date, policy="baseline"))
    if not records:
        print(f"No baseline s4 decisions found for {args.world}/{date}")
        sys.exit(1)

    rows = []
    for record in records:
        power = load_appliance_power(record["household"])
        for member in record["members"]:
            baseline_segments = record["decisions"].get(member, [])
            policy_segments = read_decisions(record["house_dir"], member, args.tag)
            if not policy_segments:
                continue
            b_min, b_kwh, b_app = summarize(baseline_segments, power)
            p_min, p_kwh, p_app = summarize(policy_segments, power)

            peak_delta = (p_kwh["peak"] - b_kwh["peak"]) / b_kwh["peak"] * 100 if b_kwh["peak"] else 0.0
            valley_delta = (p_kwh["valley"] - b_kwh["valley"]) / b_kwh["valley"] * 100 if b_kwh["valley"] else 0.0
            rows.append((f"{record['house_id']}/{member}", b_min, b_kwh, p_min, p_kwh,
                         peak_delta, valley_delta))

    if not rows:
        print(f"No '{args.tag}' policy s4 decisions found for {args.world}/{date} "
              f"(run the simulation with --policy {args.tag} first)")
        sys.exit(1)

    header = ("member |" + " |".join(f"{w}_min(base/pol)" for w in WINDOWS) +
              " |" + " |".join(f"{w}_kwh(base/pol)" for w in WINDOWS) +
              " | peak_delta% | valley_delta%")
    print(header)
    print("-" * len(header))
    for member, b_min, b_kwh, p_min, p_kwh, peak_delta, valley_delta in rows:
        cells = [member]
        for w in WINDOWS:
            cells.append(f"{b_min[w]:.0f}/{p_min[w]:.0f}")
        for w in WINDOWS:
            cells.append(f"{b_kwh[w]:.2f}/{p_kwh[w]:.2f}")
        cells.append(f"{peak_delta:+.1f}")
        cells.append(f"{valley_delta:+.1f}")
        print(" | ".join(cells))

    total_peak = sum(r[4]["peak"] - r[2]["peak"] for r in rows if r)
    total_valley = sum(r[4]["valley"] - r[2]["valley"] for r in rows if r)
    print(f"\n[Total] peak kWh delta: {total_peak:+.2f} | valley kWh delta: {total_valley:+.2f}")


if __name__ == "__main__":
    main()
