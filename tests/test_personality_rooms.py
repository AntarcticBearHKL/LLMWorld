"""L1 offline tests for persona-grounded personality derivation.

Zero API calls. Covers the pure helpers shared through
``steps/world/schema.py``: Big Five / energy_awareness derivation from the
sampled persona row or portrait, and the small normalisation helpers the
household-compose step relies on.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import steps.world.schema as schema  # noqa: E402


ALL_MID = {"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5,
           "agreeableness": 0.5, "neuroticism": 0.5}


class MarkerHitTests(unittest.TestCase):
    def test_counts_whole_words_only(self):
        self.assertEqual(schema._marker_hits("i am curious and creative", ("curious", "creative")), 2)
        self.assertEqual(schema._marker_hits("curiously", ("curious",)), 0)

    def test_case_insensitive_via_caller(self):
        self.assertEqual(schema._marker_hits("calm and CALM", ("calm",)), 1)


class PortraitBigFiveTests(unittest.TestCase):
    def test_neutral_portrait_is_midpoint(self):
        self.assertEqual(schema._portrait_big_five(""), ALL_MID)
        self.assertEqual(schema._portrait_big_five(None), ALL_MID)

    def test_single_markers_shift_by_point_one(self):
        scores = schema._portrait_big_five("organized, curious, outgoing, kind, calm")
        self.assertEqual(scores, {"openness": 0.6, "conscientiousness": 0.6,
                                  "extraversion": 0.6, "agreeableness": 0.6, "neuroticism": 0.4})

    def test_positive_clamped_at_max(self):
        text = "curious creative imaginative artistic open-minded intellectual adventurous aesthetic philosophical exploratory"
        self.assertEqual(schema._portrait_big_five(text)["openness"], 0.9)

    def test_negative_clamped_at_min(self):
        text = "conventional traditional routine practical predictable"
        self.assertEqual(schema._portrait_big_five(text)["openness"], 0.1)

    def test_deterministic(self):
        text = "curious and organized but also anxious"
        self.assertEqual(schema._portrait_big_five(text), schema._portrait_big_five(text))


class PortraitEnergyTests(unittest.TestCase):
    def test_high(self):
        self.assertEqual(schema._portrait_energy_awareness("energetic and very active"), "High")

    def test_low(self):
        self.assertEqual(schema._portrait_energy_awareness("tired and exhausted"), "Low")

    def test_neutral(self):
        self.assertEqual(schema._portrait_energy_awareness(""), "Medium")

    def test_tie_defaults_medium(self):
        self.assertEqual(schema._portrait_energy_awareness("energetic tired"), "Medium")


class LevelMapTests(unittest.TestCase):
    def test_level_to_score(self):
        self.assertEqual(schema._level_to_score("Very High"), 0.9)
        self.assertEqual(schema._level_to_score("moderate"), 0.5)
        self.assertEqual(schema._level_to_score(" Slightly Low "), 0.35)
        self.assertIsNone(schema._level_to_score(None))
        self.assertIsNone(schema._level_to_score("zzz"))

    def test_level_to_awareness(self):
        self.assertEqual(schema._level_to_awareness("very low"), "Low")
        self.assertEqual(schema._level_to_awareness("slightly high"), "Medium")
        self.assertEqual(schema._level_to_awareness("excellent"), "High")
        self.assertIsNone(schema._level_to_awareness(None))


class ApplyPersonalityTests(unittest.TestCase):
    def test_prefers_persona_row(self):
        row = {"BFI-2 Open-Mindedness": "High", "BFI-2 Conscientiousness": "Very High",
               "BFI-2 Extraversion": "Low", "BFI-2 Agreeableness": "Average",
               "BFI-2 Negative Emotionality": "Slightly Low", "Energy level": "High"}
        member = {"personality": {"traits": ["x"]}}
        out = schema._apply_personality(member, row, "ignored portrait")
        self.assertEqual(out["personality"]["big_five"],
                         {"openness": 0.8, "conscientiousness": 0.9, "extraversion": 0.25,
                          "agreeableness": 0.5, "neuroticism": 0.35})
        self.assertEqual(out["personality"]["energy_awareness"], "High")
        self.assertEqual(out["personality"]["traits"], ["x"])

    def test_falls_back_to_portrait_when_no_row(self):
        out = schema._apply_personality({"personality": {}}, None, "curious")
        self.assertEqual(out["personality"]["big_five"]["openness"], 0.6)
        self.assertEqual(out["personality"]["energy_awareness"], "Medium")

    def test_fills_missing_dimensions_from_portrait(self):
        row = {"BFI-2 Open-Mindedness": "High"}
        out = schema._apply_personality({"personality": {}}, row, "tired")
        self.assertEqual(out["personality"]["big_five"]["openness"], 0.8)
        self.assertEqual(out["personality"]["big_five"]["conscientiousness"], 0.5)
        self.assertEqual(out["personality"]["energy_awareness"], "Low")

    def test_replaces_non_dict_personality(self):
        out = schema._apply_personality({"personality": "junk"}, None, "")
        self.assertIsInstance(out["personality"], dict)
        self.assertEqual(out["personality"]["big_five"], ALL_MID)


class NormalizeHelperTests(unittest.TestCase):
    def test_normalize_personal_appliances(self):
        members = [{"personal_appliances": ["Phone", {"type": "TV", "power": 1}, {"bad": 2}, 5]}]
        schema._normalize_personal_appliances(members)
        self.assertEqual(members[0]["personal_appliances"], [{"type": "Phone"}, {"type": "TV", "power": 1}])


class RowEnergyAwarenessTests(unittest.TestCase):
    def test_high_composite(self):
        row = {"Attitude: Renewable energy": "Enthusiast",
               "BFI-2 Conscientiousness": "Very high", "Energy level": "High"}
        self.assertEqual(schema._row_energy_awareness(row), "High")

    def test_low_composite(self):
        row = {"Attitude: Climate action": "Opposed",
               "BFI-2 Conscientiousness": "Very low"}
        self.assertEqual(schema._row_energy_awareness(row), "Low")

    def test_energy_only_moderate_is_medium(self):
        self.assertEqual(schema._row_energy_awareness({"Energy level": "Moderate"}), "Medium")

    def test_falls_back_to_bfi_energy_level(self):
        self.assertEqual(schema._row_energy_awareness({"BFI-2 Energy Level": "Very high"}), "High")

    def test_renewable_attitude_preferred_over_climate(self):
        row = {"Attitude: Renewable energy": "Opposed",
               "Attitude: Climate action": "Enthusiast",
               "BFI-2 Conscientiousness": "Average"}
        self.assertEqual(schema._row_energy_awareness(row), "Low")

    def test_no_components_returns_none(self):
        self.assertIsNone(schema._row_energy_awareness({}))
        self.assertIsNone(schema._row_energy_awareness(None))

    def test_conscientiousness_gives_variance_on_flat_energy_level(self):
        rows = [{"Energy level": "Moderate", "BFI-2 Conscientiousness": "Very high"},
                {"Energy level": "Moderate", "BFI-2 Conscientiousness": "Very low"}]
        self.assertEqual([schema._row_energy_awareness(r) for r in rows], ["High", "Low"])

    def test_attitude_scores(self):
        self.assertEqual(schema._score_attitude("Enthusiast"), 0.9)
        self.assertEqual(schema._score_attitude("neutral"), 0.5)
        self.assertIsNone(schema._score_attitude(None))
        self.assertIsNone(schema._score_attitude("unknown"))


if __name__ == "__main__":
    unittest.main()
