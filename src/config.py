







import os
from dotenv import load_dotenv

load_dotenv()


DEEPSEEK_APIKEY = os.getenv("DEEPSEEK_APIKEY", "")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
MODEL = "deepseek-v4-flash"
TEMPERATURE = 1.0
MAX_TOKENS = 64000







THINKING = os.getenv("THINKING", "true").strip().lower() in ("1", "true", "yes", "on")
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "low").strip().lower()



MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
LOGIC_MAX_ATTEMPTS = max(1, int(os.getenv("LOGIC_MAX_ATTEMPTS", "4")))
LLM_MAX_CONCURRENCY = max(1, int(os.getenv("LLM_MAX_CONCURRENCY", "10")))


REQUEST_TIMEOUT_SECONDS = 600


DEFAULT_START_DATE = "2026-04-21"
DEFAULT_DAYS = 5
DEFAULT_SEASON = "Spring"
DEFAULT_WEATHER = "Sunny"
DEFAULT_TEMPERATURE = 20
DEFAULT_SEED = 42


CLAYTON_POSTCODE = "3168"



ENV_MODE = "config"


MELBOURNE_CLIMATE = {
    "Summer": {"temp_range": (24, 38), "weathers": [("Sunny", 40), ("Cloudy", 25), ("Heatwave", 15), ("Shower", 20)]},
    "Autumn": {"temp_range": (14, 25), "weathers": [("Sunny", 35), ("Cloudy", 30), ("Shower", 25), ("Windy", 10)]},
    "Winter": {"temp_range": (7, 16),  "weathers": [("Cloudy", 35), ("Overcast", 25), ("Shower", 30), ("ColdSnap", 10)]},
    "Spring": {"temp_range": (12, 23), "weathers": [("Sunny", 40), ("Cloudy", 30), ("Shower", 25), ("Windy", 5)]},
}


ENV_MANUAL_FILE = "env_manual.json"



NEWS_MEMORY_KEEP = 5




APPLIANCE_DAILY_CAP_MINUTES = {
    "ElectricVehicle": 4 * 60,
    "WaterHeater": 45,
    "AirConditioner": 6 * 60,
    "WashingMachine": 2 * 60,
    "VacuumCleaner": 60,
    "TV": 8 * 60,
    "Computer": 10 * 60,
    "InductionCooker": 2 * 60,
    "Microwave": 60,
    "RiceCooker": 2 * 60,
    "Phone": 4 * 60,
    "Light": 16 * 60,
    "DeskLamp": 16 * 60,
    "RangeHood": 2 * 60,
    "SpaceHeater": 360,
    "Fan": 480,
    "Dehumidifier": 480,
    "ClothesDryer": 120,
    "Dishwasher": 120,
    "Kettle": 30,
    "Toaster": 20,
    "Oven": 120,
    "Freezer": 0,
    "Router": 0,
    "GameConsole": 240,
    "Monitor": 600,
    "Ebike": 180,
}
