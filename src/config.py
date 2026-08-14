







import os
from dotenv import load_dotenv

load_dotenv()


DEEPSEEK_APIKEY = os.getenv("DEEPSEEK_APIKEY", "")
MODEL = "deepseek-v4-flash"
TEMPERATURE = 1.0
MAX_TOKENS = 64000







THINKING = False
REASONING_EFFORT = "low"



MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2


REQUEST_TIMEOUT_SECONDS = 600


DEFAULT_START_DATE = "2026年4月21日"
DEFAULT_DAYS = 5
DEFAULT_SEASON = "春天"
DEFAULT_WEATHER = "晴天"
DEFAULT_TEMPERATURE = 20
DEFAULT_SEED = 42


CLAYTON_POSTCODE = "3168"



ENV_MODE = "config"


MELBOURNE_CLIMATE = {
    "夏天": {"temp_range": (24, 38), "weathers": [("晴天", 40), ("多云", 25), ("热浪", 15), ("阵雨", 20)]},
    "秋天": {"temp_range": (14, 25), "weathers": [("晴天", 35), ("多云", 30), ("阵雨", 25), ("大风", 10)]},
    "冬天": {"temp_range": (7, 16),  "weathers": [("多云", 35), ("阴天", 25), ("阵雨", 30), ("寒潮", 10)]},
    "春天": {"temp_range": (12, 23), "weathers": [("晴天", 40), ("多云", 30), ("阵雨", 25), ("大风", 5)]},
}


ENV_MANUAL_FILE = "env_manual.json"



NEWS_MEMORY_KEEP = 5




APPLIANCE_DAILY_CAP_MINUTES = {
    "电动汽车": 4 * 60,
    "热水器": 45,
    "空调": 6 * 60,
    "洗衣机": 2 * 60,
    "吸尘器": 60,
    "电视": 8 * 60,
    "电脑": 10 * 60,
    "电磁炉": 2 * 60,
    "微波炉": 60,
    "电饭煲": 2 * 60,
    "手机": 4 * 60,
    "灯": 16 * 60,
    "台灯": 16 * 60,
    "油烟机": 2 * 60,
}
