










import json
import os
import random

import config


class EnvironmentInterface:
    @staticmethod
    def get_weather(location, date_str, season="Spring"):

        mode = config.ENV_MODE

        if mode == "real":
            weather = EnvironmentInterface._real(location, date_str)
            if weather is not None:
                return weather
            print("[env] Real weather unavailable (no key or failed); falling back to config random mode")
            weather = EnvironmentInterface._config(season)
            weather["mode"] = "config(fallback)"
            return weather

        if mode == "manual":
            return EnvironmentInterface._manual(date_str)

        weather = EnvironmentInterface._config(season)
        weather["mode"] = "config"
        return weather



    @staticmethod
    def _real(location, date_str):
        from .weather_api import WeatherAPI
        try:
            result = WeatherAPI.get_history(
                location["coordinates"]["lat"],
                location["coordinates"]["lon"],
                date_str,
            )
            if result and result.get("condition"):
                result["mode"] = "real"
                return result
        except Exception as e:
            print(f"[env] Real weather error: {e}")
        return None



    @staticmethod
    def _config(season):
        climate = config.MELBOURNE_CLIMATE.get(season, config.MELBOURNE_CLIMATE["Spring"])
        lo, hi = climate["temp_range"]


        weathers, weights = zip(*climate["weathers"])
        condition = random.choices(weathers, weights=weights, k=1)[0]


        avg = random.randint(lo, hi)
        span = random.randint(3, 6)
        t_min = max(lo - 3, avg - span)
        t_max = min(hi + 3, avg + span)

        return {
            "date": "",
            "temperature": {"min": t_min, "max": t_max, "avg": avg},
            "condition": condition,
            "humidity": random.randint(40, 85),
        }



    @staticmethod
    def _manual(date_str):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(project_root, config.ENV_MANUAL_FILE)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"ENV_MODE=manual but config file {path} was not found (create it, or use config mode)")

        with open(path, "r", encoding="utf-8") as f:
            conf = json.load(f)

        temp = conf.get("temperature", 20)
        if isinstance(temp, (list, tuple)) and len(temp) == 2:

            avg = random.randint(temp[0], temp[1])
            t_min, t_max = temp[0], temp[1]
        else:
            avg = t_min = t_max = float(temp)

        return {
            "date": date_str,
            "temperature": {"min": t_min, "max": t_max, "avg": avg},
            "condition": conf.get("condition", "Sunny"),
            "humidity": conf.get("humidity", 60),
            "mode": "manual",
        }
