







import os
from dotenv import load_dotenv

load_dotenv()


DEEPSEEK_APIKEY = os.getenv("DEEPSEEK_APIKEY", "")
MODEL = "deepseek-v4-flash"
TEMPERATURE = 1.0
MAX_TOKENS = 64000


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").lower()


MATILDA_BASE_URL = os.getenv("MATILDA_BASE_URL", "https://matilda.maincode.com")
MATILDA_API_BASE = os.getenv("MATILDA_API_BASE", "https://matilda.maincode.com/api")
MATILDA_CLIENT_ID = os.getenv("MATILDA_CLIENT_ID", "matilda-code")
MATILDA_API_VERSION = os.getenv("MATILDA_API_VERSION", "2026-06-23")
MATILDA_CREDENTIALS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "matilda_credentials.json"
)







THINKING = False
REASONING_EFFORT = "low"



MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2


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
    "Electric Vehicle": 4 * 60,
    "Water Heater": 45,
    "Air Conditioner": 6 * 60,
    "Washing Machine": 2 * 60,
    "Vacuum Cleaner": 60,
    "TV": 8 * 60,
    "Computer": 10 * 60,
    "Induction Cooker": 2 * 60,
    "Microwave": 60,
    "Rice Cooker": 2 * 60,
    "Phone": 4 * 60,
    "Light": 16 * 60,
    "Desk Lamp": 16 * 60,
    "Range Hood": 2 * 60,
}
