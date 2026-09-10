"""L1 offline tests for Feature B2: persona-grounded personality + room dedup.

Zero API calls. Covers the pure logic added to steps/world/s3_household_build.py
(Big Five / energy_awareness derivation from the sampled persona row or portrait,
redundant shared-room removal) and its small normalisation helpers.

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

import steps.world.s3_household_build as s3  # noqa: E402
import generate_world as gw  # noqa: E402


ALL_MID = {"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5,
           "agreeableness": 0.5, "neuroticism": 0.5}


class MarkerHitTests(unittest.TestCase):
    def test_counts_whole_words_only(self):
        self.assertEqual(s3._marker_hits("i am curious and creative", ("curious", "creative")), 2)
        self.assertEqual(s3._marker_hits("curiously", ("curious",)), 0)

    def test_case_insensitive_via_caller(self):
        self.assertEqual(s3._marker_hits("calm and CALM", ("calm",)), 1)


class PortraitBigFiveTests(unittest.TestCase):
    def test_neutral_portrait_is_midpoint(self):
        self.assertEqual(s3._portrait_big_five(""), ALL_MID)
        self.assertEqual(s3._portrait_big_five(None), ALL_MID)

    def test_single_markers_shift_by_point_one(self):
        scores = s3._portrait_big_five("organized, curious, outgoing, kind, calm")
        self.assertEqual(scores, {"openness": 0.6, "conscientiousness": 0.6,
                                  "extraversion": 0.6, "agreeableness": 0.6, "neuroticism": 0.4})

    def test_positive_clamped_at_max(self):
        text = "curious creative imaginative artistic open-minded intellectual adventurous aesthetic philosophical exploratory"
        self.assertEqual(s3._portrait_big_five(text)["openness"], 0.9)

    def test_negative_clamped_at_min(self):
        text = "conventional traditional routine practical predictable"
        self.assertEqual(s3._portrait_big_five(text)["openness"], 0.1)

    def test_deterministic(self):
        text = "curious and organized but also anxious"
        self.assertEqual(s3._portrait_big_five(text), s3._portrait_big_five(text))


class PortraitEnergyTests(unittest.TestCase):
    def test_high(self):
        self.assertEqual(s3._portrait_energy_awareness("energetic and very active"), "High")

    def test_low(self):
        self.assertEqual(s3._portrait_energy_awareness("tired and exhausted"), "Low")

    def test_neutral(self):
        self.assertEqual(s3._portrait_energy_awareness(""), "Medium")

    def test_tie_defaults_medium(self):
        self.assertEqual(s3._portrait_energy_awareness("energetic tired"), "Medium")


class LevelMapTests(unittest.TestCase):
    def test_level_to_score(self):
        self.assertEqual(s3._level_to_score("Very High"), 0.9)
        self.assertEqual(s3._level_to_score("moderate"), 0.5)
        self.assertEqual(s3._level_to_score(" Slightly Low "), 0.35)
        self.assertIsNone(s3._level_to_score(None))
        self.assertIsNone(s3._level_to_score("zzz"))

    def test_level_to_awareness(self):
        self.assertEqual(s3._level_to_awareness("very low"), "Low")
        self.assertEqual(s3._level_to_awareness("slightly high"), "Medium")
        self.assertEqual(s3._level_to_awareness("excellent"), "High")
        self.assertIsNone(s3._level_to_awareness(None))


class ApplyPersonalityTests(unittest.TestCase):
    def test_prefers_persona_row(self):
        row = {"BFI-2 Open-Mindedness": "High", "BFI-2 Conscientiousness": "Very High",
               "BFI-2 Extraversion": "Low", "BFI-2 Agreeableness": "Average",
               "BFI-2 Negative Emotionality": "Slightly Low", "Energy level": "High"}
        member = {"personality": {"traits": ["x"]}}
        out = s3._apply_personality(member, row, "ignored portrait")
        self.assertEqual(out["personality"]["big_five"],
                         {"openness": 0.8, "conscientiousness": 0.9, "extraversion": 0.25,
                          "agreeableness": 0.5, "neuroticism": 0.35})
        self.assertEqual(out["personality"]["energy_awareness"], "High")
        self.assertEqual(out["personality"]["traits"], ["x"])

    def test_falls_back_to_portrait_when_no_row(self):
        out = s3._apply_personality({"personality": {}}, None, "curious")
        self.assertEqual(out["personality"]["big_five"]["openness"], 0.6)
        self.assertEqual(out["personality"]["energy_awareness"], "Medium")

    def test_fills_missing_dimensions_from_portrait(self):
        row = {"BFI-2 Open-Mindedness": "High"}
        out = s3._apply_personality({"personality": {}}, row, "tired")
        self.assertEqual(out["personality"]["big_five"]["openness"], 0.8)
        self.assertEqual(out["personality"]["big_five"]["conscientiousness"], 0.5)
        self.assertEqual(out["personality"]["energy_awareness"], "Low")

    def test_replaces_non_dict_personality(self):
        out = s3._apply_personality({"personality": "junk"}, None, "")
        self.assertIsInstance(out["personality"], dict)
        self.assertEqual(out["personality"]["big_five"], ALL_MID)


class RoomHelperTests(unittest.TestCase):
    def test_room_family_set_ignores_junk(self):
        room = {"appliances": [{"type": "Laptop"}, {"type": "TV"}, {"bad": 1}, "Phone"]}
        self.assertEqual(s3._room_family_set(room), {"Computer", "TV"})

    def test_protected_rooms(self):
        for name in ("Bedroom 1", "Living Room", "Kitchen", "Bathroom"):
            self.assertTrue(s3._is_protected_room(name), name)
        for name in ("Study", "Laundry", "Garage", ""):
            self.assertFalse(s3._is_protected_room(name), name)


class DropRedundantRoomsTests(unittest.TestCase):
    def test_keeps_only_shared_room_when_it_would_be_the_last(self):
        home = {"rooms": [{"name": "Kitchen", "appliances": [{"type": "TV"}]},
                          {"name": "Study", "appliances": [{"type": "TV"}]}]}
        s3._drop_redundant_rooms(home)
        self.assertEqual([r["name"] for r in home["rooms"]], ["Kitchen", "Study"])

    def test_removes_duplicate_shared_room(self):
        home = {"rooms": [{"name": "Kitchen", "appliances": [{"type": "TV"}]},
                          {"name": "Living Room", "appliances": [{"type": "TV"}]},
                          {"name": "Study", "appliances": [{"type": "TV"}]}]}
        s3._drop_redundant_rooms(home)
        self.assertEqual([r["name"] for r in home["rooms"]], ["Kitchen", "Living Room"])

    def test_empty_candidate_not_removed(self):
        home = {"rooms": [{"name": "Kitchen", "appliances": [{"type": "TV"}]},
                          {"name": "Study", "appliances": []}]}
        s3._drop_redundant_rooms(home)
        self.assertEqual([r["name"] for r in home["rooms"]], ["Kitchen", "Study"])

    def test_only_protected_rooms_untouched(self):
        home = {"rooms": [{"name": "Kitchen", "appliances": [{"type": "TV"}]},
                          {"name": "Bathroom", "appliances": [{"type": "TV"}]}]}
        s3._drop_redundant_rooms(home)
        self.assertEqual(len(home["rooms"]), 2)

    def test_non_list_rooms_untouched(self):
        home = {"rooms": "broken"}
        self.assertIs(s3._drop_redundant_rooms(home), home)


class NormalizeHelperTests(unittest.TestCase):
    def test_normalize_personal_appliances(self):
        members = [{"personal_appliances": ["Phone", {"type": "TV", "power": 1}, {"bad": 2}, 5]}]
        s3._normalize_personal_appliances(members)
        self.assertEqual(members[0]["personal_appliances"], [{"type": "Phone"}, {"type": "TV", "power": 1}])

    def test_normalize_type(self):
        out = s3.normalize_type({"household_type": "family", "typical_housing": "house"})
        self.assertEqual(out["type"], "family")
        self.assertEqual(out["housing_hint"], "house")


class LoadPersonaRowsTests(unittest.TestCase):
    def _write(self, house_dir, name, payload):
        with open(os.path.join(house_dir, name), "w", encoding="utf-8") as f:
            json.dump(payload, f)

    def test_uses_matching_cache_and_provenance_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "persona_provenance.json", {"seed": 7})
            self._write(tmp, "persona_rows.json",
                        {"aligned_texts": ["a", "b"], "rows": [{"id": 1}, {"id": 2}, {"id": 3}]})
            rows, seed = s3._load_persona_rows(tmp, {"type": "x"}, 2, 42, ["a", "b"])
            self.assertEqual(seed, 7)
            self.assertEqual(rows, [{"id": 1}, {"id": 2}])

    def test_cache_mismatch_resamples(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "persona_provenance.json", {"seed": 7})
            self._write(tmp, "persona_rows.json",
                        {"aligned_texts": ["stale"], "rows": [{"id": 1}]})
            with mock.patch.object(gw, "sample_personas",
                                   return_value=([], [{"id": 9}, {"id": 10}])):
                rows, seed = s3._load_persona_rows(tmp, {"type": "x"}, 2, 42, ["a", "b"])
            self.assertEqual(seed, 7)
            self.assertEqual(rows, [{"id": 9}, {"id": 10}])

    def test_resample_failure_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(gw, "sample_personas", side_effect=RuntimeError("boom")):
                rows, seed = s3._load_persona_rows(tmp, {"type": "x"}, 1, 42, ["a"])
            self.assertEqual(rows, [])
            self.assertEqual(seed, 42)

    def test_corrupt_files_fall_back_to_default_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "persona_provenance.json"), "w", encoding="utf-8") as f:
                f.write("{not json")
            with open(os.path.join(tmp, "persona_rows.json"), "w", encoding="utf-8") as f:
                f.write("{not json")
            with mock.patch.object(gw, "sample_personas", return_value=([], [{"id": 1}])):
                rows, seed = s3._load_persona_rows(tmp, {"type": "x"}, 1, 42, ["a"])
            self.assertEqual(seed, 42)
            self.assertEqual(rows, [{"id": 1}])


if __name__ == "__main__":
    unittest.main()
