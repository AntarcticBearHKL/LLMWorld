import config

_SEASON_BY_MONTH = {
    12: "Summer", 1: "Summer", 2: "Summer",
    3: "Autumn", 4: "Autumn", 5: "Autumn",
    6: "Winter", 7: "Winter", 8: "Winter",
    9: "Spring", 10: "Spring", 11: "Spring",
}
_SEASON_TEMPERATURE = {"Summer": 31, "Autumn": 18, "Winter": 10, "Spring": 20}


def season_for_date(date):
    """Australian season for an ISO date string (None when unavailable)."""
    if not date:
        return None
    try:
        month = int(str(date)[5:7])
    except (ValueError, TypeError):
        return None
    return _SEASON_BY_MONTH.get(month)


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
    season = season_for_date(date)
    if season:
        result["season"] = season
        result["temperature"] = _SEASON_TEMPERATURE[season]
    if override:
        if override.get("weather"):
            result["weather"] = override["weather"]
        delta = override.get("temperature_delta")
        if isinstance(delta, (int, float)) and not isinstance(delta, bool):
            result["temperature"] = result["temperature"] + delta
    return result
