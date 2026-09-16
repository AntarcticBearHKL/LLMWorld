"""L1 offline tests for named districts in generate_world.

Zero API calls, zero LLM. Covers the district identifier refactor: districts()
resolution (world.json names, child-dir fallback, legacy postcodes),
primary_district/district_dir, add_district (create + idempotency + validation),
remove_district (recoverable + permanent), init_world scaffolding and
load_district_text.

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


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class DistrictBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.worlds = os.path.join(self._tmp.name, "worlds")
        self.trash = os.path.join(self._tmp.name, "_trash")
        os.makedirs(self.worlds, exist_ok=True)
        self._patches = [
            mock.patch.object(gw, "WORLDS_DIR", self.worlds),
            mock.patch.object(gw, "TRASH_DIR", self.trash),
        ]
        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in self._patches:
            patch.stop()
        self._tmp.cleanup()

    def world_dir(self, world_id="w1"):
        path = os.path.join(self.worlds, world_id)
        os.makedirs(path, exist_ok=True)
        return path


class DistrictsTests(DistrictBase):
    def test_missing_world_is_empty(self):
        self.assertEqual(gw.districts("nope"), [])
        self.assertEqual(gw.primary_district("nope"), "")

    def test_reads_names_from_world_json(self):
        _write_json(os.path.join(self.world_dir(), "world.json"),
                    {"world_id": "w1", "districts": [{"name": "clayton"}, {"name": "dockside"}]})
        self.assertEqual(gw.districts("w1"), ["clayton", "dockside"])
        self.assertEqual(gw.primary_district("w1"), "clayton")

    def test_legacy_postcode_entries_still_resolve(self):
        _write_json(os.path.join(self.world_dir(), "world.json"),
                    {"world_id": "w1", "districts": [{"postcode": "3168"}]})
        self.assertEqual(gw.districts("w1"), ["3168"])

    def test_falls_back_to_child_dirs_ignoring_log(self):
        world = self.world_dir()
        os.makedirs(os.path.join(world, "3168"))
        os.makedirs(os.path.join(world, "dockside"))
        os.makedirs(os.path.join(world, "log"))
        _write_json(os.path.join(world, "world.json"), {"world_id": "w1", "districts": []})
        self.assertEqual(gw.districts("w1"), ["3168", "dockside"])
        self.assertEqual(gw.primary_district("w1"), "3168")

    def test_empty_districts_list_is_empty(self):
        world = self.world_dir()
        os.makedirs(os.path.join(world, "log"))
        _write_json(os.path.join(world, "world.json"), {"world_id": "w1", "districts": []})
        self.assertEqual(gw.districts("w1"), [])

    def test_district_dir_uses_primary_or_explicit(self):
        world = self.world_dir()
        _write_json(os.path.join(world, "world.json"),
                    {"world_id": "w1", "districts": [{"name": "clayton"}]})
        self.assertEqual(gw.district_dir("w1"), os.path.join(world, "clayton"))
        self.assertEqual(gw.district_dir("w1", "dockside"), os.path.join(world, "dockside"))


class AddDistrictTests(DistrictBase):
    def test_creates_dir_meta_and_registers(self):
        self.world_dir()
        result = gw.add_district("w1", "clayton", description="student suburb")
        self.assertTrue(result["created"])
        district = os.path.join(self.worlds, "w1", "clayton")
        self.assertTrue(os.path.isdir(district))
        with open(os.path.join(district, "district.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["name"], "clayton")
        self.assertEqual(meta["description"], "student suburb")
        self.assertIn("created_at", meta)
        with open(os.path.join(self.worlds, "w1", "world.json"), encoding="utf-8") as f:
            world = json.load(f)
        self.assertEqual([entry["name"] for entry in world["districts"]], ["clayton"])
        self.assertEqual(gw.districts("w1"), ["clayton"])

    def test_idempotent_keeps_first_metadata(self):
        self.world_dir()
        gw.add_district("w1", "clayton", description="first")
        result = gw.add_district("w1", "clayton", description="second")
        self.assertFalse(result["created"])
        with open(os.path.join(self.worlds, "w1", "clayton", "district.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["description"], "first")
        self.assertEqual(gw.districts("w1"), ["clayton"])

    def test_two_districts_keep_registration_order(self):
        self.world_dir()
        gw.add_district("w1", "clayton")
        gw.add_district("w1", "dockside")
        self.assertEqual(gw.districts("w1"), ["clayton", "dockside"])
        self.assertEqual(gw.primary_district("w1"), "clayton")

    def test_invalid_names_rejected(self):
        self.world_dir()
        for bad in ("", "   ", ".", "..", "-lead", "bad/name", "a b"):
            with self.assertRaises(ValueError):
                gw.add_district("w1", bad)

    def test_does_not_overwrite_existing_district_json(self):
        district = os.path.join(self.world_dir(), "3168")
        os.makedirs(district)
        legacy = {"postcode": "3168", "description": "legacy"}
        _write_json(os.path.join(district, "district.json"), legacy)
        result = gw.add_district("w1", "3168")
        self.assertTrue(result["created"])
        with open(os.path.join(district, "district.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f), legacy)


class RemoveDistrictTests(DistrictBase):
    def test_recoverable_move_to_trash(self):
        self.world_dir()
        gw.add_district("w1", "clayton")
        gw.add_district("w1", "dockside")
        result = gw.remove_district("w1", "clayton")
        self.assertTrue(result["existed"])
        self.assertFalse(os.path.isdir(os.path.join(self.worlds, "w1", "clayton")))
        self.assertTrue(result["moved_to"] and os.path.isdir(result["moved_to"]))
        self.assertTrue(result["moved_to"].startswith(os.path.abspath(self.trash)))
        self.assertEqual(gw.districts("w1"), ["dockside"])

    def test_permanent_delete(self):
        self.world_dir()
        gw.add_district("w1", "clayton")
        result = gw.remove_district("w1", "clayton", permanent=True)
        self.assertIsNone(result["moved_to"])
        self.assertFalse(os.path.isdir(os.path.join(self.worlds, "w1", "clayton")))
        self.assertEqual(gw.districts("w1"), [])

    def test_missing_district_is_noop(self):
        self.world_dir()
        result = gw.remove_district("w1", "ghost")
        self.assertFalse(result["existed"])
        self.assertEqual(gw.districts("w1"), [])


class ListHousesTests(DistrictBase):
    def test_resolves_named_district(self):
        self.world_dir()
        gw.add_district("w1", "clayton")
        house = os.path.join(self.worlds, "w1", "clayton", "house_0001")
        os.makedirs(house)
        _write_json(os.path.join(house, "household.json"), {"home": {}, "members": []})
        self.assertEqual(gw.list_houses("w1"), ["house_0001"])
        self.assertEqual(gw.list_houses("w1", "dockside"), [])


class InitWorldTests(DistrictBase):
    def setUp(self):
        super().setUp()
        self.config_root = os.path.join(self._tmp.name, "import_world")
        district = os.path.join(self.config_root, "Melbourne", "clayton")
        os.makedirs(district)
        with open(os.path.join(district, "info.md"), "w", encoding="utf-8") as f:
            f.write("A student suburb.")
        self._config_patch = mock.patch.object(gw, "WORLD_CONFIG_DIR", self.config_root)
        self._config_patch.start()

    def tearDown(self):
        self._config_patch.stop()
        super().tearDown()

    def test_init_creates_empty_districts_and_world_log(self):
        world_dir, log_dir = gw.init_world("w1", "Melbourne")
        self.assertTrue(os.path.isdir(log_dir))
        self.assertEqual(os.path.abspath(log_dir), os.path.abspath(os.path.join(world_dir, "log")))
        with open(os.path.join(world_dir, "world.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["world_config"], "Melbourne")
        self.assertEqual(meta["districts"], [])
        self.assertEqual(gw.districts("w1"), [])

    def test_init_keeps_existing_districts(self):
        self.world_dir()
        gw.add_district("w1", "clayton")
        gw.init_world("w1", "Melbourne")
        self.assertEqual(gw.districts("w1"), ["clayton"])

    def test_load_district_text_present_missing_and_none(self):
        self.assertEqual(gw.load_district_text("clayton", "Melbourne"), "A student suburb.")
        self.assertEqual(gw.load_district_text("ghost", "Melbourne"), "")
        self.assertEqual(gw.load_district_text(None, "Melbourne"), "")


if __name__ == "__main__":
    unittest.main()
