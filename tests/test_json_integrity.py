"""A world.json / district.json must survive a BOM, and a parse failure must never wipe it."""

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

from backend import world_admin  # noqa: E402

BOM = b"\xef\xbb\xbf"


class JsonIntegrityTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.worlds = os.path.join(self._tmp.name, "worlds")
        trash = os.path.join(self._tmp.name, "_trash")
        os.makedirs(self.worlds, exist_ok=True)
        self._patches = [
            mock.patch.object(gw, "WORLDS_DIR", self.worlds),
            mock.patch.object(gw, "TRASH_DIR", trash),
            mock.patch.object(world_admin, "WORLDS_DIR", self.worlds),
            mock.patch.object(world_admin, "TRASH_DIR", trash),
        ]
        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in self._patches:
            patch.stop()
        self._tmp.cleanup()

    def world_json(self, world_id="w1"):
        return os.path.join(self.worlds, world_id, "world.json")

    def write_raw(self, path, raw):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(raw)

    def read_json(self, path):
        with open(path, "r", encoding="utf-8-sig") as fh:
            return json.load(fh)

    def test_a_bom_is_tolerated_and_sibling_keys_survive_a_write(self):
        original = {
            "world_id": "w1",
            "world_config": "Melbourne",
            "created_at": "2026-01-01 00:00:00",
            "districts": [],
        }
        self.write_raw(self.world_json(), BOM + json.dumps(original).encode("utf-8"))

        gw.add_district("w1", "alpha")

        after = self.read_json(self.world_json())
        self.assertEqual(after["world_config"], "Melbourne")
        self.assertEqual(after["created_at"], "2026-01-01 00:00:00")
        self.assertEqual([entry["name"] for entry in after["districts"]], ["alpha"])

    def test_a_corrupt_world_json_is_refused_not_wiped(self):
        self.write_raw(self.world_json(), b"{ this is not json")

        with self.assertRaises(ValueError):
            gw.add_district("w1", "alpha")

        with open(self.world_json(), "rb") as fh:
            self.assertEqual(fh.read(), b"{ this is not json")

    def test_missing_files_still_read_as_none(self):
        missing = os.path.join(self.worlds, "w1", "world.json")
        self.assertIsNone(gw._read_json(missing))
        self.assertIsNone(world_admin.read_json(missing))

    def test_the_backend_reader_tolerates_a_bom_and_refuses_corruption(self):
        self.write_raw(self.world_json(), BOM + b'{"world_id": "w1"}')
        self.assertEqual(world_admin.read_json(self.world_json())["world_id"], "w1")

        self.write_raw(self.world_json(), b"nope")
        with self.assertRaises(ValueError):
            world_admin.read_json(self.world_json())


if __name__ == "__main__":
    unittest.main()
