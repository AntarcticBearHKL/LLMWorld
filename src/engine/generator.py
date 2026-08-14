import json
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .subagent import SubAgent
import config
from .prompt import Prompt

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')

class EnvironmentGenerator:
    def __init__(self):
        self.prompt = Prompt()
    
    def generate_district(self, user_prompt):
        prompt = self.prompt.load("generate_step1_district",
            user_prompt=user_prompt
        )
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=config.THINKING)
        return json.loads(response['content'])
    
    def generate_household_distribution(self, district_info):
        prompt = self.prompt.load("generate_step2_household_distribution",
            district_info=json.dumps(district_info, ensure_ascii=False, indent=2)
        )
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=config.THINKING)
        return json.loads(response['content'])
    
    def generate_household(self, district_info, household_type):
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from appliances import get_supported_appliances_text, get_appliance_schemas_text
        import json
        
        prompt = self.prompt.load("generate_step3_household",
            district_info=json.dumps(district_info, ensure_ascii=False, indent=2),
            household_type=json.dumps(household_type, ensure_ascii=False, indent=2),
            household_type_name=household_type['type'],
            supported_appliances=get_supported_appliances_text(),
            appliance_schemas=get_appliance_schemas_text()
        )
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=config.THINKING)
        return json.loads(response['content'])
    
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
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=config.THINKING)
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
        return self._generate_mock_holidays(location, year)
    
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
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=config.THINKING)
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
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=config.THINKING)
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
    
    def _generate_mock_holidays(self, location, year=None):
        if year is None:
            year = datetime.now().year
        
        country = location.get('country', 'CN')
        
        if country == 'CN':
            mock_holidays = {
                f"{year}-01-01": [{"name": "元旦", "type": "public"}],
                f"{year}-02-10": [{"name": "春节", "type": "public"}],
                f"{year}-02-11": [{"name": "春节", "type": "public"}],
                f"{year}-02-12": [{"name": "春节", "type": "public"}],
                f"{year}-04-04": [{"name": "清明节", "type": "public"}],
                f"{year}-05-01": [{"name": "劳动节", "type": "public"}],
                f"{year}-06-10": [{"name": "端午节", "type": "public"}],
                f"{year}-09-17": [{"name": "中秋节", "type": "public"}],
                f"{year}-10-01": [{"name": "国庆节", "type": "public"}],
                f"{year}-10-02": [{"name": "国庆节", "type": "public"}],
                f"{year}-10-03": [{"name": "国庆节", "type": "public"}],
            }
        elif country == 'AU':
            mock_holidays = {
                f"{year}-01-01": [{"name": "New Year's Day", "type": "public"}],
                f"{year}-01-26": [{"name": "Australia Day", "type": "public"}],
                f"{year}-04-18": [{"name": "Good Friday", "type": "public"}],
                f"{year}-04-21": [{"name": "Easter Monday", "type": "public"}],
                f"{year}-04-25": [{"name": "Anzac Day", "type": "public"}],
                f"{year}-06-09": [{"name": "Queen's Birthday", "type": "public"}],
                f"{year}-12-25": [{"name": "Christmas Day", "type": "public"}],
                f"{year}-12-26": [{"name": "Boxing Day", "type": "public"}],
            }
        elif country == 'US':
            mock_holidays = {
                f"{year}-01-01": [{"name": "New Year's Day", "type": "public"}],
                f"{year}-07-04": [{"name": "Independence Day", "type": "public"}],
                f"{year}-11-27": [{"name": "Thanksgiving", "type": "public"}],
                f"{year}-12-25": [{"name": "Christmas Day", "type": "public"}],
            }
        else:
            mock_holidays = {
                f"{year}-01-01": [{"name": "New Year's Day", "type": "public"}],
                f"{year}-12-25": [{"name": "Christmas Day", "type": "public"}],
            }
        
        return {
            'year': year,
            'country': country,
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


