"""L1 offline tests for the cross-day carry-over continuity feature.

Zero API calls: everything here is pure logic (day_state) or local prompt
rendering (engine.prompt). Run with:

    .venv\\Scripts\\python.exe -m unittest discover -s tests -v

Context: goal.md requires L1 offline tests before any real (token-spending)
simulation. This locks the day-boundary anti-teleport behaviour wired into
run.py -> s1_macro_plan.run_step -> day_state.
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

from steps.simulate import day_state  # noqa: E402
from engine.prompt import Prompt  # noqa: E402


def seg(time, location, activity):
    return {"time": time, "location": location, "activity": activity}


class ParseRangeTests(unittest.TestCase):
    def test_valid_range(self):
        self.assertEqual(day_state._parse_range("07:30-08:15"), (450, 495))

    def test_full_day_range(self):
        self.assertEqual(day_state._parse_range("00:00-24:00"), (0, 1440))

    def test_rejects_non_range(self):
        self.assertIsNone(day_state._parse_range("08:00"))
        self.assertIsNone(day_state._parse_range(""))
        self.assertIsNone(day_state._parse_range(None))

    def test_rejects_zero_or_reversed_span(self):
        self.assertIsNone(day_state._parse_range("08:00-08:00"))
        self.assertIsNone(day_state._parse_range("09:00-08:00"))

    def test_rejects_non_numeric(self):
        self.assertIsNone(day_state._parse_range("ab:cd-ef:gh"))


class IsOutTests(unittest.TestCase):
    def test_out_variants(self):
        for value in ("Out", "out", "OUT", "Out (work)", "out(downtown)", "Out at gym"):
            self.assertTrue(day_state._is_out(value), value)

    def test_home_locations_are_not_out(self):
        for value in ("Living Room", "Kitchen", "", None, "Workplace"):
            self.assertFalse(day_state._is_out(value), value)


class FormatTests(unittest.TestCase):
    def test_format_edges(self):
        self.assertEqual(day_state._fmt(0), "00:00")
        self.assertEqual(day_state._fmt(45), "00:45")
        self.assertEqual(day_state._fmt(1440), "24:00")

    def test_format_clamps(self):
        self.assertEqual(day_state._fmt(-10), "00:00")
        self.assertEqual(day_state._fmt(2000), "24:00")


class EndStateTests(unittest.TestCase):
    def test_empty_returns_none(self):
        self.assertIsNone(day_state.end_state([]))
        self.assertIsNone(day_state.end_state(None))

    def test_reads_last_segment(self):
        activities = [
            seg("00:00-08:00", "Bedroom", "Sleeping"),
            seg("08:00-24:00", "Out", "Working"),
        ]
        state = day_state.end_state(activities)
        self.assertEqual(state["end_time"], "08:00-24:00")
        self.assertEqual(state["end_location"], "Out")
        self.assertTrue(state["ends_out"])

    def test_home_end_not_out(self):
        state = day_state.end_state([seg("22:00-24:00", "Bedroom", "Sleeping")])
        self.assertFalse(state["ends_out"])


class CarryOverTextTests(unittest.TestCase):
    def test_none_state_is_empty(self):
        self.assertEqual(day_state.carry_over_text(None, "Alice"), "")
        self.assertEqual(day_state.carry_over_text({}, "Alice"), "")

    def test_mentions_member_and_previous_state(self):
        state = {"end_location": "Out", "end_activity": "Working", "ends_out": True}
        text = day_state.carry_over_text(state, "Alice")
        self.assertIn("Alice", text)
        self.assertIn("Out", text)
        self.assertIn("Working", text)
        self.assertIn("commuting home", text)


class ReconcileBoundaryTests(unittest.TestCase):
    HOME_DAY = [
        seg("00:00-09:00", "Bedroom", "Sleeping"),
        seg("09:00-17:00", "Out", "Working"),
        seg("17:00-24:00", "Living Room", "Relaxing"),
    ]
    OUT_STATE = {"end_location": "Out", "end_activity": "Working", "ends_out": True}
    HOME_STATE = {"end_location": "Bedroom", "end_activity": "Sleeping", "ends_out": False}

    def test_no_previous_day_is_noop(self):
        activities = [seg("00:00-24:00", "Living Room", "Relaxing")]
        self.assertIs(day_state.reconcile_boundary(activities, None), activities)
        self.assertIs(day_state.reconcile_boundary(activities, {}), activities)

    def test_previous_day_not_out_is_noop(self):
        activities = [seg("00:00-24:00", "Living Room", "Relaxing")]
        self.assertIs(day_state.reconcile_boundary(activities, self.HOME_STATE), activities)

    def test_first_segment_already_out_is_noop(self):
        activities = [seg("00:00-08:00", "Out", "Working")]
        self.assertIs(day_state.reconcile_boundary(activities, self.OUT_STATE), activities)

    def test_unparseable_first_segment_is_noop(self):
        activities = [seg("bad", "Living Room", "Relaxing")]
        self.assertIs(day_state.reconcile_boundary(activities, self.OUT_STATE), activities)

    def test_splits_opening_home_segment(self):
        rewritten = day_state.reconcile_boundary(self.HOME_DAY, self.OUT_STATE)
        self.assertIsNot(rewritten, self.HOME_DAY)
        self.assertEqual(len(rewritten), 4)
        self.assertEqual(rewritten[0], {"time": "00:00-00:45", "location": "Out",
                                        "activity": "Commuting home from work"})
        self.assertEqual(rewritten[1]["time"], "00:45-09:00")
        self.assertEqual(rewritten[1]["location"], "Bedroom")
        self.assertEqual(rewritten[2:], self.HOME_DAY[1:])

    def test_short_first_segment_is_replaced_by_commute(self):
        activities = [seg("00:00-00:30", "Bedroom", "Sleeping"),
                      seg("00:30-24:00", "Living Room", "Relaxing")]
        rewritten = day_state.reconcile_boundary(activities, self.OUT_STATE)
        self.assertEqual(rewritten[0],
                         {"time": "00:00-00:30", "location": "Out",
                          "activity": "Commuting home from work"})
        self.assertEqual(rewritten[1:], activities[1:])

    def test_gap_before_first_segment_is_filled(self):
        activities = [seg("06:00-09:00", "Bedroom", "Sleeping"),
                      seg("09:00-24:00", "Living Room", "Relaxing")]
        rewritten = day_state.reconcile_boundary(activities, self.OUT_STATE)
        self.assertEqual(len(rewritten), 3)
        self.assertEqual(rewritten[0]["time"], "00:00-06:00")
        self.assertEqual(rewritten[0]["location"], "Out")
        self.assertEqual(rewritten[1:], activities)

    def test_rewrite_covers_00_24_without_gaps(self):
        rewritten = day_state.reconcile_boundary(self.HOME_DAY, self.OUT_STATE)
        cursor = 0
        for item in rewritten:
            start, end = day_state._parse_range(item["time"])
            self.assertEqual(start, cursor, item)
            cursor = end
        self.assertEqual(cursor, 1440)

    def test_does_not_mutate_input(self):
        snapshot = json.dumps(self.HOME_DAY, ensure_ascii=False)
        day_state.reconcile_boundary(self.HOME_DAY, self.OUT_STATE)
        self.assertEqual(json.dumps(self.HOME_DAY, ensure_ascii=False), snapshot)


class PersistenceTests(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = {"end_location": "Out", "end_activity": "Working", "ends_out": True}
            path = day_state.save_day_state(tmp, "Alice", state)
            self.assertTrue(os.path.isfile(path))
            self.assertEqual(day_state.load_day_state(tmp, "Alice"), state)

    def test_save_none_is_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(day_state.save_day_state(tmp, "Alice", None))
            self.assertEqual(os.listdir(tmp), [])

    def test_load_missing_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(day_state.load_day_state(tmp, "Nobody"))

    def test_none_member_requires_unique_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            day_state.save_day_state(tmp, "Alice", {"ends_out": True})
            self.assertIsNotNone(day_state.load_day_state(tmp))
            day_state.save_day_state(tmp, "Bob", {"ends_out": False})
            self.assertIsNone(day_state.load_day_state(tmp))

    def test_load_corrupt_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "day_state_Alice.json"), "w", encoding="utf-8") as f:
                f.write("{not json")
            self.assertIsNone(day_state.load_day_state(tmp, "Alice"))


class PromptWiringTests(unittest.TestCase):
    """The s1 template must actually consume the injected carry-over text."""

    def test_placeholder_is_substituted(self):
        rendered = Prompt().load("simulate_step1_macro_plan",
                                 carry_over_context="CTX_SENTINEL_42")
        self.assertIn("CTX_SENTINEL_42", rendered)
        self.assertNotIn("{carry_over_context}", rendered)

    def test_empty_context_leaves_no_placeholder(self):
        rendered = Prompt().load("simulate_step1_macro_plan", carry_over_context="")
        self.assertNotIn("{carry_over_context}", rendered)


if __name__ == "__main__":
    unittest.main()
