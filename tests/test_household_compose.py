"""L1 offline tests for the household-compose step (mocked LLM, 0 API calls).

Covers the composition call's shape validation and member-count bounds, that the
member count is wired through ``gw.sample_personas``, the alignment call (correct
count, retry-then-fallback, JSON failure), the "district description missing" and
"no districts" error paths, the successful writes (household.json /
aligned_texts.json / persona_provenance.json plus the registered household meta)
and the append-new versus overwrite house selectors.

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
from engine.subagent import LLMCallError  # noqa: E402
from steps.world import s2_household_compose as compose  # noqa: E402


MEMBER_KEYS = (
    "source_persona_index", "name", "age", "gender", "cultural_background",
    "bedroom", "occupation", "work_schedule", "personality", "habits",
    "health", "personal_appliances",
)


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _compose_payload(household_type="International Student Share House", member_count=2,
                     rationale="Students dominate this district."):
    return json.dumps({
        "household_type": household_type,
        "member_count": member_count,
        "rationale": rationale,
    })


def _members_payload(member_count):
    return json.dumps({
        "members": [
            {
                "portrait": "Member %d is a %d-year-old woman studying at the university."
                            % (i, 20 + i),
                "age": 20 + i,
                "gender": "Female",
            }
            for i in range(1, member_count + 1)
        ]
    })


def _sampled(member_count):
    texts = ["Member %d:\nPersona text %d" % (i, i) for i in range(1, member_count + 1)]
    rows = [{"BFI-2 Conscientiousness": "High", "Energy level": "High"}
            for _ in range(member_count)]
    return texts, rows


class ComposeBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.worlds = os.path.join(self._tmp.name, "worlds")
        os.makedirs(self.worlds, exist_ok=True)
        self._patch = mock.patch.object(gw, "WORLDS_DIR", self.worlds)
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        self._tmp.cleanup()

    def add_district(self, name="clayton",
                     description="A dense student district near the university."):
        gw.add_district("w1", name, description=description)

    def district_path(self, name="clayton"):
        return os.path.join(self.worlds, "w1", name)

    def house_path(self, house_id="house_0001", name="clayton"):
        return os.path.join(self.district_path(name), house_id)

    def run_compose(self, compose_payload, members_payload, *, member_count=2,
                    house=None, seed=7, district="clayton"):
        texts, rows = _sampled(member_count)
        with mock.patch.object(gw, "sample_personas", return_value=(texts, rows)) as sampler, \
                mock.patch.object(compose.SubAgent, "single_call",
                                  side_effect=[{"content": compose_payload},
                                               {"content": members_payload}]):
            result = compose.run_step("w1", district, house, seed=seed)
        return result, sampler, texts


class ComposeSuccessTests(ComposeBase):
    def test_success_writes_household_aligned_provenance_and_meta(self):
        self.add_district()
        (ok, house_dir), sampler, texts = self.run_compose(
            _compose_payload(member_count=2), _members_payload(2), member_count=2)

        self.assertTrue(ok)
        self.assertEqual(house_dir, self.house_path())

        household = _read_json(os.path.join(house_dir, "household.json"))
        self.assertEqual(household["type"], "International Student Share House")
        self.assertTrue(household["llm_generated"])
        self.assertNotIn("home", household)
        self.assertEqual(len(household["members"]), 2)

        first = household["members"][0]
        for key in MEMBER_KEYS:
            self.assertIn(key, first)
        self.assertEqual(first["source_persona_index"], 1)
        self.assertEqual(first["name"], "Member 1")
        self.assertEqual(first["age"], 21)
        self.assertEqual(first["gender"], "Female")
        self.assertEqual(first["bedroom"], "Bedroom 1")
        self.assertIsInstance(first["personal_appliances"], list)
        self.assertIn("energy_awareness", first["personality"])
        self.assertIn("big_five", first["personality"])

        aligned = _read_json(os.path.join(house_dir, "aligned_texts.json"))
        self.assertEqual(len(aligned), 2)

        provenance = _read_json(os.path.join(house_dir, "persona_provenance.json"))
        self.assertEqual(provenance["seed"], 7)
        self.assertEqual(provenance["member_count"], 2)
        self.assertEqual(provenance["source"], "llm")
        self.assertEqual(provenance["canonical_persona_texts"], texts)
        self.assertEqual(provenance["aligned_texts"], aligned)

        meta = _read_json(os.path.join(self.district_path(), "households.json"))
        entries = meta["households"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["house_id"], "house_0001")
        self.assertEqual(entries[0]["type"], "International Student Share House")
        self.assertEqual(entries[0]["members_count"], 2)
        self.assertEqual(entries[0]["rooms_count"], 0)

        sampler.assert_called_once()
        self.assertEqual(sampler.call_args.kwargs.get("n"), 2)

    def test_member_count_drives_sampling_and_household_type_is_passed(self):
        self.add_district()
        (ok, _), sampler, _ = self.run_compose(
            _compose_payload(household_type="Retired Couple", member_count=3),
            _members_payload(3), member_count=3)
        self.assertTrue(ok)
        args, kwargs = sampler.call_args
        household_type = args[0]
        self.assertEqual(household_type["type"], "Retired Couple")
        self.assertEqual(household_type["typical_members"], 3)
        self.assertEqual(kwargs.get("n"), 3)

    def test_custom_household_type_and_rationale(self):
        self.add_district()
        (ok, house_dir), _, _ = self.run_compose(
            _compose_payload("Single-Parent Family", 1, "A single parent with one child."),
            _members_payload(1), member_count=1)
        self.assertTrue(ok)
        household = _read_json(os.path.join(house_dir, "household.json"))
        self.assertEqual(household["type"], "Single-Parent Family")
        self.assertEqual(household["story"], "A single parent with one child.")


class ComposeValidationTests(ComposeBase):
    def test_member_count_above_max_is_rejected(self):
        self.add_district()
        with mock.patch.object(compose.SubAgent, "single_call",
                               return_value={"content": _compose_payload(member_count=9)}):
            ok, msg = compose.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertIn("member_count", msg)
        self.assertFalse(os.path.isfile(os.path.join(self.house_path(), "household.json")))

    def test_member_count_below_min_is_rejected(self):
        self.add_district()
        with mock.patch.object(compose.SubAgent, "single_call",
                               return_value={"content": _compose_payload(member_count=0)}):
            ok, msg = compose.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertIn("member_count", msg)

    def test_non_integer_member_count_is_rejected(self):
        self.add_district()
        payload = json.dumps({"household_type": "Retired Couple", "member_count": "two",
                              "rationale": "x"})
        with mock.patch.object(compose.SubAgent, "single_call", return_value={"content": payload}):
            ok, msg = compose.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertIn("integer", msg)

    def test_missing_household_type_is_rejected(self):
        self.add_district()
        payload = json.dumps({"member_count": 2, "rationale": "x"})
        with mock.patch.object(compose.SubAgent, "single_call", return_value={"content": payload}):
            ok, msg = compose.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertIn("household_type", msg)

    def test_invalid_json_is_rejected(self):
        self.add_district()
        with mock.patch.object(compose.SubAgent, "single_call", return_value={"content": "{not json"}):
            ok, msg = compose.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertIn("not valid JSON", msg)


class ComposeMemberTests(ComposeBase):
    def test_wrong_member_count_retries_then_falls_back(self):
        self.add_district()
        texts, rows = _sampled(2)
        wrong = _members_payload(3)
        with mock.patch.object(gw, "sample_personas", return_value=(texts, rows)), \
                mock.patch.object(compose.SubAgent, "single_call",
                                  side_effect=[{"content": _compose_payload(member_count=2)},
                                               {"content": wrong},
                                               {"content": wrong},
                                               {"content": wrong}]) as call:
            ok, house_dir = compose.run_step("w1", "clayton")

        self.assertTrue(ok)
        self.assertEqual(call.call_count, 1 + compose.MAX_MEMBER_ATTEMPTS)
        provenance = _read_json(os.path.join(house_dir, "persona_provenance.json"))
        self.assertEqual(provenance["source"], "fallback")
        self.assertEqual(provenance["aligned_texts"], texts)
        household = _read_json(os.path.join(house_dir, "household.json"))
        self.assertEqual(len(household["members"]), 2)

    def test_duplicate_portraits_fall_back(self):
        self.add_district()
        texts, rows = _sampled(2)
        duplicate = json.dumps({"members": [
            {"portrait": "Same portrait.", "age": 20, "gender": "Female"},
            {"portrait": "Same portrait.", "age": 21, "gender": "Male"},
        ]})
        with mock.patch.object(gw, "sample_personas", return_value=(texts, rows)), \
                mock.patch.object(compose.SubAgent, "single_call",
                                  side_effect=[{"content": _compose_payload(member_count=2)},
                                               {"content": duplicate},
                                               {"content": duplicate},
                                               {"content": duplicate}]):
            ok, house_dir = compose.run_step("w1", "clayton")
        self.assertTrue(ok)
        provenance = _read_json(os.path.join(house_dir, "persona_provenance.json"))
        self.assertEqual(provenance["source"], "fallback")

    def test_members_json_failure_returns_false(self):
        self.add_district()
        texts, rows = _sampled(2)
        with mock.patch.object(gw, "sample_personas", return_value=(texts, rows)), \
                mock.patch.object(compose.SubAgent, "single_call",
                                  side_effect=[{"content": _compose_payload(member_count=2)},
                                               {"content": "{broken"}]) as call:
            ok, msg = compose.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertIn("not valid JSON", msg)
        self.assertEqual(call.call_count, 2)
        self.assertFalse(os.path.isfile(os.path.join(self.house_path(), "household.json")))


class ComposeErrorPathTests(ComposeBase):
    def test_district_description_missing(self):
        self.add_district(description=None)
        with mock.patch.object(compose.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = compose.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertEqual(msg, "district description missing; run the district-description step first")

    def test_no_districts(self):
        os.makedirs(os.path.join(self.worlds, "empty"), exist_ok=True)
        _write_json(os.path.join(self.worlds, "empty", "world.json"),
                    {"world_id": "empty", "districts": []})
        with mock.patch.object(compose.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = compose.run_step("empty")
        self.assertFalse(ok)
        self.assertEqual(msg, "no districts in world empty")

    def test_llm_error_returns_false_and_writes_nothing(self):
        self.add_district()
        with mock.patch.object(compose.SubAgent, "single_call", side_effect=LLMCallError("boom")):
            ok, msg = compose.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertEqual(msg, "boom")
        self.assertFalse(os.path.isfile(os.path.join(self.house_path(), "household.json")))

    def test_invalid_house_selector(self):
        self.add_district()
        with mock.patch.object(compose.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = compose.run_step("w1", "clayton", "not-a-house")
        self.assertFalse(ok)
        self.assertIn("invalid house selector", msg)


class ComposeHouseSelectorTests(ComposeBase):
    def _seed_household(self, house_id):
        _write_json(os.path.join(self.house_path(house_id), "household.json"),
                    {"type": "Old Type", "llm_generated": True, "members": ["old"]})

    def test_none_appends_next_free_house(self):
        self.add_district()
        self._seed_household("house_0001")
        (ok, house_dir), _, _ = self.run_compose(
            _compose_payload(member_count=1), _members_payload(1), member_count=1, house=None)
        self.assertTrue(ok)
        self.assertEqual(house_dir, self.house_path("house_0002"))
        self.assertTrue(os.path.isfile(os.path.join(self.house_path("house_0002"), "household.json")))

    def test_int_selector_overwrites_existing_house(self):
        self.add_district()
        self._seed_household("house_0002")
        (ok, house_dir), _, _ = self.run_compose(
            _compose_payload(member_count=1), _members_payload(1), member_count=1, house=1)
        self.assertTrue(ok)
        self.assertEqual(house_dir, self.house_path("house_0002"))
        household = _read_json(os.path.join(house_dir, "household.json"))
        self.assertNotEqual(household["type"], "Old Type")

    def test_string_selector_overwrites_existing_house(self):
        self.add_district()
        self._seed_household("house_0001")
        (ok, house_dir), _, _ = self.run_compose(
            _compose_payload(member_count=1), _members_payload(1), member_count=1,
            house="house_0001")
        self.assertTrue(ok)
        self.assertEqual(house_dir, self.house_path("house_0001"))

    def test_overwrite_replaces_meta_entry(self):
        self.add_district()
        self._seed_household("house_0001")
        _write_json(os.path.join(self.district_path(), "households.json"),
                    {"households": [{"house_id": "house_0001", "type": "Old Type",
                                     "members_count": 5, "rooms_count": 9}]})
        (ok, _), _, _ = self.run_compose(
            _compose_payload(member_count=1), _members_payload(1), member_count=1,
            house="house_0001")
        self.assertTrue(ok)
        meta = _read_json(os.path.join(self.district_path(), "households.json"))
        self.assertEqual(len(meta["households"]), 1)
        self.assertEqual(meta["households"][0]["members_count"], 1)


class ComposeCliTests(ComposeBase):
    def test_all_iterates_every_district(self):
        self.add_district("clayton")
        self.add_district("dockside")
        calls = []

        def fake_run_step(world_id, district=None, house=None, *, seed=42):
            calls.append(district)
            return True, "ok"

        with mock.patch.object(compose, "run_step", side_effect=fake_run_step), \
                mock.patch.object(sys, "argv",
                                  ["s2_household_compose", "--world", "w1", "--all"]):
            with self.assertRaises(SystemExit) as ctx:
                compose.main()
        self.assertEqual(ctx.exception.code, 0)
        self.assertEqual(sorted(calls), ["clayton", "dockside"])

    def test_failure_exits_nonzero(self):
        self.add_district("clayton")
        with mock.patch.object(compose, "run_step", return_value=(False, "nope")), \
                mock.patch.object(sys, "argv", ["s2_household_compose", "--world", "w1"]):
            with self.assertRaises(SystemExit) as ctx:
                compose.main()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
