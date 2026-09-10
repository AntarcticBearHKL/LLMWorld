"""L1 offline tests for compare_worlds.profile_metrics (guide §7 multi-world control).

Zero API calls, no file I/O.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
ANALYZE = os.path.join(SRC, "analyze")
for _p in (SRC, ANALYZE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import compare_worlds  # noqa: E402


class ProfileMetricsTests(unittest.TestCase):
    def test_empty_profile(self):
        metrics = compare_worlds.profile_metrics([])
        self.assertEqual(metrics["total_kwh"], 0.0)
        self.assertEqual(metrics["peak_watts"], 0.0)
        self.assertIsNone(metrics["peak_to_mean"])
        self.assertIsNone(metrics["evening_morning_ratio"])

    def test_known_profile(self):
        profile = [0.0] * 1440
        for minute in range(6 * 60, 7 * 60):
            profile[minute] = 1000.0
        for minute in range(17 * 60, 18 * 60):
            profile[minute] = 2000.0
        metrics = compare_worlds.profile_metrics(profile)
        self.assertEqual(metrics["total_kwh"], 3.0)
        self.assertEqual(metrics["peak_watts"], 2000.0)
        self.assertEqual(metrics["peak_hour"], 17)
        self.assertEqual(metrics["peak_to_mean"], 16.0)
        self.assertEqual(metrics["morning_kwh"], 1.0)
        self.assertEqual(metrics["evening_kwh"], 2.0)
        self.assertEqual(metrics["evening_morning_ratio"], 2.0)

    def test_zero_profile_has_no_ratios(self):
        metrics = compare_worlds.profile_metrics([0.0] * 1440)
        self.assertEqual(metrics["total_kwh"], 0.0)
        self.assertIsNone(metrics["peak_to_mean"])
        self.assertIsNone(metrics["evening_morning_ratio"])

    def test_ratio_none_without_morning_load(self):
        profile = [0.0] * 1440
        for minute in range(17 * 60, 18 * 60):
            profile[minute] = 1000.0
        metrics = compare_worlds.profile_metrics(profile)
        self.assertEqual(metrics["evening_kwh"], 1.0)
        self.assertIsNone(metrics["evening_morning_ratio"])


if __name__ == "__main__":
    unittest.main()
