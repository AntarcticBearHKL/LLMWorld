"""L1 offline tests for aggregate_runs.summarize (multi-run averaging harness).

Zero API calls. Motivated by the finding that single-run variance dominates
(see reports/R047, R054), so credible magnitudes need mean +/- spread.

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

import aggregate_runs  # noqa: E402


class SummarizeTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(aggregate_runs.summarize([]),
                         {"n": 0, "mean": None, "std": None, "min": None, "max": None})

    def test_single_value(self):
        result = aggregate_runs.summarize([2.0])
        self.assertEqual(result["n"], 1)
        self.assertEqual(result["mean"], 2.0)
        self.assertEqual(result["std"], 0.0)

    def test_known_values(self):
        result = aggregate_runs.summarize([1.0, 2.0, 3.0])
        self.assertEqual(result["n"], 3)
        self.assertEqual(result["mean"], 2.0)
        self.assertAlmostEqual(result["std"], 0.8165, places=3)
        self.assertEqual(result["min"], 1.0)
        self.assertEqual(result["max"], 3.0)

    def test_ignores_none(self):
        result = aggregate_runs.summarize([1.0, None, 3.0])
        self.assertEqual(result["n"], 2)
        self.assertEqual(result["mean"], 2.0)

    def test_all_none(self):
        self.assertEqual(aggregate_runs.summarize([None, None])["n"], 0)


if __name__ == "__main__":
    unittest.main()
