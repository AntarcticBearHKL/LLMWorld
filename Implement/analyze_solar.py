import argparse
import json
import math
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from load_profile_cluster import scan_house_profiles
from engine import utils

WEATHER_FACTOR = {"晴天": 1.0, "热浪": 1.0, "多云": 0.6,
                  "阴天": 0.3, "阵雨": 0.15, "雨天": 0.15}

SEASON_SUN = {
    "夏天": (6.5, 20.5, 1.0),
    "春天": (6.5, 18.5, 0.9),
    "秋天": (7.0, 18.0, 0.85),
    "冬天": (7.5, 17.0, 0.7),
}


def solar_generation_curve(season, weather, capacity=5000):
    sunrise, sunset, season_factor = SEASON_SUN.get(season, SEASON_SUN["春天"])
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
        raise ValueError("没有找到任何模拟曲线")
    rows = []
    for p in profiles:
        gen = solar_generation_curve(season, p.get("weather", "晴天"), capacity)
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
    parser = argparse.ArgumentParser(description="光伏自用分析（prosumer）")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD，缺省取每户最后一天")
    parser.add_argument("--capacity", type=float, default=5.0, help="光伏容量 kW（默认 5）")
    parser.add_argument("--battery", type=float, default=0.0, help="电池容量 kWh（默认 0=无）")
    parser.add_argument("--battery-power", type=float, default=3.0, help="电池功率 kW（默认 3）")
    parser.add_argument("--weather", default=None, help="天气（缺省自动：从聚合环境读取或默认晴天）")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    profiles = scan_house_profiles(args.world_id, args.scenario, args.date)
    season = None
    if args.date:
        season = utils.season_for_date(args.date)
    if not season:
        season = "夏天"
    weather = args.weather or "晴天"
    for p in profiles:
        p["weather"] = weather
    report = build_report(profiles, args.capacity * 1000.0, season,
                          args.battery, args.battery_power)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario
    report["date"] = args.date or "latest"

    if not args.out:
        out_dir = os.path.join(PROJECT_ROOT, "outputs", args.world_id,
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        date_tag = args.date.replace("-", "") if args.date else "latest"
        args.out = os.path.join(out_dir,
                                f"solar_{args.scenario}_{date_tag}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"光伏自用分析完成（{report['households']} 户，"
          f"{report['capacity_kw']}kW"
          f"{('+电池' + str(report['battery_kwh']) + 'kWh') if report['battery_kwh'] else ''}"
          f"，{report['season']}季）")
    print(f"  平均自用率 {report['mean_self_consumption_rate']}，"
          f"平均覆盖占比 {report['mean_solar_coverage']}")
    for r in report["per_house"]:
        battery_note = (f" 电池循环 {r['battery_cycle_kwh']}kWh "
                        f"晚峰削减 {r['peak_import_cut_pct']}%") \
                        if report['battery_kwh'] else ""
        print(f"  {r['house_id']}: 发电 {r['solar_gen_kwh']}kWh "
              f"自用率 {r['self_consumption_rate']} 覆盖 {r['solar_coverage']}"
              f"{battery_note}")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
