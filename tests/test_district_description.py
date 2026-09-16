"""L1 offline tests for the district-description step (mocked LLM, 0 API calls).

Covers preset loading (real file + missing/malformed), resolve_prompt precedence
(custom > preset id > default), a successful run_step write (description.md plus
a district.json merge that keeps unrelated keys), the LLMCallError path
(returns (False, msg) and writes nothing) and the no-districts error path.

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
from steps.world import s1_district_description as dd  # noqa: E402


FIXTURE_PRESETS = [
    {"id": "first", "title": "First", "description": "first preset", "prompt": "FIRST PROMPT"},
    {"id": "second", "title": "Second", "description": "second preset", "prompt": "SECOND PROMPT"},
]


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class PresetFileTests(unittest.TestCase):
    def test_real_file_has_expected_presets(self):
        presets = dd.load_presets()
        ids = [p["id"] for p in presets]
        self.assertIn("clayton_3168", ids)
        self.assertGreaterEqual(len(presets), 3)
        for preset in presets:
            self.assertTrue(preset["title"])
            self.assertTrue(preset["description"])
            self.assertTrue(preset["prompt"])
        clayton = next(p for p in presets if p["id"] == "clayton_3168")
        self.assertIn("Australian Bureau of Statistics", clayton["prompt"])
        self.assertIn("21,880", clayton["prompt"])
        self.assertIn("talent incubator", clayton["prompt"])

    def test_missing_file_returns_empty(self):
        missing = os.path.join(tempfile.gettempdir(), "llmworld_no_such_presets.json")
        with mock.patch.object(dd, "PRESETS_PATH", missing):
            self.assertEqual(dd.load_presets(), [])

    def test_malformed_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{not json")
            with mock.patch.object(dd, "PRESETS_PATH", path):
                self.assertEqual(dd.load_presets(), [])

    def test_non_list_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "obj.json")
            _write_json(path, {"id": "x"})
            with mock.patch.object(dd, "PRESETS_PATH", path):
                self.assertEqual(dd.load_presets(), [])

    def test_list_presets_cli_exits_zero_without_world(self):
        with mock.patch.object(sys, "argv", ["s1_district_description", "--list-presets"]):
            with self.assertRaises(SystemExit) as ctx:
                dd.main()
        self.assertEqual(ctx.exception.code, 0)


class DistrictDescriptionBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.worlds = os.path.join(self._tmp.name, "worlds")
        self.trash = os.path.join(self._tmp.name, "_trash")
        os.makedirs(self.worlds, exist_ok=True)
        self._patches = [
            mock.patch.object(gw, "WORLDS_DIR", self.worlds),
            mock.patch.object(gw, "TRASH_DIR", self.trash),
            mock.patch.object(dd, "PRESETS_PATH", os.path.join(self._tmp.name, "presets.json")),
        ]
        for patch in self._patches:
            patch.start()
        _write_json(os.path.join(self._tmp.name, "presets.json"), FIXTURE_PRESETS)

    def tearDown(self):
        for patch in self._patches:
            patch.stop()
        self._tmp.cleanup()

    def add_district(self, name="clayton", meta=None):
        gw.add_district("w1", name)
        if meta is not None:
            _write_json(os.path.join(self.worlds, "w1", name, "district.json"), meta)

    def district_json(self, name="clayton"):
        return os.path.join(self.worlds, "w1", name, "district.json")

    def description_md(self, name="clayton"):
        return os.path.join(self.worlds, "w1", name, "description.md")


class ResolvePromptTests(DistrictDescriptionBase):
    def test_custom_wins_over_preset(self):
        self.assertEqual(dd.resolve_prompt("second", "CUSTOM"), ("CUSTOM", "custom"))

    def test_preset_id_resolves(self):
        self.assertEqual(dd.resolve_prompt("second"), ("SECOND PROMPT", "second"))

    def test_default_is_first_preset(self):
        self.assertEqual(dd.resolve_prompt(), ("FIRST PROMPT", "default"))

    def test_unknown_preset_falls_back_to_default(self):
        self.assertEqual(dd.resolve_prompt("ghost"), ("FIRST PROMPT", "default"))

    def test_blank_custom_prompt_falls_through_to_preset(self):
        self.assertEqual(dd.resolve_prompt("second", "   "), ("SECOND PROMPT", "second"))


class RunStepTests(DistrictDescriptionBase):
    def test_success_writes_description_and_merges_meta(self):
        self.add_district(meta={"name": "clayton", "population": 1234, "created_at": "old"})
        seen = {}

        def fake_single_call(prompt):
            seen["prompt"] = prompt
            return {"content": "  A young rental district near the university.  ", "reasoning_content": ""}

        with mock.patch.object(dd.SubAgent, "single_call", side_effect=fake_single_call):
            ok, text = dd.run_step("w1", "clayton", preset="second", seed=7)

        self.assertTrue(ok)
        self.assertEqual(text, "A young rental district near the university.")
        self.assertTrue(os.path.isfile(self.description_md()))
        with open(self.description_md(), encoding="utf-8") as f:
            self.assertEqual(f.read().strip(), text)

        meta = _read_json(self.district_json())
        self.assertEqual(meta["description"], text)
        self.assertEqual(meta["description_source"], "second")
        self.assertTrue(meta["description_updated_at"])
        self.assertEqual(meta["population"], 1234)
        self.assertEqual(meta["name"], "clayton")
        self.assertEqual(meta["created_at"], "old")

        self.assertIn("SECOND PROMPT", seen["prompt"])
        self.assertIn("Return ONLY", seen["prompt"])

    def test_custom_prompt_wins_in_run_step(self):
        self.add_district()
        seen = {}

        def fake_single_call(prompt):
            seen["prompt"] = prompt
            return {"content": "Custom prose."}

        with mock.patch.object(dd.SubAgent, "single_call", side_effect=fake_single_call):
            ok, text = dd.run_step("w1", "clayton", preset="first", prompt="MY OWN BRIEF")

        self.assertTrue(ok)
        self.assertEqual(text, "Custom prose.")
        self.assertIn("MY OWN BRIEF", seen["prompt"])
        self.assertNotIn("FIRST PROMPT", seen["prompt"])
        self.assertEqual(_read_json(self.district_json())["description_source"], "custom")

    def test_defaults_to_primary_district(self):
        self.add_district("clayton")
        self.add_district("dockside")
        with mock.patch.object(dd.SubAgent, "single_call", return_value={"content": "Primary prose."}):
            ok, text = dd.run_step("w1", preset="first")
        self.assertTrue(ok)
        self.assertEqual(text, "Primary prose.")
        self.assertTrue(os.path.isfile(self.description_md("clayton")))
        self.assertFalse(os.path.isfile(self.description_md("dockside")))

    def test_llm_error_returns_false_and_writes_nothing(self):
        self.add_district(meta={"name": "clayton", "description": "seed"})
        with mock.patch.object(dd.SubAgent, "single_call", side_effect=LLMCallError("boom")):
            ok, msg = dd.run_step("w1", "clayton", preset="first")

        self.assertFalse(ok)
        self.assertEqual(msg, "boom")
        self.assertFalse(os.path.isfile(self.description_md()))
        self.assertEqual(_read_json(self.district_json()), {"name": "clayton", "description": "seed"})

    def test_no_districts_returns_readable_error(self):
        os.makedirs(os.path.join(self.worlds, "empty"), exist_ok=True)
        _write_json(os.path.join(self.worlds, "empty", "world.json"),
                    {"world_id": "empty", "districts": []})
        with mock.patch.object(dd.SubAgent, "single_call",
                               side_effect=AssertionError("LLM must not be called")):
            ok, msg = dd.run_step("empty")
        self.assertFalse(ok)
        self.assertEqual(msg, "no districts in world empty")


if __name__ == "__main__":
    unittest.main()
