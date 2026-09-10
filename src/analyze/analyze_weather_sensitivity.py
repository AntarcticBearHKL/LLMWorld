import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from simulation_env import sim_root
from dataset import list_dates, population_profile
from engine.weather import get_weather


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
    points = []
    for date in list_dates(world_id):
        profile = population_profile(world_id, scenario, date)
        if not profile.get("per_house"):
            continue
        weather = get_weather(date)
        temperature = weather.get("temperature")
        if temperature is None:
            continue
        condition = weather.get("weather")
        points.append({
            "date": date,
            "temperature": float(temperature),
            "kwh": profile.get("total_energy_kwh"),
            "conditions": {condition} if condition else set(),
        })
    return points


def build_report(points):
    if not points:
        raise ValueError("No multi-day aggregated data found")
    temps = [p["temperature"] for p in points]
    kwhs = [p["kwh"] for p in points if p["kwh"] is not None]
    valid = [(p["temperature"], p["kwh"]) for p in points
             if p["kwh"] is not None]
    corr = pearson([v[0] for v in valid], [v[1] for v in valid])
    slope = linear_slope([v[0] for v in valid], [v[1] for v in valid])
    by_weather = {}
    for p in points:
        for c in p["conditions"] or {"Unknown"}:
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
    parser = argparse.ArgumentParser(description="Weather sensitivity analysis")
    parser.add_argument("world_id")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    points = load_daily_points(args.world_id, args.scenario)
    try:
        report = build_report(points)
    except ValueError as exc:
        print(f"[Error] {exc}")
        sys.exit(1)
    report["world_id"] = args.world_id
    report["scenario"] = args.scenario

    if not args.out:
        out_dir = os.path.join(sim_root(args.world_id),
                               "analysis")
        os.makedirs(out_dir, exist_ok=True)
        args.out = os.path.join(out_dir, f"weather_{args.scenario}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Weather sensitivity analysis done ({report['days']} days, "
          f"temperature {report['temp_min']}-{report['temp_max']} C)")
    print(f"  temperature-energy correlation {report['temperature_kwh_corr']}, "
          f"slope {report['kwh_per_degree']} kWh/C")
    for w in report["by_weather"]:
        print(f"  {w['condition']}: {w['samples']} days, mean energy {w['mean_kwh']}kWh")
    print(f"  Saved: {args.out}")


if __name__ == "__main__":
    main()
