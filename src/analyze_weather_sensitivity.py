import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def pearson(a, b):
    n = len(a)
    if n < 2:
        return None
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    cov = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    var_a = sum((x - mean_a) ** 2 for x in a)
    var_b = sum((y - mean_b) ** 2 for y in b)
    if var_a <= 0 or var_b <= 0:
        return None
    return round(cov / (var_a * var_b) ** 0.5, 4)


def linear_slope(a, b):
    n = len(a)
    if n < 2:
        return None
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    var_a = sum((x - mean_a) ** 2 for x in a)
    if var_a <= 0:
        return None
    cov = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    return round(cov / var_a, 4)


def load_daily_points(world_id, scenario):
    pop_dir = os.path.join(PROJECT_ROOT, "simulation", world_id, "population",
                           scenario)
    points = []
    if not os.path.isdir(pop_dir):
        return points
    for date_dir in sorted(os.listdir(pop_dir)):
        path = os.path.join(pop_dir, date_dir,
                            "population_profile_1440min.json")
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        env = data.get("environment") or {}
        temps = [v.get("temperature") for v in env.values()
                 if isinstance(v, dict) and v.get("temperature") is not None]
        if not temps:
            continue
        points.append({
            "date": date_dir,
            "temperature": sum(temps) / len(temps),
            "kwh": data.get("total_energy_kwh"),
            "conditions": {v.get("condition") for v in env.values()
                           if isinstance(v, dict) and v.get("condition")},
        })
    return points


def build_report(points):
    if not points:
        raise ValueError("没有找到任何多日聚合数据")
    temps = [p["temperature"] for p in points]
    kwhs = [p["kwh"] for p in points if p["kwh"] is not None]
    valid = [(p["temperature"], p["kwh"]) for p in points
             if p["kwh"] is not None]
    corr = pearson([v[0] for v in valid], [v[1] for v in valid])
    slope = linear_slope([v[0] for v in valid], [v[1] for v in valid])
    by_weather = {}
    for p in points:
        for c in p["conditions"] or {"未知"}:
            by_weather.setdefault(c, []).append(p["kwh"])
    weather_rows = []
    for condition, values in sorted(by_weather.items()):
        values = [v for v in values if v is not None]
        if values:
            weather_rows.append({
                "condition": condition,
                "samples": len(values),
                "mean_kwh": round(sum(values) / len(values), 4),
            })
    return {
        "days": len(points),
        "temp_min": round(min(temps), 2),
        "temp_max": round(max(temps), 2),
        "temperature_kwh_corr": corr,
        "kwh_per_degree": slope,
        "by_weather": weather_rows,
    }


def main():
    parser = argparse.ArgumentParser(description="天气敏感性分析")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    points = load_daily_points(args.world_id, args.scenario)
    report = build_report(points)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario

    if not args.out:
        out_dir = os.path.join(PROJECT_ROOT, "simulation", args.world_id,
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, f"weather_{args.scenario}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"天气敏感性分析完成（{report['days']} 天，"
          f"温度 {report['temp_min']}-{report['temp_max']}°C）")
    print(f"  温度-用电相关 {report['temperature_kwh_corr']}，"
          f"斜率 {report['kwh_per_degree']} kWh/°C")
    for w in report["by_weather"]:
        print(f"  {w['condition']}: {w['samples']} 天, 均电 {w['mean_kwh']}kWh")
    print(f"  已保存: {args.out}")


if __name__ == "__main__":
    main()
