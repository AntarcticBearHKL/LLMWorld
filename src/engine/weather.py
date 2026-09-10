import config


def get_weather(date=None):
    """Weather/season provider for a simulation date.

    STUB: always returns configured defaults. Later this will be backed by
    real weather data/API and vary by date; keep this signature stable.
    """
    return {
        "season": config.DEFAULT_SEASON,
        "weather": config.DEFAULT_WEATHER,
        "temperature": config.DEFAULT_TEMPERATURE,
    }
