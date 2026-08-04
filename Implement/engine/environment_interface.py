"""环境信息开放接口（计划23）：统一提供天气/气温，三种模式。

优先级由 config.ENV_MODE 决定：
1. real   → 真实天气 API（WEATHER_API_KEY）；无 key 或失败自动回退 config 模式
2. config → 从墨尔本气候校准表按季节随机采样（温度范围 + 天气分布，种子可复现）
3. manual → 读 env_manual.json 手工配置（temperature 可为固定值或 [min,max] 范围）

调用方（simulate.py / population_runner.py）统一走本接口，不再直连 WeatherAPI。
返回结构：{temperature:{min,max,avg}, condition, humidity, mode}
"""

import json
import os
import random

import config


class EnvironmentInterface:
    @staticmethod
    def get_weather(location, date_str, season="春天"):
        """获取某日天气。location: {city, coordinates}; date_str: YYYY-MM-DD。"""
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

    # ---------- 模式一：真实 API ----------

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

    # ---------- 模式二：气候表随机 ----------

    @staticmethod
    def _config(season):
        climate = config.MELBOURNE_CLIMATE.get(season, config.MELBOURNE_CLIMATE["春天"])
        lo, hi = climate["temp_range"]

        # 天气按概率分布采样
        weathers, weights = zip(*climate["weathers"])
        condition = random.choices(weathers, weights=weights, k=1)[0]

        # 温度：avg 在范围内，min/max 围绕 avg 展开
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

    # ---------- 模式三：手工配置 ----------

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
            # 范围随机：[min, max]
            avg = random.randint(temp[0], temp[1])
            t_min, t_max = temp[0], temp[1]
        else:
            avg = t_min = t_max = float(temp)   # 固定值

        return {
            "date": date_str,
            "temperature": {"min": t_min, "max": t_max, "avg": avg},
            "condition": conf.get("condition", "晴天"),
            "humidity": conf.get("humidity", 60),
            "mode": "manual",
        }
