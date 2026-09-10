import argparse
from simulation_env import sim_root
from dataset import (list_dates, list_houses, discover_policy_tags,
                     population_profile)
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PEAK_HOURS = (16, 21)


def energy_of_hours(profile_watts, hours):
    start, end = hours
    total_wh = 0.0
    for h in range(24):
        if start <= h < end:
            total_wh += sum(profile_watts[h * 60:(h + 1) * 60]) / 60.0
    return total_wh / 1000.0


def peak_plateau_minutes(profile_watts, ratio=0.8):
    peak = max(profile_watts)
    if peak <= 0:
        return 0
    threshold = peak * ratio
    return sum(1 for w in profile_watts if w >= threshold)


def peak_to_mean_ratio(profile_watts):
    mean = sum(profile_watts) / len(profile_watts)
    peak = max(profile_watts)
    if mean <= 0:
        return None
    return round(peak / mean, 2)


def list_policies(world_id):
    policies = set()
    for date in list_dates(world_id):
        for house_id in list_houses(world_id, world_id, date):
            house_dir = os.path.join(sim_root(world_id), date, house_id)
            for tag in discover_policy_tags(house_dir):
                policies.add(tag)
    return sorted(policies)


def mean_profile(world_id, policy, dates):
    profile = [0.0] * 1440
    days = 0
    for date in dates:
        day_profile = population_profile(world_id, policy, date)
        if not day_profile.get("per_house"):
            continue
        days += 1
        for minute in range(1440):
            profile[minute] += day_profile["load_profile_watts"][minute]
    if not days:
        return None
    return [watts / days for watts in profile]


def _change_pct(value, base):
    if base:
        return round((value / base - 1) * 100, 2)
    return None


def build_report(world_id):
    dates = list_dates(world_id)
    if not dates:
        raise ValueError("No simulation data found")
    base_profile = mean_profile(world_id, "baseline", dates)
    if base_profile is None:
        raise ValueError("No baseline data found")
    base_total = sum(base_profile)
    base_peak_kwh = energy_of_hours(base_profile, PEAK_HOURS)
    base_peak = max(base_profile)
    base_plateau = peak_plateau_minutes(base_profile)

    rows = [{
        "scenario": "baseline",
        "total_change_pct": None,
        "peak_hours_change_pct": None,
        "peak_load_cut_pct": None,
        "peak_plateau_cut_pct": None,
        "peak_to_mean": peak_to_mean_ratio(base_profile),
    }]
    for policy in list_policies(world_id):
        profile = mean_profile(world_id, policy, dates)
        if profile is None:
            continue
        rows.append({
            "scenario": policy,
            "total_change_pct": _change_pct(sum(profile), base_total),
            "peak_hours_change_pct": _change_pct(energy_of_hours(profile, PEAK_HOURS),
                                                 base_peak_kwh),
            "peak_load_cut_pct": _change_pct(max(profile), base_peak),
            "peak_plateau_cut_pct": _change_pct(peak_plateau_minutes(profile),
                                                base_plateau),
            "peak_to_mean": peak_to_mean_ratio(profile),
        })
    return {"scenarios": rows}


def main():
    parser = argparse.ArgumentParser(description="Policy tradeoff analysis (multi-objective)")
    parser.add_argument("world_id")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    try:
        report = build_report(args.world_id)
    except ValueError as exc:
        print(f"[Error] {exc}")
        sys.exit(1)
    report["world_id"] = args.world_id
    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, "policy_tradeoffs.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("Policy tradeoff matrix (% is vs baseline; more negative is better)")
    print(f"{'Policy':<14}{'Total':<10}{'Peak hrs':<10}{'Peak':<10}{'Plateau':<10}{'P/M':<8}")
    for r in report["scenarios"]:
        fmt = lambda v: f"{v:+.1f}%" if v is not None else "-"
        print(f"{r['scenario']:<14}{fmt(r['total_change_pct']):<10}"
              f"{fmt(r['peak_hours_change_pct']):<10}"
              f"{fmt(r['peak_load_cut_pct']):<10}"
              f"{fmt(r['peak_plateau_cut_pct']):<10}"
              f"{str(r['peak_to_mean']):<8}")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
