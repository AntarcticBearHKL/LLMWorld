












import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulation_env import sim_root


def load_profile(world_id, scenario, date):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(sim_root(world_id), "population",
                        scenario, date, "population_profile_1440min.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def combine(world_ids, scenario, date):

    profiles = []
    for wid in world_ids:
        p = load_profile(wid, scenario, date)
        if p is None:
            print(f"[跳过] {wid} 无 {scenario}/{date} 曲线")
            continue
        profiles.append((wid, p))

    if not profiles:
        raise ValueError("没有可合并的曲线")

    n = len(profiles[0][1].get("load_profile_watts", []))
    total_watts = [0.0] * n
    per_house = []
    total_kwh = 0.0

    for wid, p in profiles:
        watts = p["load_profile_watts"]
        for i in range(n):
            total_watts[i] += watts[i]
        total_kwh += p["total_energy_kwh"]
        for h in p.get("per_house", []):
            per_house.append({**h, "house_id": f"{wid}:{h['house_id']}"})

    peak_min = max(range(n), key=lambda m: total_watts[m])
    kwhs = [h["total_energy_kwh"] for h in per_house]
    count = len(kwhs)
    mean = sum(kwhs) / count if count else 0
    kwhs_sorted = sorted(kwhs)
    median = kwhs_sorted[count // 2] if count else 0

    return {
        "worlds": world_ids,
        "households": count,
        "total_energy_kwh": round(total_kwh, 4),
        "mean_household_kwh": round(mean, 4),
        "median_household_kwh": round(median, 4),
        "peak_watts": round(total_watts[peak_min], 2),
        "peak_time": f"{peak_min // 60:02d}:{peak_min % 60:02d}",
        "load_profile_watts": [round(w, 2) for w in total_watts],
        "hourly_average_watts": [
            round(sum(total_watts[h * 60:(h + 1) * 60]) / 60.0, 2)
            for h in range(24)
        ],
        "per_house": per_house,
        "scenario": scenario,
        "date": date,
    }


def main():
    parser = argparse.ArgumentParser(description="多世界联合聚合（0 token）")
    parser.add_argument("--worlds", nargs="+", required=True, help="世界ID列表，如 pop02 pop03")
    parser.add_argument("--scenario", default="baseline")
    parser.add_argument("--date", default="2026-04-21")
    args = parser.parse_args()

    data = combine(args.worlds, args.scenario, args.date)

    name = "combined_" + "+".join(args.worlds)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(sim_root(name), "population",
                           args.scenario, args.date)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "population_profile_1440min.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"联合人口 {name}：{data['households']} 户")
    print(f"  总用电 {data['total_energy_kwh']} kWh | 户均 {data['mean_household_kwh']} | "
          f"中位 {data['median_household_kwh']} | 峰值 {data['peak_watts']}W @ {data['peak_time']}")
    print(f"  已保存: {out_path}")


if __name__ == "__main__":
    main()
