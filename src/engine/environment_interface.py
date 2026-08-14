










import json
import os
import random

import config


class EnvironmentInterface:
    @staticmethod
    def get_weather(location, date_str, season="春天"):

        mode = config.ENV_MODE

        if mode == "real":
            weather = EnvironmentInterface._real(location, date_str)
            if weather is not None:
                return weather
            print("[环境] 真实天气不可用（无 key 或失败），回退到 config 随机模式")
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
            print(f"[环境] 真实天气异常: {e}")
        return None



    @staticmethod
    def _config(season):
        climate = config.MELBOURNE_CLIMATE.get(season, config.MELBOURNE_CLIMATE["春天"])
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
                f"ENV_MODE=manual 但找不到配置文件 {path}（请创建，或用 config 模式）")

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
            "condition": conf.get("condition", "晴天"),
            "humidity": conf.get("humidity", 60),
            "mode": "manual",
        }
