"""L1 integration test for run_simulate's per-day policy-schedule wiring.

Zero API calls: the four simulate steps are mocked. Verifies that a schedule
activates the policy only inside its date window (R027), while a global --policy
applies every day.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest
from unittest import mock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
for _p in (PROJECT_ROOT, SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import run  # noqa: E402
from engine import policy as engine_policy  # noqa: E402


class PolicyScheduleIntegrationTests(unittest.TestCase):
    def _run(self, **kwargs):
        with mock.patch.object(run, "get_member_names", return_value=["Alex"]), \
             mock.patch.object(run.s1_macro_plan, "run_step", return_value=(True, {})), \
             mock.patch.object(run.s2_coordinate, "run_step", return_value=(True, {})), \
             mock.patch.object(run.s3_enrich, "run_step", return_value=(True, {})), \
             mock.patch.object(run.s4_appliance_decision, "run_step",
                                return_value=(True, {})) as s4:
            rc = run.run_simulate("world_test", "2026-09-11", "env_test", 1,
                                  houses="house_0001", days=2, **kwargs)
        return rc, s4.call_args_list

    def test_schedule_activates_only_inside_window(self):
        schedule = engine_policy.parse_policy_schedule(["2026-09-11,2026-09-11,tou"])
        rc, calls = self._run(policy_schedule=schedule)
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].kwargs["policy_tag"], "tou")
        self.assertIn("time-of-use", calls[0].kwargs["policy_text"])
        self.assertIsNone(calls[1].kwargs["policy_tag"])
        self.assertEqual(calls[1].kwargs["policy_text"], "")

    def test_open_ended_schedule_covers_later_days(self):
        schedule = engine_policy.parse_policy_schedule(["2026-09-11,,tou_soft"])
        _rc, calls = self._run(policy_schedule=schedule)
        self.assertEqual(calls[0].kwargs["policy_tag"], "tou_soft")
        self.assertEqual(calls[1].kwargs["policy_tag"], "tou_soft")

    def test_global_policy_applies_every_day(self):
        _rc, calls = self._run(policy_spec="tou")
        self.assertEqual(calls[0].kwargs["policy_tag"], "tou")
        self.assertEqual(calls[1].kwargs["policy_tag"], "tou")


if __name__ == "__main__":
    unittest.main()
