"""L1 offline tests for stage-1 batch household descriptions + the stage reporting.

Zero API calls, temp directories only. Covers the new ``--count`` batch mode of
``s2_household_compose`` (N descriptions in ONE LLM call, numbering after the
existing houses, description-only records with ``status="described"`` and no
members / alignment artifacts), the count + response validation, the
``status="composed"`` stamp on the single-household path, the backend's
description-vs-members stage reporting and the ``--count`` argv forwarding.

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
DASHBOARD = os.path.join(PROJECT_ROOT, "dashboard")
for _path in (SRC, DASHBOARD):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import generate_world as gw  # noqa: E402
from steps.world import s2_household_compose as compose  # noqa: E402

from backend import build as build_module  # noqa: E402
from backend import models, world_admin  # noqa: E402


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _batch_payload(count, types=None):
    types = types if types is not None else ["Household Type %d" % i for i in range(1, count + 1)]
    return json.dumps({
        "households": [
            {
                "household_type": household_type,
                "member_count": (index % compose.MAX_MEMBERS) + 1,
                "description": "Description %d for this district." % index,
            }
            for index, household_type in enumerate(types, 1)
        ]
    })


def _compose_payload():
    return json.dumps({
        "household_type": "International Student Share House",
        "member_count": 2,
        "rationale": "Students dominate this district.",
    })


def _members_payload(member_count):
    return json.dumps({
        "members": [
            {"portrait": "Member %d portrait." % i, "age": 20 + i, "gender": "Female"}
            for i in range(1, member_count + 1)
        ]
    })


class _TempWorlds(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.worlds = os.path.join(self._tmp.name, "worlds")
        os.makedirs(self.worlds, exist_ok=True)
        self._patches = [
            mock.patch.object(gw, "WORLDS_DIR", self.worlds),
            mock.patch.object(world_admin, "WORLDS_DIR", self.worlds),
        ]
        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in self._patches:
            patch.stop()
        self._tmp.cleanup()

    def district_path(self, name="clayton"):
        return os.path.join(self.worlds, "w1", name)

    def house_path(self, house_id, name="clayton"):
        return os.path.join(self.district_path(name), house_id)

    def add_district(self, name="clayton", description="A dense student district."):
        gw.add_district("w1", name, description=description)

    def seed_house(self, house_id, record=None, name="clayton"):
        _write_json(os.path.join(self.house_path(house_id, name), "household.json"),
                    record or {"type": "Old Type", "members": [{"name": "Member 1"}]})


class BatchComposeTests(_TempWorlds):
    def test_batch_creates_n_numbered_dirs_with_described_records(self):
        self.add_district()
        self.seed_house("house_0001")
        self.seed_house("house_0003")
        with mock.patch.object(gw, "sample_personas",
                               side_effect=AssertionError("batch mode must not sample personas")), \
                mock.patch.object(compose.SubAgent, "single_call",
                                  return_value={"content": _batch_payload(3)}) as call:
            ok, msg = compose.run_step("w1", "clayton", count=3)

        self.assertTrue(ok)
        self.assertEqual(call.call_count, 1)
        self.assertIn("3 household descriptions written to", msg)
        self.assertIn(self.district_path(), msg)

        created = sorted(
            name for name in os.listdir(self.district_path())
            if name.startswith("house_") and os.path.isdir(os.path.join(self.district_path(), name))
        )
        self.assertEqual(created, ["house_0001", "house_0003", "house_0004", "house_0005", "house_0006"])

        for house_id in ("house_0004", "house_0005", "house_0006"):
            house = self.house_path(house_id)
            self.assertTrue(os.path.isdir(os.path.join(house, "log")))
            record = _read_json(os.path.join(house, "household.json"))
            self.assertEqual(record["status"], "described")
            self.assertNotIn("members", record)
            self.assertIsInstance(record["household_type"], str)
            self.assertIsInstance(record["member_count"], int)
            self.assertIsInstance(record["description"], str)
            self.assertFalse(os.path.isfile(os.path.join(house, "aligned_texts.json")))
            self.assertFalse(os.path.isfile(os.path.join(house, "persona_provenance.json")))

    def test_batch_appends_after_the_highest_existing_house(self):
        self.add_district()
        with mock.patch.object(compose.SubAgent, "single_call",
                               return_value={"content": _batch_payload(2)}):
            ok, _msg = compose.run_step("w1", "clayton", count=2)
        self.assertTrue(ok)
        first = _read_json(os.path.join(self.house_path("house_0001"), "household.json"))
        second = _read_json(os.path.join(self.house_path("house_0002"), "household.json"))
        self.assertEqual(first["household_type"], "Household Type 1")
        self.assertEqual(second["household_type"], "Household Type 2")

    def test_batch_prompt_receives_existing_count_and_types(self):
        self.add_district()
        self.seed_house("house_0001", {"type": "Retired Couple", "members": [{"name": "x"}]})
        captured = {}

        def fake_single_call(prompt, **kwargs):
            captured["prompt"] = prompt
            return {"content": _batch_payload(1)}

        with mock.patch.object(compose.SubAgent, "single_call", side_effect=fake_single_call):
            ok, _msg = compose.run_step("w1", "clayton", count=1)
        self.assertTrue(ok)
        self.assertIn("Retired Couple", captured["prompt"])
        self.assertIn("Households already present: 1", captured["prompt"])
        self.assertIn("exactly 1 households", captured["prompt"])


class BatchValidationTests(_TempWorlds):
    def _refuse(self, count):
        with mock.patch.object(compose.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            return compose.run_step("w1", "clayton", count=count)

    def test_invalid_counts_are_refused(self):
        self.add_district()
        for bad in (0, -1, 2.5, "3", True):
            ok, msg = self._refuse(bad)
            self.assertFalse(ok, bad)
            self.assertIn("positive integer", msg)

    def test_wrong_number_of_items_is_refused(self):
        self.add_district()
        with mock.patch.object(compose.SubAgent, "single_call",
                               return_value={"content": _batch_payload(2)}):
            ok, msg = compose.run_step("w1", "clayton", count=3)
        self.assertFalse(ok)
        self.assertIn("expected exactly 3", msg)
        self.assertFalse(os.path.isfile(os.path.join(self.house_path("house_0001"), "household.json")))

    def test_out_of_range_member_count_is_refused(self):
        self.add_district()
        payload = json.dumps({"households": [
            {"household_type": "Too Big", "member_count": compose.MAX_MEMBERS + 1, "description": "x"},
        ]})
        with mock.patch.object(compose.SubAgent, "single_call", return_value={"content": payload}):
            ok, msg = compose.run_step("w1", "clayton", count=1)
        self.assertFalse(ok)
        self.assertIn("member_count", msg)

    def test_missing_description_is_refused(self):
        self.add_district(description=None)
        with mock.patch.object(compose.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = compose.run_step("w1", "clayton", count=2)
        self.assertFalse(ok)
        self.assertEqual(msg, "district description missing; run the district-description step first")

    def test_invalid_json_is_refused(self):
        self.add_district()
        with mock.patch.object(compose.SubAgent, "single_call", return_value={"content": "{not json"}):
            ok, msg = compose.run_step("w1", "clayton", count=1)
        self.assertFalse(ok)
        self.assertIn("not valid JSON", msg)


class SingleComposeStageTests(_TempWorlds):
    def test_single_path_stamps_composed_status(self):
        self.add_district()
        texts = ["Member 1:\npersona", "Member 2:\npersona"]
        rows = [{"BFI-2 Conscientiousness": "High", "Energy level": "High"} for _ in range(2)]
        with mock.patch.object(gw, "sample_personas", return_value=(texts, rows)), \
                mock.patch.object(compose.SubAgent, "single_call",
                                  side_effect=[{"content": _compose_payload()},
                                               {"content": _members_payload(2)}]):
            ok, house_dir = compose.run_step("w1", "clayton")
        self.assertTrue(ok)
        household = _read_json(os.path.join(house_dir, "household.json"))
        self.assertEqual(household["status"], "composed")
        self.assertEqual(len(household["members"]), 2)


class StoredBriefTests(_TempWorlds):
    def _personas(self):
        texts = ["Member 1:\npersona", "Member 2:\npersona"]
        rows = [{"BFI-2 Conscientiousness": "High", "Energy level": "High"} for _ in range(2)]
        return texts, rows

    def test_described_household_composes_from_the_stored_brief_in_one_call(self):
        self.add_district()
        self.seed_house("house_0001", {"household_type": "Retired Couple", "member_count": 2,
                                       "description": "Two retired teachers.", "status": "described"})
        texts, rows = self._personas()
        captured = {}

        def fake_single_call(prompt, **kwargs):
            captured["prompt"] = prompt
            return {"content": _members_payload(2)}

        with mock.patch.object(gw, "sample_personas", return_value=(texts, rows)) as sample, \
                mock.patch.object(compose.SubAgent, "single_call", side_effect=fake_single_call) as call:
            ok, house_dir = compose.run_step("w1", "clayton", house=0)

        self.assertTrue(ok)
        self.assertEqual(call.call_count, 1)
        self.assertIn("Two retired teachers.", captured["prompt"])
        self.assertEqual(sample.call_args.kwargs.get("n"), 2)

        household = _read_json(os.path.join(house_dir, "household.json"))
        self.assertEqual(household["type"], "Retired Couple")
        self.assertEqual(len(household["members"]), 2)
        self.assertEqual(household["status"], "composed")
        provenance = _read_json(os.path.join(house_dir, "persona_provenance.json"))
        self.assertEqual(provenance["member_count"], 2)

    def test_legacy_record_without_a_brief_still_makes_two_calls(self):
        self.add_district()
        self.seed_house("house_0001")
        texts, rows = self._personas()
        with mock.patch.object(gw, "sample_personas", return_value=(texts, rows)), \
                mock.patch.object(compose.SubAgent, "single_call",
                                  side_effect=[{"content": _compose_payload()},
                                               {"content": _members_payload(2)}]) as call:
            ok, house_dir = compose.run_step("w1", "clayton", house=0)
        self.assertTrue(ok)
        self.assertEqual(call.call_count, 2)
        household = _read_json(os.path.join(house_dir, "household.json"))
        self.assertEqual(household["type"], "International Student Share House")
        self.assertEqual(household["status"], "composed")

    def test_missing_record_without_a_brief_still_makes_two_calls(self):
        self.add_district()
        texts, rows = self._personas()
        with mock.patch.object(gw, "sample_personas", return_value=(texts, rows)), \
                mock.patch.object(compose.SubAgent, "single_call",
                                  side_effect=[{"content": _compose_payload()},
                                               {"content": _members_payload(2)}]) as call:
            ok, _house_dir = compose.run_step("w1", "clayton", house=0)
        self.assertTrue(ok)
        self.assertEqual(call.call_count, 2)

    def test_stored_brief_accepts_a_full_record_and_strips(self):
        path = os.path.join(self.house_path("house_0001"), "household.json")
        _write_json(path, {"household_type": "  Retired Couple  ", "member_count": 2,
                           "description": "  Two retired teachers.  ", "status": "described"})
        self.assertEqual(compose._stored_brief(path), ("Retired Couple", 2, "Two retired teachers."))

    def test_stored_brief_accepts_legacy_type_and_story(self):
        path = os.path.join(self.house_path("house_0001"), "household.json")
        _write_json(path, {"type": "Legacy Type", "member_count": 3, "story": "Legacy story."})
        self.assertEqual(compose._stored_brief(path), ("Legacy Type", 3, "Legacy story."))

    def test_stored_brief_rejects_invalid_records(self):
        path = os.path.join(self.house_path("house_0001"), "household.json")
        self.assertIsNone(compose._stored_brief(path))
        records = [
            ["not", "a", "dict"],
            {"household_type": "T", "member_count": compose.MAX_MEMBERS + 1, "description": "d"},
            {"household_type": "T", "member_count": compose.MIN_MEMBERS - 1, "description": "d"},
            {"household_type": "T", "member_count": "2", "description": "d"},
            {"household_type": "T", "member_count": 2.0, "description": "d"},
            {"household_type": "T", "member_count": True, "description": "d"},
            {"member_count": 2, "description": "d"},
            {"household_type": "", "member_count": 2, "description": "d"},
            {"household_type": "T", "member_count": 2},
            {"household_type": "T", "member_count": 2, "description": ""},
        ]
        for record in records:
            _write_json(path, record)
            self.assertIsNone(compose._stored_brief(path), record)


class BackendStageTests(_TempWorlds):
    def setUp(self):
        super().setUp()
        os.makedirs(os.path.join(self.worlds, "w1"), exist_ok=True)
        _write_json(os.path.join(self.worlds, "w1", "world.json"),
                    {"world_id": "w1", "districts": []})
        self.add_district()
        _write_text(os.path.join(self.district_path(), "description.md"), "A dense student district.\n")
        world_admin.lock_district("w1", "clayton")

    def _household_step(self):
        state = world_admin.build_state("w1")
        steps = {step.step: step for step in state.steps}
        return steps["household"]

    def _status_for(self, house_id):
        step = self._household_step()
        return next(item for item in step.houses if item.house == house_id)

    def _home_status_for(self, house_id):
        state = world_admin.build_state("w1")
        step = next(item for item in state.steps if item.step == "home")
        return next(item for item in step.houses if item.house == house_id)

    def test_described_household_is_not_done_and_reports_stage(self):
        self.seed_house("house_0001", {"household_type": "Young DINK Couple", "member_count": 2,
                                       "description": "A couple.", "status": "described"})
        status = self._status_for("house_0001")
        self.assertEqual(status.stage, "described")
        self.assertFalse(status.done)
        self.assertFalse(self._household_step().done)

    def test_composed_household_is_done_and_reports_stage(self):
        self.seed_house("house_0001", {"type": "Young DINK Couple", "members": [{"name": "Member 1"}],
                                       "status": "composed"})
        status = self._status_for("house_0001")
        self.assertEqual(status.stage, "composed")
        self.assertTrue(status.done)
        self.assertTrue(self._household_step().done)

    def test_missing_household_reports_missing(self):
        os.makedirs(self.house_path("house_0001"), exist_ok=True)
        status = self._status_for("house_0001")
        self.assertEqual(status.stage, "missing")
        self.assertFalse(status.done)

    def test_empty_members_list_is_only_described(self):
        self.seed_house("house_0001", {"type": "Young DINK Couple", "members": []})
        status = self._status_for("house_0001")
        self.assertEqual(status.stage, "described")
        self.assertFalse(status.done)

    def test_home_is_blocked_until_the_household_has_members(self):
        self.seed_house("house_0001", {"household_type": "Young DINK Couple", "member_count": 2,
                                       "description": "A couple.", "status": "described"})
        home = self._home_status_for("house_0001")
        self.assertFalse(home.runnable)
        self.assertFalse(home.done)
        self.assertEqual(home.blocked_reason, world_admin.HOUSEHOLD_MEMBERS_REQUIRED_REASON)

    def test_home_becomes_runnable_once_members_exist(self):
        self.seed_house("house_0001", {"type": "Young DINK Couple",
                                       "members": [{"name": "Member 1"}], "status": "composed"})
        home = self._home_status_for("house_0001")
        self.assertTrue(home.runnable)
        self.assertIsNone(home.blocked_reason)

    def test_stage_field_is_part_of_the_contract(self):
        schema = models.HouseStepStatus.model_json_schema()
        self.assertIn("stage", schema["properties"])
        self.assertEqual(
            sorted(schema["properties"]["stage"]["enum"]),
            ["composed", "described", "missing"],
        )


class BuildArgvCountTests(_TempWorlds):
    def setUp(self):
        super().setUp()
        os.makedirs(os.path.join(self.worlds, "w1"), exist_ok=True)
        _write_json(os.path.join(self.worlds, "w1", "world.json"),
                    {"world_id": "w1", "districts": []})
        self.add_district()
        world_admin.lock_district("w1", "clayton")

    def _argv(self, **kwargs):
        request = models.JobRequest(kind="build", step="household", world="w1",
                                    district="clayton", confirm=True, **kwargs)
        argv, _warnings = build_module.build_step_argv(request)
        return argv

    def test_count_is_forwarded(self):
        argv = self._argv(count=4)
        self.assertIn("--count", argv)
        self.assertEqual(argv[argv.index("--count") + 1], "4")

    def test_count_absent_when_not_requested(self):
        self.assertNotIn("--count", self._argv())

    def test_batch_estimate_is_a_single_call(self):
        request = models.JobRequest(kind="build", step="household", world="w1",
                                    district="clayton", count=4, confirm=True)
        estimate = build_module.estimate_build(request)
        self.assertEqual(estimate.estimated_calls, 1)


if __name__ == "__main__":
    unittest.main()
