"""A run resolves to the WORLD it replays — a scenario name is not a world id."""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
DASHBOARD = os.path.join(PROJECT_ROOT, "dashboard")
for _path in (SRC, DASHBOARD):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from backend import derive, paths  # noqa: E402


class RunWorldTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.sim = os.path.join(self._tmp.name, "simulation")
        os.makedirs(self.sim, exist_ok=True)
        self._patch = mock.patch.object(paths, "SIMULATION_DIR", self.sim)
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        self._tmp.cleanup()

    def write_manifest(self, name, payload):
        run_dir = os.path.join(self.sim, name)
        os.makedirs(run_dir, exist_ok=True)
        with open(os.path.join(run_dir, "spacetime.json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh)

    def test_resolves_the_world_from_the_manifest(self):
        self.write_manifest("A", {"name": "A", "world": "world_vapor"})
        self.assertEqual(derive.world_for_run("A"), "world_vapor")

    def test_falls_back_to_the_run_name_without_a_manifest(self):
        os.makedirs(os.path.join(self.sim, "world_838587"), exist_ok=True)
        self.assertEqual(derive.world_for_run("world_838587"), "world_838587")

    def test_manifest_without_a_world_falls_back(self):
        self.write_manifest("B", {"name": "B", "world": ""})
        self.assertEqual(derive.world_for_run("B"), "B")

    def test_an_unusable_name_falls_back_instead_of_raising(self):
        self.assertEqual(derive.world_for_run(".."), "..")


if __name__ == "__main__":
    unittest.main()
