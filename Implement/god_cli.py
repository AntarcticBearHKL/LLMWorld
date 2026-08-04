"""上帝交互控制台：逐日模拟时随时注入世界事件（用户=上帝）。

用法：
    python Implement/god_cli.py <world_id> --days N [--date 2026年4月21日] [--policy tou]

每个模拟日之前会询问上帝是否注入新事件：
    输入格式：日期|标题|内容[|来源]（如 2026-04-21|暴风雨预警|强降雨可能停电|气象局）
    回车跳过，q 退出模拟。

事件实时注入内存新闻台 → 当天 prompt 即生效（不必等 events.json 重读）。
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import World, utils
from engine.news import NewsItem
from simulate import load_world, create_home_from_household
import config


def ask_god(day_index, num_days, world):
    """上帝交互：模拟第 day_index 天前询问注入事件。返回 False 表示要退出。"""
    while True:
        print(f"\n[上帝] 第 {day_index + 1}/{num_days} 天模拟前，要注入新事件吗？"
              f"（日期|标题|内容[|来源]，回车跳过，q 退出）")
        try:
            line = input("> ").strip()
        except EOFError:
            return False
        if not line:
            return True
        if line.lower() == "q":
            return False
        try:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 3:
                raise ValueError("至少需要 日期|标题|内容")
            world.news.add_event(NewsItem(
                date=parts[0], time="07:00", title=parts[1], content=parts[2],
                source=parts[3] if len(parts) > 3 else "上帝"))
            print(f"  已注入：{parts[0]} {parts[1]}")
        except ValueError as e:
            print(f"  [格式错误] {e}")


def main():
    parser = argparse.ArgumentParser(description="上帝交互控制台")
    parser.add_argument("world_id")
    parser.add_argument("--days", type=int, default=2)
    parser.add_argument("--date", type=str, default=config.DEFAULT_START_DATE)
    parser.add_argument("--house", type=int, default=0)
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    args = parser.parse_args()

    utils.set_seed(args.seed)

    world_meta, district_info, households = load_world(args.world_id)
    selected = households[args.house]
    household = selected["household"]
    home = create_home_from_household(household)

    postcode = district_info["postcode"]
    world = World(home, world_id=args.world_id, postcode=postcode,
                  house_id=selected["house_id"], start_date=args.date)

    print("=" * 60)
    print("上帝控制台已开启")
    print(f"世界 {args.world_id} | {len(household['members'])} 名成员 | {args.days} 天")
    print(f"events.json 剧本自动加载：{len(world.news.items)} 条已有新闻")
    print("=" * 60)

    season = household.get("season", config.DEFAULT_SEASON)

    for day in range(args.days):
        # 上帝交互（每日本前）
        if not ask_god(day, args.days, world):
            print("\n[上帝] 退出模拟")
            break

        current_date = world.time.date
        print(f"\n=== 第 {day + 1}/{args.days} 天 {world.time.get_full_date_string()} ===")
        if world.news.render_for_prompt(current_date.strftime('%Y-%m-%d')):
            print(f"[新闻] 今日可见 {len(world.news.available_on(current_date.strftime('%Y-%m-%d')))} 条")

        world.simulate_day(
            season=season,
            weather=config.DEFAULT_WEATHER,
            temperature=config.DEFAULT_TEMPERATURE,
            verbose=True)

        executor = world.current_executor
        if executor and executor.validation_warnings:
            print(f"\n[警告] {len(executor.validation_warnings)} 条校验问题")

        if day < args.days - 1:
            world.next_day()

    tokens = world.get_total_tokens()
    print(f"\n=== Token 账单 ===")
    print(f"  总计: {tokens['total']}")
    world.print_summary()


if __name__ == "__main__":
    main()
