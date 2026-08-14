import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_nilm import load_true_appliances


def scan_house_dirs(world_id, scenario, date_str):
    simulation_root = os.path.join(PROJECT_ROOT, "simulation", world_id)
    house_dirs = []
    if not os.path.isdir(simulation_root):
        return house_dirs
    for postcode_dir in sorted(os.listdir(simulation_root)):
        postcode_path = os.path.join(simulation_root, postcode_dir)
        if not os.path.isdir(postcode_path) or postcode_dir == "population":
            continue
        for house_id in sorted(os.listdir(postcode_path)):
            scenario_dir = os.path.join(postcode_path, house_id, scenario)
            if not os.path.isdir(scenario_dir):
                continue
            date_dirs = [d for d in sorted(os.listdir(scenario_dir))
                         if os.path.isdir(os.path.join(scenario_dir, d))]
            if date_str:
                date_dirs = [d for d in date_dirs
                             if d == date_str.replace("-", "")]
            if date_dirs:
                house_dirs.append((house_id,
                                   os.path.join(scenario_dir, date_dirs[-1])))
    return house_dirs


def build_report(world_id, scenario, date_str):
    house_dirs = scan_house_dirs(world_id, scenario, date_str)
    if not house_dirs:
        raise ValueError("没有找到任何户数据")
    appliance_totals = {}
    per_house = []
    for house_id, house_dir in house_dirs:
        appliances = load_true_appliances(house_dir)
        if not appliances:
            continue
        total_kwh = sum(a["total_energy_kwh"] for a in appliances)
        top = max(appliances, key=lambda a: a["total_energy_kwh"]) if appliances else None
        per_house.append({
            "house_id": house_id,
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
        raise ValueError("没有找到任何电器数据")
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
    parser = argparse.ArgumentParser(description="电器使用画像分析")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD，缺省取最后一天")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    report = build_report(args.world_id, args.scenario, args.date)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    report["date"] = args.date or "latest"

    if not args.out:
        out_dir = os.path.join(PROJECT_ROOT, "simulation", args.world_id,
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        date_tag = args.date.replace("-", "") if args.date else "latest"
        args.out = os.path.join(out_dir,
                                f"appliance_usage_{args.scenario}_{date_tag}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"电器使用画像完成（{report['households']} 户，"
          f"总电 {report['grand_total_kwh']}kWh）")
    for r in report["ranking"][:10]:
        print(f"  {r['name']}: {r['total_kwh']}kWh "
              f"({r['share_pct']}%, {r['households']} 户)")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
