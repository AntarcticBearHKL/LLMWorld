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
        prompt = f"""You are a home environment design expert. Based on the user's brief description, generate a detailed home environment setting.

User description: {user_prompt}

Please generate a detailed environment setting, including:
1. Geographic location (city, district, coordinates)
2. Economic level and spending power
3. Cultural background and lifestyle
4. Housing type and size
5. Community environment description

Output in JSON format:
{{
  "setting": "detailed human-environment description",
  "location": {{
    "city": "city name",
    "district": "district",
    "country": "country code (e.g. CN, US)",
    "coordinates": {{"lat": latitude, "lon": longitude}}
  }},
  "culture": "cultural background description",
  "economic_level": "economic level (low/medium/high)",
  "lifestyle": "lifestyle description",
  "housing": {{
    "type": "housing type",
    "size": size number
  }}
}}

Return only JSON, nothing else."""
        
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
            print(f"Weather API call failed: {e}")
            return self._generate_mock_weather(location)
    
    def get_holiday_data(self, location, year=None):
        return self._generate_mock_holidays(location, year)
    
    def generate_home_structure(self, environment):
        prompt = f"""Based on the environment setting, design a reasonable home room layout and appliance configuration.

Environment setting:
{json.dumps(environment, ensure_ascii=False, indent=2)}

Requirements:
1. Number and type of rooms fit the housing size ({environment['housing']['size']} square metres)
2. Appliance configuration fits the economic level ({environment['economic_level']})
3. Appliance brands and power ratings must be realistic and reasonable
4. Appliances in each room must be practical and not duplicated

Output in JSON format:
{{
  "name": "home name",
  "type": "{environment['housing']['type']}",
  "size": {environment['housing']['size']},
  "rooms": [
    {{
      "name": "room name",
      "size": size,
      "appliances": [
        {{
          "type": "appliance type (must be one of: TV, Air Conditioner, Refrigerator, Washing Machine, Microwave, Rice Cooker, Induction Cooker, Range Hood, Vacuum Cleaner, Light, Desk Lamp, Computer, Phone, Electric Vehicle)",
          "brand": "brand",
          "power": power in watts,
          "age": age in years
        }}
      ]
    }}
  ]
}}

Return only JSON, nothing else."""
        
        response = SubAgent.single_call(prompt, json_mode=False, thinking=config.THINKING)
        return json.loads(response['content'])
    
    def generate_members(self, environment, home):
        prompt = f"""Based on the environment and household structure, generate detailed family member configurations.

Environment:
{json.dumps(environment, ensure_ascii=False, indent=2)}

Home:
{json.dumps(home, ensure_ascii=False, indent=2)}

Requirements:
1. Member information must be detailed and reasonable
2. Daily routines must fit the profession
3. Personal preferences must show individual differences
4. Personal devices must fit age and profession
5. Number of members must be reasonable (2-5 people)

Output in JSON format (array):
[
  {{
    "name": "name",
    "age": age,
    "gender": "gender",
    "occupation": "occupation",
    "work_schedule": {{
      "start": "09:00",
      "end": "18:00",
      "remote": true/false,
      "work_days": [1,2,3,4,5]
    }},
    "personality": {{
      "traits": ["personality traits"],
      "energy_awareness": "energy awareness (low/medium/high)"
    }},
    "habits": {{
      "wake_time": "07:00",
      "sleep_time": "23:00",
      "exercise": "exercise habit",
      "hobbies": ["hobbies"]
    }},
    "health": {{
      "condition": "health condition",
      "temperature_preference": {{"summer": 26, "winter": 22}}
    }},
    "personal_appliances": [
      {{
        "type": "device type (must be one of: Phone, Computer, Electric Vehicle)",
        "brand": "brand",
        "usage_pattern": "usage pattern"
      }}
    ]
  }}
]

Return only JSON, nothing else."""
        
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
            'condition': 'Sunny',
            'humidity': 65,
            'wind_kph': 15,
            'hourly': [
                {
                    'time': f"2025-04-20 {h:02d}:00",
                    'temp': 20 + (h - 6) if 6 <= h <= 14 else 28 - (h - 14) if h > 14 else 18,
                    'condition': 'Sunny',
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
                f"{year}-01-01": [{"name": "New Year's Day", "type": "public"}],
                f"{year}-02-10": [{"name": "Spring Festival", "type": "public"}],
                f"{year}-02-11": [{"name": "Spring Festival", "type": "public"}],
                f"{year}-02-12": [{"name": "Spring Festival", "type": "public"}],
                f"{year}-04-04": [{"name": "Qingming Festival", "type": "public"}],
                f"{year}-05-01": [{"name": "Labour Day", "type": "public"}],
                f"{year}-06-10": [{"name": "Dragon Boat Festival", "type": "public"}],
                f"{year}-09-17": [{"name": "Mid-Autumn Festival", "type": "public"}],
                f"{year}-10-01": [{"name": "National Day", "type": "public"}],
                f"{year}-10-02": [{"name": "National Day", "type": "public"}],
                f"{year}-10-03": [{"name": "National Day", "type": "public"}],
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


