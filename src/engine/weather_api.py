import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')

class WeatherAPI:
    @staticmethod
    def get_history(lat, lon, date):
        if not WEATHER_API_KEY:
            return WeatherAPI._mock_data(date)
        
        url = "https://api.weatherapi.com/v1/history.json"
        params = {
            'key': WEATHER_API_KEY,
            'q': f"{lat},{lon}",
            'dt': date
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'date': date,
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
            return WeatherAPI._mock_data(date)
    
    @staticmethod
    def _mock_data(date):
        return {
            'date': date,
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
                    'time': f"{date} {h:02d}:00",
                    'temp': 20 + (h - 6) if 6 <= h <= 14 else 28 - (h - 14) if h > 14 else 18,
                    'condition': 'Sunny',
                    'humidity': 65
                }
                for h in range(24)
            ]
        }

class HolidayAPI:
    @staticmethod
    def get_holidays(country, year):
        holiday_api_key = os.getenv('HOLIDAY_API_KEY', '')
        
        if not holiday_api_key:
            return HolidayAPI._mock_data(country, year)
        
        url = "https://holidayapi.com/v1/holidays"
        params = {
            'key': holiday_api_key,
            'country': country,
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
                'country': country,
                'holidays': holidays
            }
        except Exception as e:
            print(f"Holiday API call failed: {e}")
            return HolidayAPI._mock_data(country, year)
    
    @staticmethod
    def _mock_data(country, year):
        if country == 'CN':
            return {
                'year': year,
                'country': country,
                'holidays': {
                    f"{year}-01-01": [{"name": "New Year's Day", "type": "public"}],
                    f"{year}-05-01": [{"name": "Labour Day", "type": "public"}],
                    f"{year}-10-01": [{"name": "National Day", "type": "public"}],
                }
            }
        else:
            return {
                'year': year,
                'country': country,
                'holidays': {}
            }
