"""The district-description step refuses an empty preset/prompt request.

No silent fallback to the first preset in the library (the bundled
``clayton_3168`` census text used to be forced that way): the build-job argv
builder and the step's own prompt resolver both refuse, explicit presets and
custom prompts keep working, and the refusal never reaches the LLM. Temp worlds
only — no user data under ``output/`` is touched.

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

from backend import build as build_module  # noqa: E402
from backend import models, world_admin  # noqa: E402
from steps.world import s1_district_description as dd  # noqa: E402


FIXTURE_PRESETS = [
    {"id": "first", "title": "First", "description": "first preset", "prompt": "FIRST PROMPT"},
    {"id": "second", "title": "Second", "description": "second preset", "prompt": "SECOND PROMPT"},
]
REFUSAL = (
    "no preset or prompt given for district clayton: refusing to fall back to the first preset"
)


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


class DistrictBriefBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.worlds = os.path.join(self._tmp.name, "worlds")
        self.trash = os.path.join(self._tmp.name, "_trash")
        os.makedirs(self.worlds, exist_ok=True)
        self._patches = [
            mock.patch.object(gw, "WORLDS_DIR", self.worlds),
            mock.patch.object(gw, "TRASH_DIR", self.trash),
            mock.patch.object(world_admin, "WORLDS_DIR", self.worlds),
            mock.patch.object(world_admin, "TRASH_DIR", self.trash),
            mock.patch.object(dd, "PRESETS_PATH", os.path.join(self._tmp.name, "presets.json")),
        ]
        for patch in self._patches:
            patch.start()
        _write_json(os.path.join(self._tmp.name, "presets.json"), FIXTURE_PRESETS)

    def tearDown(self):
        for patch in self._patches:
            patch.stop()
        self._tmp.cleanup()

    def add_district(self, name="clayton"):
        gw.add_district("w1", name)

    def district_json(self, name="clayton"):
        return os.path.join(self.worlds, "w1", name, "district.json")

    def description_md(self, name="clayton"):
        return os.path.join(self.worlds, "w1", name, "description.md")


class ResolvePromptRefusalTests(DistrictBriefBase):
    def test_no_brief_is_refused(self):
        with self.assertRaises(ValueError) as ctx:
            dd.resolve_prompt(district="clayton")
        self.assertEqual(str(ctx.exception), REFUSAL)

    def test_unknown_preset_is_refused(self):
        with self.assertRaises(ValueError) as ctx:
            dd.resolve_prompt("ghost", district="clayton")
        self.assertIn("unknown district preset", str(ctx.exception))

    def test_explicit_preset_still_resolves(self):
        self.assertEqual(dd.resolve_prompt("second"), ("SECOND PROMPT", "second"))

    def test_custom_prompt_still_wins(self):
        self.assertEqual(dd.resolve_prompt("second", "MY BRIEF"), ("MY BRIEF", "custom"))


class RunStepRefusalTests(DistrictBriefBase):
    def test_run_step_refuses_without_brief_and_writes_nothing(self):
        self.add_district()
        with mock.patch.object(
            dd.SubAgent, "single_call", side_effect=AssertionError("LLM must not be called")
        ):
            ok, message = dd.run_step("w1", "clayton")
        self.assertFalse(ok)
        self.assertEqual(message, REFUSAL)
        self.assertFalse(os.path.isfile(self.description_md()))

    def test_run_step_still_accepts_an_explicit_preset(self):
        self.add_district()
        with mock.patch.object(dd.SubAgent, "single_call", return_value={"content": "Preset prose."}):
            ok, text = dd.run_step("w1", "clayton", preset="second")
        self.assertTrue(ok)
        self.assertEqual(text, "Preset prose.")
        self.assertEqual(_read_json(self.district_json())["description_source"], "second")

    def test_run_step_still_accepts_a_custom_prompt(self):
        self.add_district()
        with mock.patch.object(dd.SubAgent, "single_call", return_value={"content": "Custom prose."}):
            ok, _text = dd.run_step("w1", "clayton", prompt="MY OWN BRIEF")
        self.assertTrue(ok)
        self.assertEqual(_read_json(self.district_json())["description_source"], "custom")


class BuildArgvRefusalTests(DistrictBriefBase):
    def _request(self, **kwargs):
        return models.JobRequest(
            kind="build", step="district", world="w1", district="clayton", confirm=True, **kwargs
        )

    def test_build_argv_refuses_without_brief(self):
        self.add_district()
        with self.assertRaises(ValueError) as ctx:
            build_module.build_step_argv(self._request())
        self.assertEqual(str(ctx.exception), REFUSAL)

    def test_build_argv_accepts_an_explicit_preset(self):
        self.add_district()
        argv, _warnings = build_module.build_step_argv(self._request(preset="second"))
        self.assertIn("--preset", argv)
        self.assertIn("second", argv)

    def test_build_argv_accepts_a_custom_prompt(self):
        self.add_district()
        argv, _warnings = build_module.build_step_argv(self._request(prompt="MY OWN BRIEF"))
        self.assertIn("--prompt", argv)
        self.assertIn("MY OWN BRIEF", argv)


if __name__ == "__main__":
    unittest.main()
