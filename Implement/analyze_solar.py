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


def build_report(profiles, capacity, season):
    if not profiles:
        raise ValueError("没有找到任何模拟曲线")
    rows = []
    for p in profiles:
        gen = solar_generation_curve(season, p.get("weather", "晴天"), capacity)
        load = p["load_profile_watts"]
        net = [max(0.0, load[m] - gen[m]) for m in range(1440)]
        min_load_gen = sum(min(load[m], gen[m]) for m in range(1440))
        total_gen = sum(gen)
        total_load = sum(load)
        self_consumption = min_load_gen / total_gen if total_gen else 0.0
        coverage = min_load_gen / total_load if total_load else 0.0
        rows.append({
            "house_id": p["house_id"],
            "total_load_kwh": round(total_load / 60000, 4),
            "solar_gen_kwh": round(total_gen / 60000, 4),
            "self_consumption_rate": round(self_consumption, 4),
            "solar_coverage": round(coverage, 4),
            "grid_import_kwh": round(sum(net) / 60000, 4),
            "grid_export_kwh": round(max(0.0, total_gen - min_load_gen) / 60000, 4),
            "net_peak_watts": round(max(net), 2),
        })
    mean_self = sum(r["self_consumption_rate"] for r in rows) / len(rows)
    mean_coverage = sum(r["solar_coverage"] for r in rows) / len(rows)
    return {
        "households": len(rows),
        "capacity_kw": capacity / 1000.0,
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
    report = build_report(profiles, args.capacity * 1000.0, season)
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
          f"{report['capacity_kw']}kW，{report['season']}季）")
    print(f"  平均自用率 {report['mean_self_consumption_rate']}，"
          f"平均覆盖占比 {report['mean_solar_coverage']}")
    for r in report["per_house"]:
        print(f"  {r['house_id']}: 发电 {r['solar_gen_kwh']}kWh "
              f"自用率 {r['self_consumption_rate']} 覆盖 {r['solar_coverage']}")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
