from engine import EnvironmentGenerator
import json
import os
import random
from datetime import datetime

USER_PROMPT = """
位于墨尔本的中产家庭，居住在clayton
"""

def generate_run_id():
    return str(random.randint(100000, 999999))

def save_log(log_dir, filename, data):
    filepath = os.path.join(log_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  已保存: {filepath}")

def main():
    run_id = generate_run_id()
    log_dir = os.path.join('logs', f"{run_id}_logs_env")
    
    print("="*60)
    print("环境与家庭生成系统")
    print("="*60)
    print(f"运行ID: {run_id}")
    print(f"输出目录: {log_dir}")
    
    user_prompt = USER_PROMPT.strip()
    
    if not user_prompt:
        print("错误：设定描述不能为空")
        return
    
    print(f"\n用户设定：")
    print(f"  {user_prompt}")
    
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs('members', exist_ok=True)
    
    generator = EnvironmentGenerator()
    
    print("\n" + "="*60)
    print("步骤 1/5: 生成环境设定")
    print("="*60)
    environment = generator.expand_setting(user_prompt)
    print(f"\n环境设定生成完成：")
    print(f"  位置: {environment['location']['city']} - {environment['location']['district']}")
    print(f"  经济水平: {environment['economic_level']}")
    print(f"  住房类型: {environment['housing']['type']}")
    print(f"  住房面积: {environment['housing']['size']}平米")
    save_log(log_dir, '01_environment.json', environment)
    
    print("\n" + "="*60)
    print("步骤 2/5: 获取天气数据")
    print("="*60)
    weather = generator.get_weather_data(environment['location'])
    print(f"\n天气数据获取完成：")
    print(f"  日期: {weather['date']}")
    print(f"  天气: {weather['condition']}")
    print(f"  温度: {weather['temperature']['min']}°C - {weather['temperature']['max']}°C")
    print(f"  湿度: {weather['humidity']}%")
    save_log(log_dir, '02_weather.json', weather)
    
    print("\n" + "="*60)
    print("步骤 3/5: 获取节假日数据")
    print("="*60)
    holidays = generator.get_holiday_data(environment['location'])
    print(f"\n节假日数据获取完成：")
    print(f"  年份: {holidays['year']}")
    print(f"  国家: {holidays['country']}")
    print(f"  节假日数量: {len(holidays['holidays'])}")
    if holidays['holidays']:
        print(f"  示例节假日:")
        for date, holiday_list in list(holidays['holidays'].items())[:3]:
            for holiday in holiday_list:
                print(f"    - {date}: {holiday['name']}")
    save_log(log_dir, '03_holidays.json', holidays)
    
    print("\n" + "="*60)
    print("步骤 4/5: 生成家庭结构")
    print("="*60)
    home = generator.generate_home_structure(environment)
    print(f"\n家庭结构生成完成：")
    print(f"  家庭名称: {home['name']}")
    print(f"  住房类型: {home['type']}")
    print(f"  房间数量: {len(home['rooms'])}")
    print(f"  房间列表:")
    for room in home['rooms']:
        appliance_count = len(room['appliances'])
        print(f"    - {room['name']} ({room['size']}平米, {appliance_count}个家电)")
    save_log(log_dir, '04_home.json', home)
    
    print("\n" + "="*60)
    print("步骤 5/5: 生成家庭成员")
    print("="*60)
    members = generator.generate_members(environment, home)
    print(f"\n家庭成员生成完成：")
    print(f"  成员数量: {len(members)}")
    print(f"  成员列表:")
    for member in members:
        personal_appliances = len(member.get('personal_appliances', []))
        print(f"    - {member['name']} ({member['age']}岁, {member['gender']}, {member['occupation']})")
        print(f"      作息: {member['habits']['wake_time']} - {member['habits']['sleep_time']}")
        print(f"      个人设备: {personal_appliances}个")
    save_log(log_dir, '05_members.json', members)
    
    with open('members/environment.json', 'w', encoding='utf-8') as f:
        json.dump(environment, f, ensure_ascii=False, indent=2)
    
    with open('members/weather.json', 'w', encoding='utf-8') as f:
        json.dump(weather, f, ensure_ascii=False, indent=2)
    
    with open('members/holidays.json', 'w', encoding='utf-8') as f:
        json.dump(holidays, f, ensure_ascii=False, indent=2)
    
    with open('members/home.json', 'w', encoding='utf-8') as f:
        json.dump(home, f, ensure_ascii=False, indent=2)
    
    with open('members/members.json', 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=2)
    
    summary = {
        'run_id': run_id,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_prompt': user_prompt,
        'environment': {
            'city': environment['location']['city'],
            'economic_level': environment['economic_level'],
            'housing_type': environment['housing']['type'],
            'housing_size': environment['housing']['size']
        },
        'home': {
            'name': home['name'],
            'rooms_count': len(home['rooms']),
            'total_appliances': sum(len(room['appliances']) for room in home['rooms'])
        },
        'members': {
            'count': len(members),
            'names': [m['name'] for m in members]
        }
    }
    save_log(log_dir, '00_summary.json', summary)
    
    print("\n" + "="*60)
    print("生成完成！")
    print("="*60)
    print(f"\n配置已保存到:")
    print(f"  - members/ 目录（用于模拟）")
    print(f"  - {log_dir}/ 目录（详细日志）")
    
    print("\n环境概览：")
    print(f"  位置：{environment['location']['city']}")
    print(f"  家庭类型：{home['type']}")
    print(f"  房间数量：{len(home['rooms'])}")
    print(f"  成员数量：{len(members)}")
    
    print("\n请运行 'python simulate.py' 开始模拟")

if __name__ == "__main__":
    main()
