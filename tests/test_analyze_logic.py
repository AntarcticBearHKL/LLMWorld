"""L1 offline tests for analysis-layer pure functions.

Zero API calls, no file I/O. Covers the metrics that turn s4 decisions into the
paper's reported quantities:
  - analyze_groups.group_stats            (grouped policy response, RQ3)
  - analyze_policy_tradeoffs               (peak shaving / plateau / peak-to-mean)
  - compare_tou                            (tariff-window attribution)
  - dataset.household_features             (personality features read by grouping)

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

import analyze_groups  # noqa: E402
import analyze_policy_tradeoffs as tradeoffs  # noqa: E402
import compare_tou  # noqa: E402
import dataset  # noqa: E402


class GroupStatsTests(unittest.TestCase):
    LABELS = {"h1": "High", "h2": "Low", "h3": "High"}
    SCENARIOS = {
        "baseline": {"h1": 10.0, "h2": 20.0, "h3": 30.0},
        "tou": {"h1": 9.0, "h2": 18.0, "h3": 27.0},
    }

    def test_group_means_and_change(self):
        rows = analyze_groups.group_stats(self.LABELS, self.SCENARIOS)
        by_group = {r["group"]: r for r in rows}
        self.assertEqual(by_group["High"]["households"], 2)
        self.assertEqual(by_group["High"]["baseline_mean_kwh"], 20.0)
        self.assertEqual(by_group["High"]["tou_mean_kwh"], 18.0)
        self.assertEqual(by_group["High"]["tou_change_pct"], -10.0)
        self.assertEqual(by_group["Low"]["baseline_mean_kwh"], 20.0)

    def test_group_order_follows_label_insertion(self):
        rows = analyze_groups.group_stats(self.LABELS, self.SCENARIOS)
        self.assertEqual([r["group"] for r in rows], ["High", "Low"])

    def test_missing_baseline_yields_none(self):
        rows = analyze_groups.group_stats(self.LABELS, {"tou": self.SCENARIOS["tou"]})
        by_group = {r["group"]: r for r in rows}
        self.assertIsNone(by_group["High"]["baseline_mean_kwh"])
        self.assertIsNone(by_group["High"]["tou_change_pct"])
        self.assertEqual(by_group["High"]["tou_mean_kwh"], 18.0)


class TradeoffMetricTests(unittest.TestCase):
    def test_energy_of_hours(self):
        profile = [0.0] * 1440
        for m in range(0, 60):
            profile[m] = 1000.0
        self.assertEqual(tradeoffs.energy_of_hours(profile, (0, 1)), 1.0)
        self.assertEqual(tradeoffs.energy_of_hours(profile, (16, 21)), 0.0)

    def test_peak_plateau_minutes(self):
        self.assertEqual(tradeoffs.peak_plateau_minutes([0.0, 10.0, 8.0, 9.0, 2.0], ratio=0.8), 3)

    def test_peak_plateau_zero_profile(self):
        self.assertEqual(tradeoffs.peak_plateau_minutes([0.0] * 10), 0)

    def test_peak_to_mean_ratio(self):
        self.assertEqual(tradeoffs.peak_to_mean_ratio([0.0, 0.0, 10.0, 0.0]), 4.0)

    def test_peak_to_mean_none_for_zero_mean(self):
        self.assertIsNone(tradeoffs.peak_to_mean_ratio([0.0] * 5))

    def test_change_pct(self):
        self.assertEqual(tradeoffs._change_pct(90.0, 100.0), -10.0)
        self.assertEqual(tradeoffs._change_pct(110.0, 100.0), 10.0)
        self.assertIsNone(tradeoffs._change_pct(10.0, 0.0))


class TariffWindowTests(unittest.TestCase):
    def test_minutes_of_day(self):
        self.assertEqual(compare_tou.minutes_of_day("16:30"), 990)
        self.assertEqual(compare_tou.minutes_of_day("00:00"), 0)

    def test_window_of(self):
        self.assertEqual(compare_tou.window_of(16 * 60), "peak")
        self.assertEqual(compare_tou.window_of(20 * 60 + 59), "peak")
        self.assertEqual(compare_tou.window_of(0), "valley")
        self.assertEqual(compare_tou.window_of(22 * 60), "valley")
        self.assertEqual(compare_tou.window_of(8 * 60), "shoulder")

    def test_segment_minutes(self):
        self.assertEqual(len(compare_tou.segment_minutes("16:00-17:00")), 60)
        self.assertEqual(len(compare_tou.segment_minutes("23:30-24:00")), 30)
        self.assertEqual(compare_tou.segment_minutes("bad"), [])

    def test_summarize_attributes_window(self):
        segments = [{"time": "16:00-16:10",
                     "operations": [{"action": "use", "unique_id": "a"}]}]
        minutes, kwh, per_app = compare_tou.summarize(segments, {"a": 1000.0})
        self.assertEqual(minutes["peak"], 10)
        self.assertEqual(minutes["valley"], 0)
        self.assertAlmostEqual(kwh["peak"], 10 * 1000.0 / 1000.0 / 60.0, places=9)
        self.assertEqual(per_app["a"]["peak"], 10)

    def test_summarize_ignores_non_usd_actions(self):
        segments = [{"time": "16:00-16:10",
                     "operations": [{"action": "idle", "unique_id": "a"}]}]
        minutes, kwh, per_app = compare_tou.summarize(segments, {"a": 1000.0})
        self.assertEqual(minutes["peak"], 0)
        self.assertEqual(kwh["peak"], 0.0)
        self.assertEqual(per_app, {})


class HouseholdFeatureTests(unittest.TestCase):
    def test_reads_personality(self):
        household = {"type": "family", "members": [
            {"age": 30, "personality": {"energy_awareness": "High",
                                        "big_five": {"openness": 0.8}}}]}
        feats = dataset.household_features(household)
        self.assertEqual(feats["household_type"], "family")
        self.assertEqual(feats["members_count"], 1)
        self.assertEqual(feats["energy_awareness"], "High")
        self.assertEqual(feats["big_five"], {"openness": 0.8})
        self.assertEqual(feats["age"], 30)

    def test_missing_personality_defaults(self):
        feats = dataset.household_features({"type": "single", "members": [{"age": 40}]})
        self.assertEqual(feats["energy_awareness"], "?")
        self.assertEqual(feats["big_five"], {})

    def test_non_dict_household(self):
        feats = dataset.household_features("junk")
        self.assertEqual(feats["household_type"], "?")
        self.assertEqual(feats["members_count"], 0)
        self.assertEqual(feats["age"], 0)


if __name__ == "__main__":
    unittest.main()
