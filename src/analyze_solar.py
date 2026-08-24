import argparse
import json
import math
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulation_env import sim_root

from load_profile_cluster import scan_house_profiles
from engine import utils

WEATHER_FACTOR = {"Sunny": 1.0, "Heatwave": 1.0, "Cloudy": 0.6,
                  "Overcast": 0.3, "Shower": 0.15, "Rainy": 0.15}

SEASON_SUN = {
    "Summer": (6.5, 20.5, 1.0),
    "Spring": (6.5, 18.5, 0.9),
    "Autumn": (7.0, 18.0, 0.85),
    "Winter": (7.5, 17.0, 0.7),
}


def solar_generation_curve(season, weather, capacity=5000):
    sunrise, sunset, season_factor = SEASON_SUN.get(season, SEASON_SUN["Spring"])
    weather_factor = WEATHER_FACTOR.get(weather, 0.6)
    curve = []
    for m in range(1440):
        h = m / 60.0
        if h < sunrise or h > sunset:
            curve.append(0.0)
            continue
        phase = math.pi * (h - sunrise) / (sunset - sunrise)
        watts = capacity * season_factor * weather_factor * math.sin(phase)
        if watts < 1.0:
            watts = 0.0
        curve.append(max(0.0, watts))
    return curve


def battery_operation(load, gen, capacity_kwh, power_kw):
    battery_wh = 0.0
    charge_curve = [0.0] * 1440
    discharge_curve = [0.0] * 1440
    peak_window = (17 * 60, 22 * 60)
    for m in range(1440):
        surplus = gen[m] - load[m]
        if surplus > 0 and battery_wh < capacity_kwh * 1000:
            charge = min(surplus, power_kw * 1000,
                         capacity_kwh * 1000 - battery_wh)
            battery_wh += charge
            charge_curve[m] = charge
        elif surplus < 0 and battery_wh > 0 and peak_window[0] <= m < peak_window[1]:
            discharge = min(-surplus, power_kw * 1000, battery_wh)
            battery_wh -= discharge
            discharge_curve[m] = discharge
    return charge_curve, discharge_curve


def build_report(profiles, capacity, season, battery_kwh=0.0, battery_power_kw=3.0):
    if not profiles:
        raise ValueError("No simulation curves found")
    rows = []
    for p in profiles:
        gen = solar_generation_curve(season, p.get("weather", "Sunny"), capacity)
        load = p["load_profile_watts"]
        charge_curve, discharge_curve = battery_operation(
            load, gen, battery_kwh, battery_power_kw)
        net = [max(0.0, load[m] - gen[m] + charge_curve[m] - discharge_curve[m])
               for m in range(1440)]
        min_load_gen = sum(min(load[m], gen[m]) for m in range(1440))
        total_gen = sum(gen)
        total_load = sum(load)
        battery_used = sum(discharge_curve)
        self_consumption = (min_load_gen + battery_used) / total_gen if total_gen else 0.0
        coverage = min_load_gen / total_load if total_load else 0.0
        night_window = (17 * 60, 22 * 60)
        peak_import_no_battery = sum(max(0.0, load[m] - gen[m])
                                     for m in range(night_window[0], night_window[1]))
        peak_import_with_battery = sum(net[m]
                                       for m in range(night_window[0], night_window[1]))
        rows.append({
            "house_id": p["house_id"],
            "total_load_kwh": round(total_load / 60000, 4),
            "solar_gen_kwh": round(total_gen / 60000, 4),
            "self_consumption_rate": round(self_consumption, 4),
            "solar_coverage": round(coverage, 4),
            "grid_import_kwh": round(sum(net) / 60000, 4),
            "grid_export_kwh": round(max(0.0, total_gen - min_load_gen) / 60000, 4),
            "battery_cycle_kwh": round(sum(discharge_curve) / 60000, 4),
            "peak_import_cut_pct": round(
                (peak_import_with_battery / peak_import_no_battery - 1) * 100, 2)
                if peak_import_no_battery else None,
            "net_peak_watts": round(max(net), 2),
        })
    mean_self = sum(r["self_consumption_rate"] for r in rows) / len(rows)
    mean_coverage = sum(r["solar_coverage"] for r in rows) / len(rows)
    return {
        "households": len(rows),
        "capacity_kw": capacity / 1000.0,
        "battery_kwh": battery_kwh,
        "season": season,
        "mean_self_consumption_rate": round(mean_self, 4),
        "mean_solar_coverage": round(mean_coverage, 4),
        "per_house": rows,
    }


def main():
    parser = argparse.ArgumentParser(description="Photovoltaic self-consumption analysis (prosumer)")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to the last day per household")
    parser.add_argument("--capacity", type=float, default=5.0, help="PV capacity in kW (default 5)")
    parser.add_argument("--battery", type=float, default=0.0, help="Battery capacity in kWh (default 0 = none)")
    parser.add_argument("--battery-power", type=float, default=3.0, help="Battery power in kW (default 3)")
    parser.add_argument("--weather", default=None, help="Weather (default automatic: read from aggregated environment or default to Sunny)")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    profiles = scan_house_profiles(args.world_id, args.scenario, args.date)
    season = None
    if args.date:
        season = utils.season_for_date(args.date)
    if not season:
        season = "Summer"
    weather = args.weather or "Sunny"
    for p in profiles:
        p["weather"] = weather
    report = build_report(profiles, args.capacity * 1000.0, season,
                          args.battery, args.battery_power)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    report["date"] = args.date or "latest"

    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        date_tag = args.date.replace("-", "") if args.date else "latest"
        args.out = os.path.join(out_dir,
                                f"solar_{args.scenario}_{date_tag}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"PV self-consumption analysis done ({report['households']} households, "
          f"{report['capacity_kw']}kW"
          f"{('+battery ' + str(report['battery_kwh']) + 'kWh') if report['battery_kwh'] else ''}"
          f", {report['season']} season)")
    print(f"  mean self-consumption rate {report['mean_self_consumption_rate']}, "
          f"mean solar coverage {report['mean_solar_coverage']}")
    for r in report["per_house"]:
        battery_note = (f"  battery cycle {r['battery_cycle_kwh']}kWh "
                        f"evening peak cut {r['peak_import_cut_pct']}%") \
                        if report['battery_kwh'] else ""
        print(f"  {r['house_id']}: generation {r['solar_gen_kwh']}kWh "
              f"self-consumption rate {r['self_consumption_rate']} coverage {r['solar_coverage']}"
              f"{battery_note}")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
