"""L1 offline tests for engine.environment.Time (prompt date context).

Zero API calls. This date/day-type context is injected into every s1/s4 prompt,
so its formatting and holiday/event handling are load-bearing.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import json
import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from engine.environment import Time  # noqa: E402


class DayTypeTests(unittest.TestCase):
    def test_weekday_is_workday(self):
        self.assertEqual(Time("2026-09-11").day_type, "Workday")  # Friday

    def test_weekend_is_weekend(self):
        self.assertEqual(Time("2026-09-12").day_type, "Weekend")  # Saturday

    def test_next_day_updates_type(self):
        t = Time("2026-09-11").next_day()
        self.assertEqual(t.get_date_string(), "2026-09-12")
        self.assertEqual(t.day_type, "Weekend")

    def test_prev_day_updates_type(self):
        t = Time("2026-09-12").prev_day()
        self.assertEqual(t.get_date_string(), "2026-09-11")
        self.assertEqual(t.day_type, "Workday")

    def test_set_day_type_override(self):
        self.assertEqual(Time("2026-09-11").set_day_type("Holiday").day_type, "Holiday")


class FormatTests(unittest.TestCase):
    def test_date_and_weekday(self):
        t = Time("2026-09-11")
        self.assertEqual(t.get_date_string(), "2026-09-11")
        self.assertEqual(t.get_weekday_chinese(), "Friday")
        self.assertEqual(t.get_full_date_string(), "2026-09-11 (Friday)")
        self.assertEqual(str(t), "2026-09-11 (Friday)")


class HolidayTests(unittest.TestCase):
    def test_holiday_detection_and_info(self):
        t = Time("2026-09-11").add_holiday("2026-09-11", "Test Day", "a description")
        self.assertTrue(t.is_holiday())
        self.assertEqual(t.get_holiday_info()["name"], "Test Day")
        context = t.get_context_info()
        self.assertTrue(context["is_holiday"])
        self.assertEqual(context["holiday_name"], "Test Day")
        self.assertEqual(context["holiday_description"], "a description")

    def test_non_holiday_context(self):
        context = Time("2026-09-11").get_context_info()
        self.assertFalse(context["is_holiday"])
        self.assertNotIn("holiday_name", context)


class SpecialEventTests(unittest.TestCase):
    def test_event_detection_and_info(self):
        t = Time("2026-09-11").add_special_event("2026-09-11", "Heatwave", "hot")
        self.assertEqual(t.get_special_event_info()["name"], "Heatwave")
        context = t.get_context_info()
        self.assertTrue(context["has_special_event"])
        self.assertEqual(context["special_event_name"], "Heatwave")

    def test_no_event_context(self):
        self.assertFalse(Time("2026-09-11").get_context_info()["has_special_event"])


class PromptStringTests(unittest.TestCase):
    def test_base_prompt_line(self):
        self.assertEqual(Time("2026-09-11").get_prompt_string(),
                         "Date: 2026-09-11 (Friday) (Workday)")

    def test_holiday_and_event_lines(self):
        t = (Time("2026-09-11")
             .add_holiday("2026-09-11", "Test Day", "a description")
             .add_special_event("2026-09-11", "Heatwave", "hot"))
        prompt = t.get_prompt_string()
        self.assertIn("Holiday: Test Day", prompt)
        self.assertIn("Special event: Heatwave", prompt)


class SerializationTests(unittest.TestCase):
    def test_to_dict_and_json(self):
        t = Time("2026-09-11")
        self.assertEqual(t.to_dict()["date"], "2026-09-11")
        self.assertEqual(json.loads(t.to_json())["day_type"], "Workday")


if __name__ == "__main__":
    unittest.main()
