import config


def get_weather(date=None, override=None):
    """Weather/season provider for a simulation date.

    STUB: always returns configured defaults. Later this will be backed by
    real weather data/API and vary by date; keep this signature stable.
    ``override`` may carry {"weather": str, "temperature_delta": number} from an
    active preset event so the news text and the weather fields agree.
    """
    result = {
        "season": config.DEFAULT_SEASON,
        "weather": config.DEFAULT_WEATHER,
        "temperature": config.DEFAULT_TEMPERATURE,
    }
    if override:
        if override.get("weather"):
            result["weather"] = override["weather"]
        delta = override.get("temperature_delta")
        if isinstance(delta, (int, float)) and not isinstance(delta, bool):
            result["temperature"] = result["temperature"] + delta
    return result
