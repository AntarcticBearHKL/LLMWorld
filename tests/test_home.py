"""L1 offline tests for the home step (mocked LLM, 0 API calls).

Covers the "household.json missing" and LLM/JSON error paths, the successful
merge that writes the generated ``home`` while preserving ``type``, ``members``
and ``llm_generated``, the ``household.json.bak.<timestamp>`` backup, appliance
power backfill, the prompt's use of the shared appliance vocabulary, the house
selector (newest by default, explicit id) and the registered household meta
(``rooms_count``).

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import glob
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
from steps.world import s3_home as home  # noqa: E402


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _members():
    return [
        {
            "source_persona_index": index,
            "name": "Member %d" % index,
            "age": 28 + index,
            "gender": "Female" if index == 1 else "Male",
            "cultural_background": "",
            "bedroom": "Bedroom %d" % index,
            "occupation": "",
            "work_schedule": {},
            "personality": {"energy_awareness": "Medium",
                            "big_five": {"openness": 0.5, "conscientiousness": 0.5,
                                         "extraversion": 0.5, "agreeableness": 0.5,
                                         "neuroticism": 0.5}},
            "habits": {},
            "health": {},
            "personal_appliances": [],
        }
        for index in (1, 2)
    ]


def _household(members=None, household_type="Young DINK Couple"):
    return {
        "type": household_type,
        "llm_generated": True,
        "story": "A young couple in the district.",
        "members": _members() if members is None else members,
    }


def _home_payload(member_count=2):
    rooms = [
        {
            "name": "Bedroom %d" % index,
            "size": 12,
            "type": "bedroom",
            "appliances": [{"type": "Light", "brand": "Acme", "power": 40, "age": 2}],
        }
        for index in range(1, member_count + 1)
    ]
    rooms.append({
        "name": "Kitchen",
        "size": 18,
        "type": "kitchen",
        "appliances": [
            {"type": "Refrigerator", "brand": "Cool", "power": 100, "age": 3},
            {"type": "Kettle", "brand": "Boil", "power": 2000, "age": 1},
            {"type": "TV", "brand": "Vision", "power": 0, "age": 1},
        ],
    })
    rooms.append({
        "name": "Bathroom",
        "size": 8,
        "type": "bathroom",
        "appliances": [{"type": "WaterHeater", "brand": "Hot", "power": 3000, "age": 4}],
    })
    return json.dumps({
        "home": {"name": "Clayton Semi-Detached", "type": "House", "size": 160, "rooms": rooms}
    })


class HomeBase(unittest.TestCase):
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

    def house_dir(self, house_id="house_0001", name="clayton"):
        return os.path.join(self.district_path(name), house_id)

    def household_path(self, house_id="house_0001", name="clayton"):
        return os.path.join(self.house_dir(house_id, name), "household.json")

    def seed_household(self, house_id="house_0001", members=None, household_type="Young DINK Couple"):
        data = _household(members=members, household_type=household_type)
        _write_json(self.household_path(house_id), data)
        return data


class HomeSuccessTests(HomeBase):
    def test_success_merges_home_and_backs_up(self):
        self.add_district()
        original = self.seed_household()
        payload = _home_payload(2)
        with mock.patch.object(home.SubAgent, "single_call", return_value={"content": payload}):
            ok, house_dir = home.run_step("w1", "clayton")

        self.assertTrue(ok)
        self.assertEqual(house_dir, self.house_dir())

        merged = _read_json(self.household_path())
        self.assertIn("home", merged)
        self.assertEqual(merged["home"]["name"], "Clayton Semi-Detached")
        self.assertEqual(len(merged["home"]["rooms"]), 4)
        self.assertEqual(merged["type"], original["type"])
        self.assertTrue(merged["llm_generated"])
        self.assertEqual(merged["members"], original["members"])

        backups = glob.glob(self.household_path() + ".bak.*")
        self.assertEqual(len(backups), 1)
        self.assertEqual(_read_json(backups[0]), original)

        meta = _read_json(os.path.join(self.district_path(), "households.json"))
        self.assertEqual(len(meta["households"]), 1)
        self.assertEqual(meta["households"][0]["house_id"], "house_0001")
        self.assertEqual(meta["households"][0]["rooms_count"], 4)
        self.assertEqual(meta["households"][0]["members_count"], 2)

    def test_members_survive_merge(self):
        self.add_district()
        members = _members()
        self.seed_household(members=members)
        with mock.patch.object(home.SubAgent, "single_call",
                               return_value={"content": _home_payload(2)}):
            ok, _ = home.run_step("w1", "clayton")
        self.assertTrue(ok)
        merged = _read_json(self.household_path())
        self.assertEqual(merged["members"], members)
        self.assertEqual(len(merged["members"]), 2)

    def test_appliance_power_is_backfilled(self):
        self.add_district()
        self.seed_household()
        with mock.patch.object(home.SubAgent, "single_call",
                               return_value={"content": _home_payload(2)}):
            ok, _ = home.run_step("w1", "clayton")
        self.assertTrue(ok)
        merged = _read_json(self.household_path())
        for room in merged["home"]["rooms"]:
            for appliance in room["appliances"]:
                self.assertIsInstance(appliance["power"], int)
                self.assertGreater(appliance["power"], 0)
        kitchen = next(r for r in merged["home"]["rooms"] if r["name"] == "Kitchen")
        tv = next(a for a in kitchen["appliances"] if a["type"] == "TV")
        self.assertEqual(tv["power"], 150)

    def test_prompt_uses_district_household_and_appliance_vocabulary(self):
        self.add_district()
        self.seed_household(household_type="Family with Children")
        seen = {}

        def fake_single_call(prompt, **kwargs):
            seen["prompt"] = prompt
            return {"content": _home_payload(2)}

        with mock.patch.object(home.SubAgent, "single_call", side_effect=fake_single_call):
            ok, _ = home.run_step("w1", "clayton")
        self.assertTrue(ok)
        prompt = seen["prompt"]
        self.assertIn("Family with Children", prompt)
        self.assertIn("student district", prompt.lower())
        self.assertIn("Bedroom 1", prompt)
        self.assertIn("Refrigerator", prompt)
        self.assertIn("TV", prompt)


class HomeErrorTests(HomeBase):
    def test_household_missing(self):
        self.add_district()
        with mock.patch.object(home.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = home.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertEqual(msg, "household.json missing; run the household step first")

    def test_household_without_members(self):
        self.add_district()
        _write_json(self.household_path(), {"type": "X", "llm_generated": True, "members": []})
        with mock.patch.object(home.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = home.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertEqual(
            msg, "this household has no members yet: compose them before generating a home"
        )

    def test_missing_household_file(self):
        self.add_district()
        with mock.patch.object(home.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = home.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertEqual(msg, "household.json missing; run the household step first")

    def test_invalid_json_returns_false_and_leaves_file_untouched(self):
        self.add_district()
        original = self.seed_household()
        with mock.patch.object(home.SubAgent, "single_call", return_value={"content": "{not json"}):
            ok, msg = home.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertIn("not valid JSON", msg)
        self.assertEqual(_read_json(self.household_path()), original)
        self.assertEqual(glob.glob(self.household_path() + ".bak.*"), [])

    def test_home_without_rooms_is_rejected(self):
        self.add_district()
        self.seed_household()
        payload = json.dumps({"home": {"name": "Empty", "type": "Flat", "size": 40, "rooms": []}})
        with mock.patch.object(home.SubAgent, "single_call", return_value={"content": payload}):
            ok, msg = home.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertIn("rooms", msg)
        self.assertEqual(glob.glob(self.household_path() + ".bak.*"), [])

    def test_llm_error_returns_false_and_leaves_file_untouched(self):
        self.add_district()
        original = self.seed_household()
        with mock.patch.object(home.SubAgent, "single_call", side_effect=LLMCallError("boom")):
            ok, msg = home.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertEqual(msg, "boom")
        self.assertEqual(_read_json(self.household_path()), original)
        self.assertEqual(glob.glob(self.household_path() + ".bak.*"), [])

    def test_no_districts(self):
        os.makedirs(os.path.join(self.worlds, "empty"), exist_ok=True)
        _write_json(os.path.join(self.worlds, "empty", "world.json"),
                    {"world_id": "empty", "districts": []})
        with mock.patch.object(home.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = home.run_step("empty")
        self.assertFalse(ok)
        self.assertEqual(msg, "no districts in world empty")


class HomeSelectorTests(HomeBase):
    def test_default_selects_newest_household(self):
        self.add_district()
        self.seed_household("house_0001", household_type="Old Household")
        self.seed_household("house_0002", household_type="New Household")
        with mock.patch.object(home.SubAgent, "single_call",
                               return_value={"content": _home_payload(2)}):
            ok, house_dir = home.run_step("w1", "clayton")
        self.assertTrue(ok)
        self.assertEqual(house_dir, self.house_dir("house_0002"))
        self.assertIn("home", _read_json(self.household_path("house_0002")))
        self.assertNotIn("home", _read_json(self.household_path("house_0001")))

    def test_explicit_house_id_selects_that_household(self):
        self.add_district()
        self.seed_household("house_0001")
        self.seed_household("house_0002")
        with mock.patch.object(home.SubAgent, "single_call",
                               return_value={"content": _home_payload(2)}):
            ok, house_dir = home.run_step("w1", "clayton", "house_0001")
        self.assertTrue(ok)
        self.assertEqual(house_dir, self.house_dir("house_0001"))
        self.assertIn("home", _read_json(self.household_path("house_0001")))

    def test_invalid_house_selector(self):
        self.add_district()
        self.seed_household()
        with mock.patch.object(home.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = home.run_step("w1", "clayton", "nope")
        self.assertFalse(ok)
        self.assertIn("invalid house selector", msg)


class HomeCliTests(HomeBase):
    def test_all_iterates_every_district(self):
        self.add_district("clayton")
        self.add_district("dockside")
        calls = []

        def fake_run_step(world_id, district=None, house=None, *, seed=42):
            calls.append(district)
            return True, "ok"

        with mock.patch.object(home, "run_step", side_effect=fake_run_step), \
                mock.patch.object(sys, "argv", ["s3_home", "--world", "w1", "--all"]):
            with self.assertRaises(SystemExit) as ctx:
                home.main()
        self.assertEqual(ctx.exception.code, 0)
        self.assertEqual(sorted(calls), ["clayton", "dockside"])

    def test_failure_exits_nonzero(self):
        self.add_district("clayton")
        with mock.patch.object(home, "run_step", return_value=(False, "nope")), \
                mock.patch.object(sys, "argv", ["s3_home", "--world", "w1"]):
            with self.assertRaises(SystemExit) as ctx:
                home.main()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
