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


def appliance_name_map(household):
    home = create_home_from_household(household)
    names = {}
    for unique_id, appliance in home.appliance_registry.items():
        names[unique_id] = getattr(appliance, "name", None) or unique_id
    return names


def scan_house_records(world_id, scenario, date_str):
    dates = list_dates(world_id)
    if date_str:
        date = date_str
    elif dates:
        date = dates[-1]
    else:
        return []
    return list(iter_house_days(world_id, date=date, policy=scenario))


def build_report(world_id, scenario, date_str):
    records = scan_house_records(world_id, scenario, date_str)
    if not records:
        raise ValueError("No household data found")
    appliance_totals = {}
    per_house = []
    for record in records:
        names = appliance_name_map(record["household"])
        appliances = [{"name": names.get(unique_id, unique_id),
                       "total_energy_kwh": kwh}
                      for unique_id, kwh in record["per_appliance_kwh"].items()]
        if not appliances:
            continue
        total_kwh = sum(a["total_energy_kwh"] for a in appliances)
        top = max(appliances, key=lambda a: a["total_energy_kwh"]) if appliances else None
        per_house.append({
            "house_id": record["house_id"],
            "appliance_count": len(appliances),
            "total_kwh": round(total_kwh, 4),
            "top_appliance": top["name"] if top else None,
        })
        for a in appliances:
            entry = appliance_totals.setdefault(a["name"], {
                "name": a["name"], "total_kwh": 0.0, "households": 0})
            entry["total_kwh"] += a["total_energy_kwh"]
            entry["households"] += 1
    if not per_house:
        raise ValueError("No appliance data found")
    grand_total = sum(e["total_kwh"] for e in appliance_totals.values())
    ranking = []
    for name, entry in appliance_totals.items():
        ranking.append({
            "name": name,
            "total_kwh": round(entry["total_kwh"], 4),
            "share_pct": round(entry["total_kwh"] / grand_total * 100, 2)
            if grand_total else 0.0,
            "households": entry["households"],
        })
    ranking.sort(key=lambda r: -r["total_kwh"])
    return {
        "households": len(per_house),
        "grand_total_kwh": round(grand_total, 4),
        "ranking": ranking,
        "per_house": per_house,
    }


def main():
    parser = argparse.ArgumentParser(description="Appliance usage profiling analysis")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to the last day")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    try:
        report = build_report(args.world_id, args.scenario, args.date)
    except ValueError as exc:
        print(f"[Error] {exc}")
        sys.exit(1)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    report["date"] = args.date or "latest"

    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        date_tag = args.date.replace("-", "") if args.date else "latest"
        args.out = os.path.join(out_dir,
                                f"appliance_usage_{args.scenario}_{date_tag}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Appliance usage profiling done ({report['households']} households, "
          f"total {report['grand_total_kwh']}kWh）")
    for r in report["ranking"][:10]:
        print(f"  {r['name']}: {r['total_kwh']}kWh "
              f"({r['share_pct']}%, {r['households']} households)")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
