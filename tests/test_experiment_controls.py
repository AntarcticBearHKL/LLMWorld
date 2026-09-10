"""L1 offline tests for experiment sampling overrides (run.apply_sampling_overrides).

Zero API calls. These overrides let experiments control run-to-run variance
(temperature / thinking / reasoning effort) without editing config.py.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import importlib
import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
for _p in (PROJECT_ROOT, SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import config  # noqa: E402
import run  # noqa: E402


class SamplingOverrideTests(unittest.TestCase):
    def setUp(self):
        self._saved = (config.TEMPERATURE, config.THINKING, config.REASONING_EFFORT)

    def tearDown(self):
        config.TEMPERATURE, config.THINKING, config.REASONING_EFFORT = self._saved

    def test_applies_all_overrides(self):
        applied = run.apply_sampling_overrides(temperature=0.2, thinking=False,
                                               reasoning_effort="medium")
        self.assertEqual(config.TEMPERATURE, 0.2)
        self.assertFalse(config.THINKING)
        self.assertEqual(config.REASONING_EFFORT, "medium")
        self.assertEqual(applied, {"temperature": 0.2, "thinking": False,
                                   "reasoning_effort": "medium"})

    def test_none_leaves_values_unchanged(self):
        before = (config.TEMPERATURE, config.THINKING, config.REASONING_EFFORT)
        applied = run.apply_sampling_overrides()
        self.assertEqual(applied, {})
        self.assertEqual((config.TEMPERATURE, config.THINKING, config.REASONING_EFFORT), before)

    def test_partial_override(self):
        before_thinking = config.THINKING
        applied = run.apply_sampling_overrides(temperature=0.7)
        self.assertEqual(applied, {"temperature": 0.7})
        self.assertEqual(config.THINKING, before_thinking)


class SubagentDynamicTemperatureTests(unittest.TestCase):
    def test_no_stale_module_constant(self):
        subagent = importlib.import_module("engine.subagent")
        self.assertFalse(hasattr(subagent, "DEFAULT_TEMPERATURE"))


if __name__ == "__main__":
    unittest.main()
