"""L1 offline tests for the neighbour-comparison social signal (engine.social).

Zero API calls. Covers the pure helpers that render the --peer-nudge text
(intervention_experiment_guide.md §6.1).

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from engine import social  # noqa: E402


class CommunityMeanTests(unittest.TestCase):
    def test_mean_of_totals(self):
        self.assertEqual(social.community_mean_kwh([1.0, 2.0, 3.0]), 2.0)

    def test_ignores_none_values(self):
        self.assertEqual(social.community_mean_kwh([1.0, None, 3.0]), 2.0)

    def test_rounds_to_three_places(self):
        self.assertEqual(social.community_mean_kwh([1.0, 2.0, 2.0]), 1.667)

    def test_empty_and_none(self):
        self.assertIsNone(social.community_mean_kwh([]))
        self.assertIsNone(social.community_mean_kwh(None))
        self.assertIsNone(social.community_mean_kwh([None, None]))


class RenderPeerNudgeTests(unittest.TestCase):
    def test_none_renders_blank(self):
        self.assertEqual(social.render_peer_nudge(None), "")

    def test_renders_value_and_context(self):
        text = social.render_peer_nudge(5.5)
        self.assertIn("5.50 kWh", text)
        self.assertIn("community", text)
        self.assertIn("yesterday", text)

    def test_zero_mean_is_rendered(self):
        self.assertIn("0.00 kWh", social.render_peer_nudge(0.0))


if __name__ == "__main__":
    unittest.main()
