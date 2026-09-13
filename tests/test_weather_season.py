"""L1 tests for date-derived season (Australian) in engine.weather."""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from engine import weather  # noqa: E402


class SeasonTests(unittest.TestCase):
    def test_months(self):
        self.assertEqual(weather.season_for_date("2026-01-15"), "Summer")
        self.assertEqual(weather.season_for_date("2026-04-15"), "Autumn")
        self.assertEqual(weather.season_for_date("2026-07-15"), "Winter")
        self.assertEqual(weather.season_for_date("2026-09-15"), "Spring")
        self.assertEqual(weather.season_for_date("2026-12-31"), "Summer")

    def test_missing(self):
        self.assertIsNone(weather.season_for_date(None))
        self.assertIsNone(weather.season_for_date("bad"))

    def test_get_weather_uses_date(self):
        winter = weather.get_weather("2026-07-15")
        self.assertEqual(winter["season"], "Winter")
        self.assertEqual(winter["temperature"], 10)
        summer = weather.get_weather("2026-01-15")
        self.assertEqual(summer["season"], "Summer")
        self.assertEqual(summer["temperature"], 31)

    def test_override_still_applies(self):
        hot = weather.get_weather("2026-07-15", override={"weather": "Heatwave", "temperature_delta": 12})
        self.assertEqual(hot["weather"], "Heatwave")
        self.assertEqual(hot["temperature"], 22)


if __name__ == "__main__":
    unittest.main()
