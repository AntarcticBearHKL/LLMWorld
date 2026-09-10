"""L1 integration test for the s1 continuity rewrite path (mocked LLM, 0 API).

Closes the gap left since R1: reconcile_boundary was unit-tested, but the full
run_step wiring (load Home -> inject carry-over prompt -> rewrite day boundary ->
persist s1_macro json + day_state json) was not. SubAgent is mocked, and the
world/simulation roots are redirected to a temp dir.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import generate_world as gw  # noqa: E402
from steps.simulate import s1_macro_plan  # noqa: E402

WORLD = "world_test"
ENV = "env_test"
DATE = "2026-09-11"

CANNED_ACTIVITIES = [
    {"time": "00:00-08:00", "location": "Bedroom 1", "activity": "Sleeping"},
    {"time": "08:00-17:00", "location": "Out", "activity": "Working"},
    {"time": "17:00-24:00", "location": "Living Room", "activity": "Relaxing"},
]


def _household():
    return {
        "home": {"name": "H", "rooms": [
            {"name": "Bedroom 1", "appliances": []},
            {"name": "Living Room", "appliances": []},
        ]},
        "members": [{"name": "Alex", "age": 30, "occupation": "engineer",
                     "personality": {}, "habits": {}, "bedroom": "Bedroom 1",
                     "personal_appliances": []}],
    }


class ContinuityIntegrationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = self._tmp.name
        worlds = os.path.join(root, "worlds")
        sims = os.path.join(root, "simulation")
        house_dir = os.path.join(worlds, WORLD, "3168", "house_0001")
        os.makedirs(house_dir, exist_ok=True)
        with open(os.path.join(house_dir, "household.json"), "w", encoding="utf-8") as f:
            json.dump(_household(), f)
        self._patches = [
            mock.patch.object(gw, "WORLDS_DIR", worlds),
            mock.patch.object(gw, "SIMULATION_DIR", sims),
        ]
        for patch in self._patches:
            patch.start()
        self.sim_dir = sims

    def tearDown(self):
        for patch in self._patches:
            patch.stop()
        self._tmp.cleanup()

    def _run(self, prev_state):
        captured = {}

        def fake_single_call(prompt, json_mode=True, json_schema=None):
            captured["prompt"] = prompt
            return {"content": json.dumps({"member": "Alex", "activities": CANNED_ACTIVITIES})}

        with mock.patch.object(s1_macro_plan.SubAgent, "single_call", side_effect=fake_single_call):
            ok, data = s1_macro_plan.run_step(WORLD, "Alex", DATE, ENV, house="house_0001",
                                              prev_state=prev_state)
        return ok, data, captured

    def _out_dir(self):
        return os.path.join(self.sim_dir, ENV, DATE, "house_0001")

    def test_out_boundary_is_rewritten_and_persisted(self):
        ok, data, captured = self._run(
            {"ends_out": True, "end_location": "Out", "end_activity": "Working"})
        self.assertTrue(ok)
        self.assertIn("The previous day ended at 24:00", captured["prompt"])
        self.assertEqual(data["activities"][0], {"time": "00:00-00:45", "location": "Out",
                                                 "activity": "Commuting home from work"})
        with open(os.path.join(self._out_dir(), "s1_macro_Alex.json"), encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(saved["activities"][0]["location"], "Out")
        with open(os.path.join(self._out_dir(), "day_state_Alex.json"), encoding="utf-8") as f:
            state = json.load(f)
        self.assertFalse(state["ends_out"])

    def test_no_previous_day_keeps_plan(self):
        ok, data, captured = self._run(None)
        self.assertTrue(ok)
        self.assertNotIn("The previous day ended at 24:00", captured["prompt"])
        self.assertEqual(data["activities"][0]["time"], "00:00-08:00")

    def test_home_previous_day_keeps_plan(self):
        ok, data, _captured = self._run(
            {"ends_out": False, "end_location": "Bedroom 1", "end_activity": "Sleeping"})
        self.assertTrue(ok)
        self.assertEqual(data["activities"][0]["time"], "00:00-08:00")


if __name__ == "__main__":
    unittest.main()
