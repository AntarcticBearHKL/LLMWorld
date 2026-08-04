











import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import utils
import config
from simulate import load_world, create_home_from_household
from engine import World


def main():
    parser = argparse.ArgumentParser(description="全管线冒烟测试（真实 API）")
    parser.add_argument("world_id", help="世界ID")
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--date", type=str, default=config.DEFAULT_START_DATE)
    parser.add_argument("--house", type=int, default=0)
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    args = parser.parse_args()

    if not config.DEEPSEEK_APIKEY:
        print("[失败] .env 里没有 DEEPSEEK_APIKEY，冒烟测试无法进行")
        sys.exit(1)

    utils.set_seed(args.seed)
    print(f"冒烟测试：世界 {args.world_id}，{args.days} 天，种子 {args.seed}")

    world_meta, district_info, households = load_world(args.world_id)
    selected = households[args.house]
    household = selected["household"]
    home = create_home_from_household(household)

    location = district_info["location"]
    postcode = district_info["postcode"]

    world = World(home, world_id=args.world_id, postcode=postcode,
                  house_id=selected["house_id"], start_date=args.date)

    failures = []

    for day in range(args.days):
        print(f"\n=== 第 {day + 1}/{args.days} 天 ===")
        current_date = world.time.date
        from engine.generator import EnvironmentGenerator
        holidays = EnvironmentGenerator().get_holiday_data(location, current_date.year)

        season = household.get("season", config.DEFAULT_SEASON)
        weather = config.DEFAULT_WEATHER

        world.simulate_day(
            season=season,
            weather=weather,
            temperature=config.DEFAULT_TEMPERATURE,
            verbose=False
        )

        day_result = world.history[-1]
        log_dir = day_result["log_dir"]


        stage_prefixes = ["01_第一层", "02_第二层", "03_第三层", "04_第四层"]
        for prefix in stage_prefixes:
            found = [f for f in os.listdir(log_dir) if f.startswith(prefix)]
            if not found:
                failures.append(f"缺少 {prefix} 日志")


        if day >= 1:
            step1_logs = [f for f in os.listdir(log_dir) if f.startswith("01_第一层")]
            if not step1_logs:
                failures.append("第 2 天缺少第一层日志（无法检查记忆注入）")
            else:
                with open(os.path.join(log_dir, step1_logs[0]), "r", encoding="utf-8") as f:
                    step1_text = f.read()
                if "昨日记忆" not in step1_text:
                    failures.append("第 2 天 prompt 未包含昨日记忆章节（跨天记忆未注入）")
                else:
                    print("  [记忆] 昨日记忆已注入第 2 天计划")


        info_dir = os.path.join(log_dir, "用电信息")
        summary_path = os.path.join(info_dir, "总用电汇总.json")
        profile_path = os.path.join(info_dir, "house_load_profile_1440min.json")
        if not os.path.exists(summary_path):
            failures.append("缺少 总用电汇总.json")
        else:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
            if summary.get("baseline_kwh", 0) <= 0:
                failures.append("基载耗电为 0（常开电器未计入）")
            print(f"  日总用电 {summary['total_energy_kwh']} kWh"
                  f"（基载 {summary['baseline_kwh']} + 决策 {summary['decision_kwh']}）")
            if summary.get("validation_warnings"):
                print(f"  校验警告 {len(summary['validation_warnings'])} 条")
                for w in summary["validation_warnings"][:5]:
                    print(f"    - {w}")

        if not os.path.exists(profile_path):
            failures.append("缺少 house_load_profile_1440min.json")
        else:
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
            if len(profile.get("load_profile_watts", [])) != 1440:
                failures.append("负荷曲线不是 1440 点")

        if day < args.days - 1:
            world.next_day()

    tokens = world.get_total_tokens()
    print(f"\n=== Token 账单（{args.days} 天）===")
    print(f"  prompt 缓存未命中: {tokens['prompt_cache_miss']}")
    print(f"  prompt 缓存命中:   {tokens['prompt_cache_hit']}")
    print(f"  输出:              {tokens['completion']}")
    print(f"  总计:              {tokens['total']}")

    if failures:
        print(f"\n[冒烟失败] {len(failures)} 个问题：")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print("\n[冒烟通过] 五阶段管线 + 能耗产物全部正常")


if __name__ == "__main__":
    main()
