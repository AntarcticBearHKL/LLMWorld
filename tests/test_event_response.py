"""L1 offline tests for analyze_event_response helpers (event-day comparison, RQ2/RQ3).

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

import analyze_event_response as aer  # noqa: E402


class HourlyMeansTests(unittest.TestCase):
    def test_single_hour_load(self):
        profile = [0.0] * 1440
        for minute in range(0, 60):
            profile[minute] = 600.0
        hourly = aer.hourly_means(profile)
        self.assertEqual(len(hourly), 24)
        self.assertEqual(hourly[0], 600.0)
        self.assertEqual(sum(hourly[1:]), 0.0)

    def test_empty_profile(self):
        hourly = aer.hourly_means([0.0] * 1440)
        self.assertEqual(hourly, [0.0] * 24)


class NormalizeShapeTests(unittest.TestCase):
    def test_zero_total_returns_zeros(self):
        self.assertEqual(aer.normalize_shape([0.0] * 24), [0.0] * 24)

    def test_normalizes_to_sum_one(self):
        hourly = [1.0, 3.0] + [0.0] * 22
        shape = aer.normalize_shape(hourly)
        self.assertEqual(len(shape), 24)
        self.assertAlmostEqual(shape[0], 0.25, places=9)
        self.assertAlmostEqual(shape[1], 0.75, places=9)
        self.assertAlmostEqual(sum(shape), 1.0, places=9)

    def test_preserves_length(self):
        self.assertEqual(len(aer.normalize_shape([2.0] * 24)), 24)


class NormalizeDateTests(unittest.TestCase):
    def test_ascii_is_unchanged(self):
        self.assertEqual(aer._normalize_date("2026-09-11"), "2026-09-11")

    def test_unicode_dashes_normalized(self):
        self.assertEqual(aer._normalize_date("2026\u201309\u201311"), "2026-09-11")
        self.assertEqual(aer._normalize_date("2026\u221209\u221211"), "2026-09-11")

    def test_compact_digits_expanded(self):
        self.assertEqual(aer._normalize_date("20260911"), "2026-09-11")

    def test_invisible_and_space_removed(self):
        self.assertEqual(aer._normalize_date(" 2026-09-11 "), "2026-09-11")
        self.assertEqual(aer._normalize_date("2026-09-11\u200b"), "2026-09-11")


if __name__ == "__main__":
    unittest.main()
