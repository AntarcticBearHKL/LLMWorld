










import argparse
import json
import os
import sys
from datetime import datetime

from engine import Home, Room, Member, World, DateHelper, WeatherAPI
from engine import utils
from appliances import create_appliance_from_config
import config


def load_world(world_id):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    world_path = os.path.join(project_root, 'worlds', world_id)

    if not os.path.exists(world_path):
        print(f"错误：未找到世界 '{world_id}'")
        print(f"请先运行 'python Implement/generate.py' 生成世界")
        exit(1)

    with open(os.path.join(world_path, 'world.json'), 'r', encoding='utf-8') as f:
        world_meta = json.load(f)

    postcode = world_meta['district']['postcode']
    district_path = os.path.join(world_path, postcode)

    with open(os.path.join(district_path, 'district.json'), 'r', encoding='utf-8') as f:
        district_info = json.load(f)

    households = []
    for house_info in world_meta['households']:
        house_id = house_info['house_id']
        house_path = os.path.join(district_path, house_id)

        with open(os.path.join(house_path, 'household.json'), 'r', encoding='utf-8') as f:
            household = json.load(f)

        households.append({
            'house_id': house_id,
            'household': household
        })

    return world_meta, district_info, households


def _personality_str(member_config):

    pers = member_config.get("personality", {})
    parts = [', '.join(pers.get("traits", []))]
    if pers.get("behavior_text"):
        parts.append("行为倾向：" + pers["behavior_text"])
    if pers.get("news_sensitivity"):
        parts.append("对新闻/政策敏感度：" + pers["news_sensitivity"])
    return "。".join(p for p in parts if p)


def create_home_from_household(household):

    home_config = household['home']
    members_config = household['members']

    home = Home(home_config['name'])

    for room_config in home_config['rooms']:
        room = Room(room_config['name'])
        for appliance in room_config['appliances']:
            appliance_obj = create_appliance_from_config(
                appliance['type'], appliance, location=room_config['name'])
            room.add_appliance(appliance_obj)
        home.add_room(room)

    for member_config in members_config:
        member = Member(
            member_config['name'],
            member_config['age'],
            member_config['occupation'],
            _personality_str(member_config),
            member_config['habits']
        )

        for appliance in member_config.get('personal_appliances', []):
            appliance_obj = create_appliance_from_config(
                appliance['type'], appliance, owner=member_config['name'])
            member.add_personal_appliance(appliance_obj)

        home.add_member(member)

    return home


def parse_args():
    parser = argparse.ArgumentParser(description="LLM 家庭用电模拟")
    parser.add_argument("world_id", help="世界ID（worlds/ 下的文件夹名）")
    parser.add_argument("--days", type=int, default=None, help=f"模拟天数（默认 {config.DEFAULT_DAYS}）")
    parser.add_argument("--date", type=str, default=None, help="开始日期，如 '2026年4月21日' 或 '2026-04-21'（缺省=自动续跑）")
    parser.add_argument("--house", type=int, default=None, help="家庭序号（0 起，默认 0）")
    parser.add_argument("--season", type=str, default=None, help=f"季节（默认 {config.DEFAULT_SEASON}）")
    parser.add_argument("--weather", type=str, default=None, help=f"天气（默认 {config.DEFAULT_WEATHER}）")
    parser.add_argument("--temp", type=float, default=None, help=f"温度（默认 {config.DEFAULT_TEMPERATURE}）")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED, help="随机种子（可复现）")
    parser.add_argument("--no-input", action="store_true", help="自动模式：不询问任何输入，缺省用默认值")
    return parser.parse_args()


def main():
    args = parse_args()
    world_id = args.world_id


    utils.set_seed(args.seed)

    print("=" * 60)
    print("世界模拟系统")
    print("=" * 60)
    print(f"世界ID: {world_id}  随机种子: {args.seed}")

    world_meta, district_info, households = load_world(world_id)

    print(f"\n世界信息:")
    print(f"  地区: {district_info['location']['city']} - {district_info['location']['district']}")
    print(f"  邮编: {district_info['postcode']}")
    print(f"  家庭数: {len(households)}")


    if len(households) > 1 and not args.no_input:
        print(f"\n可用的家庭:")
        for i, h in enumerate(households):
            household = h['household']
            print(f"  {i+1}. {h['house_id']} - {len(household['members'])}名成员, {len(household['home']['rooms'])}个房间")

        house_idx = int(input(f"\n请选择要模拟的家庭（1-{len(households)}）：").strip() or "1") - 1
        house_idx = max(0, min(house_idx, len(households) - 1))
    else:
        house_idx = args.house or 0

    selected_house = households[house_idx]
    household = selected_house['household']

    print(f"\n选择的家庭: {selected_house['house_id']}")
    print(f"  成员: {', '.join([m['name'] for m in household['members']])}")

    home = create_home_from_household(household)


    if args.no_input:
        start_date = args.date
        num_days = args.days if args.days is not None else config.DEFAULT_DAYS
    else:
        start_date = args.date or input("\n请输入开始日期（格式：2025年4月20日，留空=自动续跑）：").strip()
        num_days_input = input("请输入模拟天数（默认5天）：").strip()
        num_days = int(num_days_input) if num_days_input else (args.days or config.DEFAULT_DAYS)


    if start_date and "-" in start_date:
        y, m, d = start_date.split("-")
        start_date = f"{int(y)}年{int(m)}月{int(d)}日"

    from engine.world import validate_start_date
    start_date = validate_start_date(world_id, start_date)
    if start_date:
        print(f"开始日期: {start_date}（时间线校验通过）")

    season = args.season or household.get('season', config.DEFAULT_SEASON)
    weather = args.weather or config.DEFAULT_WEATHER
    temperature = args.temp if args.temp is not None else config.DEFAULT_TEMPERATURE

    postcode = district_info['postcode']
    house_id = selected_house['house_id']

    world = World(home, world_id=world_id, postcode=postcode, house_id=house_id, start_date=start_date)

    location = district_info['location']

    for day in range(num_days):
        print(f"\n{'#'*60}")
        print(f"第 {day + 1}/{num_days} 天")
        print(f"{'#'*60}")

        current_date = world.time.date
        date_str = current_date.strftime('%Y-%m-%d')
        year = current_date.year

        from engine.generator import EnvironmentGenerator
        generator = EnvironmentGenerator()
        holidays = generator.get_holiday_data(location, year)

        is_holiday = DateHelper.is_holiday(current_date, holidays)
        is_weekend = DateHelper.is_weekend(current_date)

        holiday_name = DateHelper.get_holiday_name(current_date, holidays)

        day_type = "节假日" if is_holiday else ("周末" if is_weekend else "工作日")
        day_info = f"{day_type}"
        if holiday_name:
            day_info += f" ({holiday_name})"

        print(f"日期类型：{day_info}")

        from engine.environment_interface import EnvironmentInterface
        weather_data = EnvironmentInterface.get_weather(location, date_str, season)

        print(f"天气：{weather_data['condition']}（模式：{weather_data.get('mode', '?')}）")
        print(f"温度：{weather_data['temperature']['min']}°C - {weather_data['temperature']['max']}°C")
        print(f"湿度：{weather_data['humidity']}%")

        world.simulate_day(
            season=season,
            weather=weather_data['condition'],
            temperature=weather_data['temperature']['avg'],
            verbose=True
        )


        executor = world.current_executor
        if executor and executor.validation_warnings:
            print(f"\n[警告] 今日发现 {len(executor.validation_warnings)} 条决策校验问题：")
            for w in executor.validation_warnings:
                print(f"  - {w}")

        if day < num_days - 1:
            world.next_day()

    print(f"\n{'='*60}")
    print(f"完成 {num_days} 天模拟")
    print(f"{'='*60}")
    world.print_summary()

    print("\n完成！")


if __name__ == "__main__":
    main()

