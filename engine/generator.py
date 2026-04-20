import json
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .subagent import SubAgent
from .prompt import Prompt

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
HOLIDAY_API_KEY = os.getenv('HOLIDAY_API_KEY', '')

class EnvironmentGenerator:
    def __init__(self):
        pass
    
    def expand_setting(self, user_prompt):
        prompt = f"""你是一个家庭环境设计专家。根据用户的简短描述，生成详细的家庭环境设定。

用户描述：{user_prompt}

请生成详细的环境设定，包括：
1. 地理位置（城市、区域、坐标）
2. 经济水平和消费能力
3. 文化背景和生活方式
4. 住房类型和面积
5. 社区环境描述

输出JSON格式：
{{
  "setting": "详细的人文环境描述",
  "location": {{
    "city": "城市名",
    "district": "区域",
    "country": "国家代码（如CN、US）",
    "coordinates": {{"lat": 纬度, "lon": 经度}}
  }},
  "culture": "文化背景描述",
  "economic_level": "经济水平（低/中/高）",
  "lifestyle": "生活方式描述",
  "housing": {{
    "type": "住房类型",
    "size": 面积数字
  }}
}}

只返回JSON，不要其他内容。"""
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=True)
        return json.loads(response['content'])
    
    def get_weather_data(self, location, date=None):
        if not WEATHER_API_KEY:
            return self._generate_mock_weather(location)
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        url = "https://api.weatherapi.com/v1/history.json"
        params = {
            'key': WEATHER_API_KEY,
            'q': f"{location['coordinates']['lat']},{location['coordinates']['lon']}",
            'dt': date
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'date': date,
                'location': location['city'],
                'temperature': {
                    'max': data['forecast']['forecastday'][0]['day']['maxtemp_c'],
                    'min': data['forecast']['forecastday'][0]['day']['mintemp_c'],
                    'avg': data['forecast']['forecastday'][0]['day']['avgtemp_c']
                },
                'condition': data['forecast']['forecastday'][0]['day']['condition']['text'],
                'humidity': data['forecast']['forecastday'][0]['day']['avghumidity'],
                'wind_kph': data['forecast']['forecastday'][0]['day']['maxwind_kph'],
                'hourly': [
                    {
                        'time': hour['time'],
                        'temp': hour['temp_c'],
                        'condition': hour['condition']['text'],
                        'humidity': hour['humidity']
                    }
                    for hour in data['forecast']['forecastday'][0]['hour']
                ]
            }
        except Exception as e:
            print(f"天气API调用失败: {e}")
            return self._generate_mock_weather(location)
    
    def get_holiday_data(self, location, year=None):
        if not HOLIDAY_API_KEY:
            return self._generate_mock_holidays(location)
        
        if year is None:
            year = datetime.now().year
        
        url = "https://holidayapi.com/v1/holidays"
        params = {
            'key': HOLIDAY_API_KEY,
            'country': location.get('country', 'CN'),
            'year': year
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            holidays = {}
            for holiday in data.get('holidays', []):
                date = holiday['date']
                if date not in holidays:
                    holidays[date] = []
                holidays[date].append({
                    'name': holiday['name'],
                    'type': holiday.get('type', 'public')
                })
            
            return {
                'year': year,
                'country': location.get('country', 'CN'),
                'holidays': holidays
            }
        except Exception as e:
            print(f"节假日API调用失败: {e}")
            return self._generate_mock_holidays(location)
    
    def generate_home_structure(self, environment):
        prompt = f"""根据环境设定，设计合理的家庭房间布局和家电配置。

环境设定：
{json.dumps(environment, ensure_ascii=False, indent=2)}

要求：
1. 房间数量和类型符合住房面积（{environment['housing']['size']}平米）
2. 家电配置符合经济水平（{environment['economic_level']}）
3. 家电品牌和功率真实合理
4. 每个房间的家电要实用且不重复

输出JSON格式：
{{
  "name": "家庭名称",
  "type": "{environment['housing']['type']}",
  "size": {environment['housing']['size']},
  "rooms": [
    {{
      "name": "房间名",
      "size": 面积,
      "appliances": [
        {{
          "type": "家电类型（必须是：电视、空调、冰箱、洗衣机、微波炉、电饭煲、电磁炉、油烟机、吸尘器、灯、台灯、电脑、手机、电动车 之一）",
          "brand": "品牌",
          "power": 功率瓦数,
          "age": 使用年限
        }}
      ]
    }}
  ]
}}

只返回JSON，不要其他内容。"""
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=True)
        return json.loads(response['content'])
    
    def generate_members(self, environment, home):
        prompt = f"""根据环境和家庭结构，生成详细的家庭成员配置。

环境：
{json.dumps(environment, ensure_ascii=False, indent=2)}

家庭：
{json.dumps(home, ensure_ascii=False, indent=2)}

要求：
1. 成员信息详细且合理
2. 作息习惯符合职业特点
3. 个人偏好有个性差异
4. 个人设备符合年龄和职业
5. 成员数量合理（2-5人）

输出JSON格式（数组）：
[
  {{
    "name": "姓名",
    "age": 年龄,
    "gender": "性别",
    "occupation": "职业",
    "work_schedule": {{
      "start": "09:00",
      "end": "18:00",
      "remote": true/false,
      "work_days": [1,2,3,4,5]
    }},
    "personality": {{
      "traits": ["性格特点"],
      "energy_awareness": "节能意识（低/中/高）"
    }},
    "habits": {{
      "wake_time": "07:00",
      "sleep_time": "23:00",
      "exercise": "运动习惯",
      "hobbies": ["爱好"]
    }},
    "health": {{
      "condition": "健康状况",
      "temperature_preference": {{"summer": 26, "winter": 22}}
    }},
    "personal_appliances": [
      {{
        "type": "设备类型（必须是：手机、电脑、电动车 之一）",
        "brand": "品牌",
        "usage_pattern": "使用模式"
      }}
    ]
  }}
]

只返回JSON，不要其他内容。"""
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=True)
        return json.loads(response['content'])
    
    def _generate_mock_weather(self, location):
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'location': location['city'],
            'temperature': {
                'max': 28,
                'min': 20,
                'avg': 24
            },
            'condition': '晴天',
            'humidity': 65,
            'wind_kph': 15,
            'hourly': [
                {
                    'time': f"2025-04-20 {h:02d}:00",
                    'temp': 20 + (h - 6) if 6 <= h <= 14 else 28 - (h - 14) if h > 14 else 18,
                    'condition': '晴',
                    'humidity': 65
                }
                for h in range(24)
            ]
        }
    
    def _generate_mock_holidays(self, location):
        year = datetime.now().year
        mock_holidays = {
            f"{year}-01-01": [{"name": "元旦", "type": "public"}],
            f"{year}-05-01": [{"name": "劳动节", "type": "public"}],
            f"{year}-10-01": [{"name": "国庆节", "type": "public"}],
        }
        return {
            'year': year,
            'country': location.get('country', 'CN'),
            'holidays': mock_holidays
        }

class DateHelper:
    @staticmethod
    def is_weekend(date):
        return date.weekday() >= 5
    
    @staticmethod
    def is_holiday(date, holidays_data):
        date_str = date.strftime('%Y-%m-%d')
        return date_str in holidays_data.get('holidays', {})
    
    @staticmethod
    def is_workday(date, holidays_data):
        return not (DateHelper.is_weekend(date) or DateHelper.is_holiday(date, holidays_data))
    
    @staticmethod
    def get_holiday_name(date, holidays_data):
        date_str = date.strftime('%Y-%m-%d')
        holidays = holidays_data.get('holidays', {}).get(date_str, [])
        return holidays[0]['name'] if holidays else None
