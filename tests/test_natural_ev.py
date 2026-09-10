"""L1 offline tests for the --natural-ev guidance strip (s4_appliance_decision).

Zero API calls.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from steps.simulate import s4_appliance_decision as s4  # noqa: E402


class StripEvGuidanceTests(unittest.TestCase):
    def test_strips_overnight_guidance(self):
        prompt = "Intro. " + s4.EV_OVERNIGHT_GUIDANCE + " Outro."
        out = s4.strip_ev_guidance(prompt)
        self.assertNotIn(s4.EV_OVERNIGHT_GUIDANCE, out)
        self.assertIn("Intro.", out)
        self.assertIn("Outro.", out)

    def test_prompt_without_guidance_unchanged(self):
        self.assertEqual(s4.strip_ev_guidance("hello world"), "hello world")

    def test_removes_all_occurrences(self):
        prompt = s4.EV_OVERNIGHT_GUIDANCE + " mid " + s4.EV_OVERNIGHT_GUIDANCE
        self.assertNotIn(s4.EV_OVERNIGHT_GUIDANCE, s4.strip_ev_guidance(prompt))


if __name__ == "__main__":
    unittest.main()
