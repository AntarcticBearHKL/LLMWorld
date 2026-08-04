"""人口级并行模拟器：多家庭逐日并行模拟 + 人口级负荷聚合。

用法（先构建人口）：
    python Implement/population.py pop01 --count 4
    python Implement/population_runner.py pop01 --days 1

输出：
    outputs/<world_id>/population/<日期>/population_profile_1440min.json
    - 人口级 1440 分钟总负荷（所有家庭之和）
    - 群体统计：总 kWh、户均、分散度、峰值、逐户明细
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import World, utils
from simulate import load_world, create_home_from_household
import config

MAX_HOUSEHOLDS_PARALLEL = 5   # 同时模拟的家庭数（每户每阶段并发受 SubAgent 全局信号量 ≤10 约束）


def aggregate_population(house_results):
    """把多户的日结果聚合成人口级负荷曲线与统计。"""
    total_profile = [0.0] * 1440
    per_house = []

    for house_id, day_result in house_results:
        calculator = day_result["energy_calculator"]
        profile = calculator.household_load_watts
        total_kwh = day_result["energy_summary"]["total_energy_kwh"]

        for m in range(1440):
            total_profile[m] += profile[m]

        peak_minute = max(range(1440), key=lambda m: profile[m])
        per_house.append({
            "house_id": house_id,
            "total_energy_kwh": round(total_kwh, 4),
            "peak_watts": round(profile[peak_minute], 2),
            "peak_time": f"{peak_minute // 60:02d}:{peak_minute % 60:02d}",
        })

    peak_minute = max(range(1440), key=lambda m: total_profile[m])
    kwhs = [h["total_energy_kwh"] for h in per_house]
    n = len(kwhs)
    mean = sum(kwhs) / n if n else 0
    std = (sum((k - mean) ** 2 for k in kwhs) / n) ** 0.5 if n else 0
    kwhs_sorted = sorted(kwhs)
    median = kwhs_sorted[n // 2] if n else 0

    return {
        "households": n,
        "total_energy_kwh": round(sum(kwhs), 4),
        "mean_household_kwh": round(mean, 4),
        "median_household_kwh": round(median, 4),
        "std_household_kwh": round(std, 4),
        "peak_watts": round(total_profile[peak_minute], 2),
        "peak_time": f"{peak_minute // 60:02d}:{peak_minute % 60:02d}",
        "load_profile_watts": [round(w, 2) for w in total_profile],
        "hourly_average_watts": [
            round(sum(total_profile[h * 60:(h + 1) * 60]) / 60.0, 2)
            for h in range(24)
        ],
        "per_house": per_house,
    }


def main_aggregate_only(args, project_root, pop_root):
    """离线聚合：从各户已保存的 house_load_profile_1440min.json 重建人口曲线（不花 token）。"""
    from simulate import load_world
    world_meta, district_info, households = load_world(args.world_id)
    postcode = district_info["postcode"]

    class _ProfileSource:
        def __init__(self, watts):
            self.household_load_watts = watts

    outputs_root = os.path.join(project_root, "outputs", args.world_id, postcode)
    house_results = []
    for info in households:
        house_id = info["house_id"]
        house_dir = os.path.join(outputs_root, house_id)
        if not os.path.isdir(house_dir):
            continue
        date_dirs = sorted(d for d in os.listdir(house_dir)
                           if os.path.isdir(os.path.join(house_dir, d)))
        if not date_dirs:
            continue
        profile_path = os.path.join(house_dir, date_dirs[-1], "用电信息",
                                    "house_load_profile_1440min.json")
        if not os.path.exists(profile_path):
            continue
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        house_results.append((house_id, {
            "energy_calculator": _ProfileSource(profile["load_profile_watts"]),
            "energy_summary": {"total_energy_kwh": profile["total_energy_kwh"]},
        }))

    if not house_results:
        print("没有找到任何已保存的模拟结果，请先运行模拟")
        sys.exit(1)

    population = aggregate_population(house_results)
    os.makedirs(pop_root, exist_ok=True)
    out_path = os.path.join(pop_root, "aggregate_only.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(population, f, ensure_ascii=False, indent=2)

    print(f"离线聚合完成（{len(house_results)} 户，0 token）")
    print(f"  人口总用电 {population['total_energy_kwh']} kWh"
          f"（户均 {population['mean_household_kwh']}，中位 {population['median_household_kwh']}，"
          f"标准差 {population['std_household_kwh']}）")
    print(f"  人口峰值 {population['peak_watts']} W @ {population['peak_time']}")
    for h in population["per_house"]:
        print(f"    - {h['house_id']}: {h['total_energy_kwh']} kWh, 峰值 {h['peak_watts']}W@{h['peak_time']}")
    print(f"  已保存: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="人口级并行模拟")
    parser.add_argument("world_id", help="世界ID")
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--date", type=str, default=config.DEFAULT_START_DATE)
    parser.add_argument("--house-start", type=int, default=0, help="起始家庭序号")
    parser.add_argument("--house-count", type=int, default=None, help="参与家庭数（默认全部）")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    parser.add_argument("--aggregate-only", action="store_true",
                        help="不跑 LLM，直接从已保存的 outputs 曲线文件离线聚合")
    args = parser.parse_args()

    utils.set_seed(args.seed)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pop_root = os.path.join(project_root, "outputs", args.world_id, "population")

    if args.aggregate_only:
        main_aggregate_only(args, project_root, pop_root)
        return

    world_meta, district_info, households = load_world(args.world_id)
    selected = households[args.house_start:]
    if args.house_count:
        selected = selected[:args.house_count]

    print(f"人口模拟：{len(selected)} 户 × {args.days} 天（world {args.world_id}）")
    location = district_info["location"]
    postcode = district_info["postcode"]

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pop_root = os.path.join(project_root, "outputs", args.world_id, "population")

    # 每户一个 World（含各自跨天记忆）
    worlds = {}
    homes = {}
    for info in selected:
        household = info["household"]
        home = create_home_from_household(household)
        homes[info["house_id"]] = home
        worlds[info["house_id"]] = World(
            home, world_id=args.world_id, postcode=postcode,
            house_id=info["house_id"], start_date=args.date)

    for day in range(args.days):
        print(f"\n=== 第 {day + 1}/{args.days} 天 ===")

        def run_one(item):
            house_id, world = item
            # 季节从 household 配置读
            household = next(h for h in selected if h["house_id"] == house_id)["household"]
            season = household.get("season", config.DEFAULT_SEASON)
            day_result = world.simulate_day(
                season=season,
                weather=config.DEFAULT_WEATHER,
                temperature=config.DEFAULT_TEMPERATURE,
                verbose=False)
            return house_id, day_result

        with ThreadPoolExecutor(max_workers=MAX_HOUSEHOLDS_PARALLEL) as executor:
            house_results = list(executor.map(run_one, worlds.items()))

        # 聚合
        population = aggregate_population(house_results)

        date_str = house_results[0][1]["date"].replace("年", "-").replace("月", "-").replace("日", "")
        out_dir = os.path.join(pop_root, date_str)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "population_profile_1440min.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(population, f, ensure_ascii=False, indent=2)

        print(f"  人口总用电 {population['total_energy_kwh']} kWh"
              f"（户均 {population['mean_household_kwh']}，中位 {population['median_household_kwh']}，"
              f"标准差 {population['std_household_kwh']}）")
        print(f"  人口峰值 {population['peak_watts']} W @ {population['peak_time']}")
        print(f"  已保存: {out_path}")

        # 每日汇总每户
        for h in population["per_house"]:
            print(f"    - {h['house_id']}: {h['total_energy_kwh']} kWh, 峰值 {h['peak_watts']}W@{h['peak_time']}")

        # 校验警告汇总
        for house_id, day_result in house_results:
            executor_obj = day_result["executor"]
            if executor_obj and executor_obj.validation_warnings:
                print(f"  [警告] {house_id} {len(executor_obj.validation_warnings)} 条决策校验问题")

        if day < args.days - 1:
            for world in worlds.values():
                world.next_day()

    # Token 汇总
    tokens = next(iter(worlds.values())).get_total_tokens()
    print(f"\n=== Token 账单（{args.days} 天 × {len(worlds)} 户）===")
    print(f"  缓存未命中 {tokens['prompt_cache_miss']} + 缓存命中 {tokens['prompt_cache_hit']} + 输出 {tokens['completion']} = {tokens['total']}")
    print(f"  户均/天 ≈ {tokens['total'] / (args.days * len(worlds)):.0f} tokens")
    print("\n人口模拟完成")


if __name__ == "__main__":
    main()
