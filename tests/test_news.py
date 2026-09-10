"""L1 offline tests for engine.news (preset event templates + injection helpers).

Zero API calls. Covers the news/event capability referenced by
intervention_experiment_guide.md §5 and consumed by analyze_event_response.py.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import json
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from engine import news  # noqa: E402


class TemplateTests(unittest.TestCase):
    def test_ten_presets(self):
        self.assertEqual(len(news.NEWS_TEMPLATES), 10)
        self.assertEqual(len(news.list_templates()), 10)

    def test_expected_names(self):
        expected = {"heatwave", "cold_snap", "storm", "price_hike", "energy_crisis",
                    "ac_tax", "rebate", "blackout_risk", "solar_incentive", "lockdown"}
        self.assertEqual(set(news.list_templates()), expected)

    def test_each_template_has_title_and_content(self):
        for name, template in news.NEWS_TEMPLATES.items():
            self.assertTrue(template.get("title"), name)
            self.assertTrue(template.get("content"), name)


class ParseEventSpecTests(unittest.TestCase):
    def test_valid(self):
        event = news.parse_event_spec("2026-04-21|Subsidy cancelled|The off-peak subsidy ends next month")
        self.assertEqual(event, {"date": "2026-04-21", "title": "Subsidy cancelled",
                                 "content": "The off-peak subsidy ends next month"})

    def test_content_may_contain_pipe(self):
        event = news.parse_event_spec("2026-04-21|T|a|b")
        self.assertEqual(event["content"], "a|b")

    def test_empty_is_none(self):
        self.assertIsNone(news.parse_event_spec(""))
        self.assertIsNone(news.parse_event_spec(None))

    def test_malformed_raises(self):
        with self.assertRaises(ValueError):
            news.parse_event_spec("2026-04-21|only-title")
        with self.assertRaises(ValueError):
            news.parse_event_spec("|title|content")


class ParseTemplateSpecTests(unittest.TestCase):
    def test_valid(self):
        event = news.parse_event_template_spec("2026-01-15|heatwave")
        self.assertEqual(event["date"], "2026-01-15")
        self.assertEqual(event["title"], news.NEWS_TEMPLATES["heatwave"]["title"])

    def test_case_insensitive(self):
        self.assertIsNotNone(news.parse_event_template_spec("2026-01-15|HeatWave"))

    def test_unknown_template_raises(self):
        with self.assertRaises(ValueError):
            news.parse_event_template_spec("2026-01-15|meteor")

    def test_empty_is_none(self):
        self.assertIsNone(news.parse_event_template_spec(None))

    def test_malformed_raises(self):
        with self.assertRaises(ValueError):
            news.parse_event_template_spec("2026-01-15")


class ParseEventsTests(unittest.TestCase):
    def test_combines_sources(self):
        events = news.parse_events(
            event_specs=["2026-04-21|Custom|A custom event"],
            template_specs=["2026-04-22|heatwave"])
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["title"], "Custom")
        self.assertEqual(events[1]["date"], "2026-04-22")

    def test_skips_empty(self):
        self.assertEqual(news.parse_events([""], [None]), [])


class EventsForDateTests(unittest.TestCase):
    EVENTS = [
        {"date": "2026-04-20", "title": "a", "content": "x"},
        {"date": "2026-04-22", "title": "b", "content": "y"},
        {"date": "2026-04-24", "title": "c", "content": "z"},
    ]

    def test_filters_future(self):
        active = news.events_for_date(self.EVENTS, "2026-04-22")
        self.assertEqual([e["title"] for e in active], ["a", "b"])

    def test_keeps_most_recent_n(self):
        active = news.events_for_date(self.EVENTS, "2026-04-30", keep=2)
        self.assertEqual([e["title"] for e in active], ["b", "c"])

    def test_keep_zero_returns_all(self):
        active = news.events_for_date(self.EVENTS, "2026-04-30", keep=0)
        self.assertEqual(len(active), 3)

    def test_ignores_bad_entries(self):
        active = news.events_for_date([{"nope": 1}, None], "2026-04-30")
        self.assertEqual(active, [])


class RenderTests(unittest.TestCase):
    def test_empty_renders_blank(self):
        self.assertEqual(news.render_world_news([]), "")
        self.assertEqual(news.render_world_news(None), "")

    def test_renders_lines(self):
        text = news.render_world_news([{"date": "2026-04-21", "title": "T", "content": "C"}])
        self.assertIn("2026-04-21", text)
        self.assertIn("T", text)
        self.assertIn("C", text)


class PersistenceTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = [{"date": "2026-04-21", "title": "T", "content": "C"}]
            news.write_events_json(tmp, events)
            self.assertEqual(news.load_events_json(tmp), events)
            with open(os.path.join(tmp, "events.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"events": events})

    def test_load_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(news.load_events_json(tmp), [])

    def test_load_corrupt(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "events.json"), "w", encoding="utf-8") as f:
                f.write("{not json")
            self.assertEqual(news.load_events_json(tmp), [])


if __name__ == "__main__":
    unittest.main()
