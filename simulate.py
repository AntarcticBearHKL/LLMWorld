from engine import Home, Room, Member, World, DateHelper, WeatherAPI
import json
import os
from datetime import datetime

def load_config():
    if not os.path.exists('members'):
        print("错误：未找到 members/ 目录")
        print("请先运行 'python generate.py' 生成配置")
        exit(1)
    
    with open('members/environment.json', 'r', encoding='utf-8') as f:
        environment = json.load(f)
    
    with open('members/home.json', 'r', encoding='utf-8') as f:
        home_config = json.load(f)
    
    with open('members/members.json', 'r', encoding='utf-8') as f:
        members_config = json.load(f)
    
    with open('members/holidays.json', 'r', encoding='utf-8') as f:
        holidays = json.load(f)
    
    return environment, home_config, members_config, holidays

def create_home_from_config(home_config, members_config):
    home = Home(home_config['name'])
    
    for room_config in home_config['rooms']:
        room = Room(room_config['name'])
        for appliance in room_config['appliances']:
            room.add_appliance_by_name(appliance['type'])
        home.add_room(room)
    
    for member_config in members_config:
        member = Member(
            member_config['name'],
            member_config['age'],
            member_config['occupation'],
            ', '.join(member_config['personality']['traits']),
            member_config['habits']
        )
        
        for appliance in member_config.get('personal_appliances', []):
            member.add_personal_appliance_by_name(appliance['type'])
        
        home.add_member(member)
    
    return home

def main():
    environment, home_config, members_config, holidays = load_config()
    
    home = create_home_from_config(home_config, members_config)
    
    start_date = input("\n请输入开始日期（格式：2025年4月20日，留空使用今天）：").strip()
    if not start_date:
        start_date = datetime.now().strftime('%Y年%m月%d日')
    
    num_days_input = input("请输入模拟天数（默认5天）：").strip()
    num_days = int(num_days_input) if num_days_input else 5
    
    world = World(home, start_date=start_date)
    
    location = environment['location']
    
    for day in range(num_days):
        print(f"\n{'#'*60}")
        print(f"第 {day + 1}/{num_days} 天")
        print(f"{'#'*60}")
        
        current_date = world.time.date
        date_str = current_date.strftime('%Y-%m-%d')
        
        is_holiday = DateHelper.is_holiday(current_date, holidays)
        is_weekend = DateHelper.is_weekend(current_date)
        is_workday = DateHelper.is_workday(current_date, holidays)
        
        holiday_name = DateHelper.get_holiday_name(current_date, holidays)
        
        day_type = "节假日" if is_holiday else ("周末" if is_weekend else "工作日")
        day_info = f"{day_type}"
        if holiday_name:
            day_info += f" ({holiday_name})"
        
        print(f"日期类型：{day_info}")
        
        weather_data = WeatherAPI.get_history(
            location['coordinates']['lat'],
            location['coordinates']['lon'],
            date_str
        )
        
        print(f"天气：{weather_data['condition']}")
        print(f"温度：{weather_data['temperature']['min']}°C - {weather_data['temperature']['max']}°C")
        print(f"湿度：{weather_data['humidity']}%")
        
        world.simulate_day(
            season=environment.get('season', '春天'),
            weather=weather_data['condition'],
            temperature=weather_data['temperature']['avg'],
            verbose=True
        )
        
        if day < num_days - 1:
            world.next_day()
    
    print(f"\n{'='*60}")
    print(f"完成 {num_days} 天模拟")
    print(f"{'='*60}")
    world.print_summary()
    
    print("\n完成！")

if __name__ == "__main__":
    main()
