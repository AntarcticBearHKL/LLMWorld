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

from engine import World, utils, SubAgent
from simulate import load_world, create_home_from_household
import config

# 户级并行不设上限：并行多少户只取决于世界有多少家庭（用户 2026-08 指令）
# 世界级约束：每世界最多 10 户（见 population.py 校验）


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
        # 兼容两种目录结构：
        # 新：house_dir/<policy>/<date>/用电信息/...
        # 旧：house_dir/<date>/用电信息/...
        date_candidates = []
        for entry in os.listdir(house_dir):
            entry_path = os.path.join(house_dir, entry)
            if os.path.isdir(entry_path):
                sub = os.listdir(entry_path)
                if any(d.isdigit() and len(d) == 8 for d in sub):
                    date_candidates.extend(os.path.join(entry_path, d) for d in sub
                                           if d.isdigit() and len(d) == 8)
                elif entry.isdigit() and len(entry) == 8:
                    date_candidates.append(entry_path)
        if not date_candidates:
            continue
        date_candidates.sort()
        profile_path = os.path.join(date_candidates[-1], "用电信息",
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
    parser.add_argument("--policy", default=None,
                        help="政策干预（RQ2）：tou 分时电价 / subsidy 低谷补贴 / nudge 社会规范 / nudge_loss 损失框架")
    parser.add_argument("--event", action="append", default=None,
                        help="上帝注入的世界事件（可多次）：日期|标题|内容[|来源]，如 "
                        "'2026-04-21|政府宣布开征空调用电附加税|从今日起空调电价上调10%|政府公告'")
    parser.add_argument("--scenario", default=None,
                        help="场景标签（聚合输出目录名，默认=政策名或 baseline）。"
                        "新闻实验请用自定义名如 war_news，避免与基线混淆")
    parser.add_argument("--no-events", action="store_true",
                        help="跳过 worlds/<id>/events.json 剧本（仅用命令行 --event）")
    parser.add_argument("--aggregate-only", action="store_true",
                        help="不跑 LLM，直接从已保存的 outputs 曲线文件离线聚合")
    args = parser.parse_args()

    utils.set_seed(args.seed)

    # 场景标签：--scenario > 政策名 > baseline
    scenario_name = args.scenario
    if not scenario_name:
        from engine.policy import Policy
        scenario_name = args.policy if args.policy else "baseline"

    # 上帝注入的新闻（命令行方式，与 events.json 剧本并存）
    inline_events = []
    if args.event:
        from engine.news import NewsItem
        for text in args.event:
            parts = [p.strip() for p in text.split("|")]
            if len(parts) < 3:
                print(f"[错误] 事件格式应为 日期|标题|内容[|来源]：{text}")
                sys.exit(1)
            inline_events.append(NewsItem(
                date=parts[0], time="07:00", title=parts[1], content=parts[2],
                source=parts[3] if len(parts) > 3 else "官方公告"))
        print(f"上帝注入新闻 {len(inline_events)} 条")

    # 政策上下文（无干预为空串 → 与基线行为完全一致）
    policy_context = ""
    policy_name = None
    if args.policy:
        from engine.policy import Policy
        policy = Policy.from_name(args.policy)
        policy_name = policy.describe()
        policy_context = policy.render()
        print(f"政策干预: {policy_name}")

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

    # 每户一个 World（含各自跨天记忆与新闻台）
    worlds = {}
    homes = {}
    for info in selected:
        household = info["household"]
        home = create_home_from_household(household)
        homes[info["house_id"]] = home
        world = World(
            home, world_id=args.world_id, postcode=postcode,
            house_id=info["house_id"], start_date=args.date)
        # --no-events：跳过 events.json 剧本，仅保留命令行注入的新闻
        if args.no_events:
            world.news.items = []
        # 命令行注入的新闻并入每个世界的新闻台
        for item in inline_events:
            world.news.add_event(item)
        worlds[info["house_id"]] = world

    for day in range(args.days):
        print(f"\n=== 第 {day + 1}/{args.days} 天 ===")

        def run_one(item):
            house_id, world = item
            # 季节从 household 配置读
            household = next(h for h in selected if h["house_id"] == house_id)["household"]
            season = household.get("season", config.DEFAULT_SEASON)
            # 环境接口：真实/配置随机/手工（计划23）
            from engine.environment_interface import EnvironmentInterface
            env = EnvironmentInterface.get_weather(location, world.time.date.strftime('%Y-%m-%d'), season)
            day_result = world.simulate_day(
                season=season,
                weather=env["condition"],
                temperature=env["temperature"]["avg"],
                verbose=False,
                policy_context=policy_context,
                policy_name=scenario_name)
            day_result["_env"] = {"season": season, "condition": env["condition"],
                                  "temperature": env["temperature"]["avg"],
                                  "mode": env.get("mode", "?")}
            return house_id, day_result

        with ThreadPoolExecutor(max_workers=len(worlds)) as executor:  # 户级并行 = 世界家庭数
            house_results = list(executor.map(run_one, worlds.items()))

        # 聚合
        population = aggregate_population(house_results)
        population["policy"] = scenario_name   # 场景标签（政策或新闻实验名），供对比脚本识别
        population["environment"] = {h: r.get("_env", {}) for h, r in house_results}  # 计划23：环境信息

        date_str = house_results[0][1]["date"].replace("年", "-").replace("月", "-").replace("日", "")
        # 每个政策场景存独立子目录，避免互相覆盖（计划9发现的缺陷）
        policy_dir = scenario_name
        out_dir = os.path.join(pop_root, policy_dir, date_str)
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

    # 并发观测（用户 2026-08：不设上限，仅报告实测峰值）
    current, peak = SubAgent.get_concurrency_stats()
    print("\n=== 并发实测（观测，无限制）===")
    print(f"  历史峰值并发 {peak}")
    print("人口模拟完成")


if __name__ == "__main__":
    main()


