import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root
from dataset import iter_house_days, list_dates
from simulate import create_home_from_household


def load_true_appliances(record):
    home = create_home_from_household(record.get("household", {}))
    per_appliance_kwh = record.get("per_appliance_kwh", {})
    appliances = []
    for unique_id, appliance in home.appliance_registry.items():
        appliances.append({
            "unique_id": unique_id,
            "name": appliance.name,
            "power_watts": appliance.power_watts,
            "total_energy_kwh": per_appliance_kwh.get(unique_id, 0.0),
        })
    return appliances


def find_plateaus(load_watts, min_minutes=10, tolerance=0.05):
    plateaus = []
    start = None
    ref = None
    for m, w in enumerate(load_watts):
        if w <= 0:
            if start is not None:
                if m - start >= min_minutes:
                    plateaus.append({"start": start, "end": m - 1,
                                     "watts": ref})
                start = None
            continue
        if start is None:
            start = m
            ref = w
        elif abs(w - ref) / ref > tolerance:
            if m - start >= min_minutes:
                plateaus.append({"start": start, "end": m - 1, "watts": ref})
            start = m
            ref = w
    if start is not None and len(load_watts) - start >= min_minutes:
        plateaus.append({"start": start, "end": len(load_watts) - 1,
                         "watts": ref})
    return plateaus


def match_appliances(plateaus, appliances):
    estimates = {}
    for p in plateaus:
        best = None
        for a in appliances:
            if a["power_watts"] <= 0:
                continue
            if abs(p["watts"] - a["power_watts"]) / a["power_watts"] <= 0.1:
                if best is None or abs(p["watts"] - a["power_watts"]) < \
                        abs(p["watts"] - best["power_watts"]):
                    best = a
        if best is not None:
            duration_min = p["end"] - p["start"] + 1
            key = best["unique_id"]
            estimates[key] = estimates.get(key, 0.0) + \
                best["power_watts"] * duration_min / 60000.0
    return estimates


def build_report(load_watts, appliances):
    if not appliances:
        raise ValueError("No appliance ground-truth data found")
    plateaus = find_plateaus(load_watts)
    estimates = match_appliances(plateaus, appliances)
    rows = []
    total_mae = 0.0
    for a in appliances:
        est = estimates.get(a["unique_id"], 0.0)
        true_kwh = a["total_energy_kwh"]
        mae = abs(est - true_kwh)
        total_mae += mae
        rows.append({
            "name": a["name"],
            "power_watts": a["power_watts"],
            "true_kwh": round(true_kwh, 4),
            "estimated_kwh": round(est, 4),
            "mae_kwh": round(mae, 4),
            "relative_error": round(mae / true_kwh, 4) if true_kwh else None,
        })
    total_true = sum(a["total_energy_kwh"] for a in appliances)
    return {
        "households": 1,
        "total_true_kwh": round(total_true, 4),
        "total_estimated_kwh": round(sum(estimates.values()), 4),
        "total_mae_kwh": round(total_mae, 4),
        "disaggregation_rate": round(sum(estimates.values()) / total_true, 4)
        if total_true else None,
        "per_appliance": rows,
    }


def main():
    parser = argparse.ArgumentParser(description="NILM load disaggregation benchmark")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to the last day")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    if not args.date:
        dates = list_dates(args.world_id)
        args.date = dates[-1] if dates else None

    reports = []
    for record in iter_house_days(args.world_id, date=args.date, policy=args.scenario):
        appliances = load_true_appliances(record)
        try:
            report = build_report(record["load_profile_watts"], appliances)
        except ValueError as exc:
            print(f"Skipping {record['house_id']}: {exc}")
            continue
        report["house_id"] = record["house_id"]
        reports.append(report)

    if not reports:
        print(f"No disaggregatable household data found for {args.world_id}")
        sys.exit(1)
    report = {
        "world_id": args.world_id,
        "scenario": args.scenario,
        "date": args.date or "latest",
        "households": len(reports),
        "per_house": reports,
    }
    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        date_tag = args.date.replace("-", "") if args.date else "latest"
        args.out = os.path.join(out_dir, f"nilm_{args.scenario}_{date_tag}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"NILM disaggregation benchmark done ({len(reports)} households)")
    for r in reports:
        print(f"  {r['house_id']}: disaggregation rate {r['disaggregation_rate']}, "
              f"total MAE {r['total_mae_kwh']}kWh")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
