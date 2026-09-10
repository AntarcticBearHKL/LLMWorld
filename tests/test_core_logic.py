"""L1 offline tests for core intervention / parsing / validation logic.

Zero API calls. Covers goal.md §4 L1 priority targets that are independent of
work in progress elsewhere:
  - engine.json_parse.parse   (tolerant LLM JSON)
  - engine.policy.parse_policy_arg (TOU intervention entry point, RQ2)
  - engine.utils.normalize_time_range / normalize_activity_times
  - engine.utils.repair_appliance_operations / validate_and_clean_decisions
  - appliances.catalog.backfill_power

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from engine import json_parse  # noqa: E402
from engine import policy  # noqa: E402
from engine import utils  # noqa: E402
from appliances.catalog import backfill_power  # noqa: E402
from simulate import create_home_from_household  # noqa: E402


class JsonParseTests(unittest.TestCase):
    def test_plain_object(self):
        self.assertEqual(json_parse.parse('{"a": 1}'), {"a": 1})

    def test_strips_markdown_fence(self):
        self.assertEqual(json_parse.parse('```json\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(json_parse.parse('```\n{"a": 2}\n```'), {"a": 2})

    def test_prose_around_json(self):
        self.assertEqual(json_parse.parse('Here: {"a": 1} done'), {"a": 1})

    def test_single_quotes(self):
        self.assertEqual(json_parse.parse("{'a': 'x', 'b': 2}"), {"a": "x", "b": 2})

    def test_trailing_comma(self):
        self.assertEqual(json_parse.parse('{"a": [1, 2,],}'), {"a": [1, 2]})

    def test_unquoted_keys_and_bare_literals(self):
        self.assertEqual(json_parse.parse("{a: 1, b: true, c: null}"),
                         {"a": 1, "b": True, "c": None})
        self.assertEqual(json_parse.parse('{"a": True, "b": False, "c": None}'),
                         {"a": True, "b": False, "c": None})

    def test_brace_inside_string_is_not_a_boundary(self):
        self.assertEqual(json_parse.parse('{"s": "a } b"}'), {"s": "a } b"})

    def test_raw_newline_in_string_is_escaped(self):
        self.assertEqual(json_parse.parse('{"s": "x\ny"}'), {"s": "x\ny"})

    def test_nested_object(self):
        payload = '{"m": {"n": [1, {"k": "v"}]}}'
        self.assertEqual(json_parse.parse(payload), {"m": {"n": [1, {"k": "v"}]}})


class PolicyTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(policy.parse_policy_arg(None), ("", None))
        self.assertEqual(policy.parse_policy_arg(""), ("", None))

    def test_default_tou(self):
        text, tag = policy.parse_policy_arg("tou")
        self.assertEqual(tag, "tou")
        self.assertIn("time-of-use", text)
        self.assertIn("16:00-21:00", text)
        self.assertIn("0.60 AUD/kWh", text)
        self.assertIn("0.18 AUD/kWh", text)

    def test_tou_custom_rates(self):
        text, tag = policy.parse_policy_arg("TOU:0.5,0.2")
        self.assertEqual(tag, "tou")
        self.assertIn("0.50 AUD/kWh", text)
        self.assertIn("0.20 AUD/kWh", text)

    def test_tou_with_shoulder(self):
        text, _tag = policy.parse_policy_arg("tou:0.6,0.18,0.35")
        self.assertIn("0.35 AUD/kWh", text)

    def test_single_rate_falls_back_to_defaults(self):
        text, _tag = policy.parse_policy_arg("tou:0.9")
        self.assertIn("0.60 AUD/kWh", text)
        self.assertIn("0.18 AUD/kWh", text)

    def test_unknown_policy_raises(self):
        with self.assertRaises(ValueError):
            policy.parse_policy_arg("nudge")

    def test_tou_soft_has_no_directive(self):
        text, tag = policy.parse_policy_arg("tou_soft")
        self.assertEqual(tag, "tou_soft")
        self.assertIn("0.60 AUD/kWh", text)
        self.assertIn("16:00-21:00", text)
        self.assertNotIn("shift", text.lower())
        self.assertNotIn("avoid", text.lower())

    def test_tou_soft_custom_rates(self):
        text, tag = policy.parse_policy_arg("tou_soft:0.5,0.2,0.3")
        self.assertEqual(tag, "tou_soft")
        self.assertIn("0.50 AUD/kWh", text)
        self.assertIn("0.30 AUD/kWh", text)


class PolicyScheduleTests(unittest.TestCase):
    def test_parse_entries(self):
        schedule = policy.parse_policy_schedule(["2026-04-25,2026-04-28,tou"])
        self.assertEqual(schedule, [{"start": "2026-04-25", "end": "2026-04-28", "policy": "tou"}])

    def test_open_ended_entry(self):
        schedule = policy.parse_policy_schedule(["2026-04-25,,tou"])
        self.assertIsNone(schedule[0]["end"])

    def test_empty_input(self):
        self.assertEqual(policy.parse_policy_schedule([]), [])
        self.assertEqual(policy.parse_policy_schedule(None), [])
        self.assertEqual(policy.parse_policy_schedule([""]), [])

    def test_malformed_raises(self):
        with self.assertRaises(ValueError):
            policy.parse_policy_schedule(["2026-04-25,tou"])
        with self.assertRaises(ValueError):
            policy.parse_policy_schedule([",,tou"])

    def test_active_policy_within_windows(self):
        schedule = policy.parse_policy_schedule(
            ["2026-04-25,2026-04-28,tou", "2026-04-29,,tou_soft"])
        self.assertEqual(policy.active_policy_spec(schedule, "2026-04-25"), "tou")
        self.assertEqual(policy.active_policy_spec(schedule, "2026-04-28"), "tou")
        self.assertEqual(policy.active_policy_spec(schedule, "2026-04-29"), "tou_soft")
        self.assertEqual(policy.active_policy_spec(schedule, "2027-01-01"), "tou_soft")

    def test_active_policy_gap_is_none(self):
        schedule = policy.parse_policy_schedule(["2026-04-25,2026-04-28,tou"])
        self.assertIsNone(policy.active_policy_spec(schedule, "2026-04-24"))
        self.assertIsNone(policy.active_policy_spec(schedule, "2026-04-29"))


class NormalizeTimeRangeTests(unittest.TestCase):
    def test_pads_hours(self):
        self.assertEqual(utils.normalize_time_range("8:00-8:30"), "08:00-08:30")

    def test_fullwidth_colon_and_dash(self):
        self.assertEqual(utils.normalize_time_range("8：00–9：30"), "08:00-09:30")

    def test_removes_spaces(self):
        self.assertEqual(utils.normalize_time_range(" 08:00 - 09:00 "), "08:00-09:00")

    def test_single_time_uses_next_start(self):
        self.assertEqual(utils.normalize_time_range("08:00", next_start="09:30"),
                         "08:00-09:30")

    def test_single_time_without_next_defaults_to_one_hour(self):
        self.assertEqual(utils.normalize_time_range("08:00"), "08:00-09:00")

    def test_single_late_time_caps_at_24(self):
        self.assertEqual(utils.normalize_time_range("23:30"), "23:30-24:00")

    def test_none_passthrough(self):
        self.assertIsNone(utils.normalize_time_range(None))

    def test_invalid_returns_original(self):
        self.assertEqual(utils.normalize_time_range("not a time"), "not a time")
        self.assertEqual(utils.normalize_time_range("24:30-25:00"), "24:30-25:00")

    def test_reversed_range_left_untouched(self):
        self.assertEqual(utils.normalize_time_range("09:00-08:00"), "09:00-08:00")


class NormalizeActivityTimesTests(unittest.TestCase):
    def test_uses_next_segment_and_logs(self):
        items = [{"time": "08:00", "activity": "a"},
                 {"time": "09:00-10:00", "activity": "b"}]
        log = []
        out = utils.normalize_activity_times(items, repair_log=log)
        self.assertEqual(out[0]["time"], "08:00-09:00")
        self.assertEqual(out[1]["time"], "09:00-10:00")
        self.assertEqual(len(log), 1)

    def test_non_dict_passthrough(self):
        out = utils.normalize_activity_times(["raw", {"time": "07:00-08:00"}])
        self.assertEqual(out[0], "raw")

    def test_empty(self):
        self.assertEqual(utils.normalize_activity_times([]), [])


class BackfillPowerTests(unittest.TestCase):
    def test_missing_power_filled_from_estimate(self):
        self.assertEqual(backfill_power({"type": "TV"})["power"], 150)

    def test_out_of_bounds_clamped_to_estimate(self):
        self.assertEqual(backfill_power({"type": "TV", "power": 99999})["power"], 150)

    def test_valid_power_preserved(self):
        self.assertEqual(backfill_power({"type": "TV", "power": 120})["power"], 120)

    def test_bool_power_replaced(self):
        self.assertEqual(backfill_power({"type": "TV", "power": True})["power"], 150)

    def test_location_aware_air_conditioner(self):
        self.assertEqual(backfill_power({"type": "AirConditioner"}, location="Bedroom 1")["power"], 1800)
        self.assertEqual(backfill_power({"type": "AirConditioner"}, location="Kitchen")["power"], 2000)

    def test_location_aware_light(self):
        self.assertEqual(backfill_power({"type": "Light"}, location="Living Room")["power"], 60)
        self.assertEqual(backfill_power({"type": "Light"}, location="Kitchen")["power"], 40)
        self.assertEqual(backfill_power({"type": "Light"}, location="Bathroom")["power"], 30)

    def test_refrigerator_daily_energy_filled(self):
        self.assertEqual(backfill_power({"type": "Refrigerator"})["daily_energy_kwh"], 1.2)

    def test_does_not_mutate_input(self):
        cfg = {"type": "TV"}
        backfill_power(cfg)
        self.assertNotIn("power", cfg)


def _household():
    return {
        "home": {
            "name": "T",
            "rooms": [
                {"name": "Kitchen", "appliances": [
                    {"type": "TV", "power": 150},
                    {"type": "Refrigerator", "power": 100},
                ]},
                {"name": "Bedroom 1", "appliances": [{"type": "AirConditioner", "power": 2000}]},
            ],
        },
        "members": [
            {"name": "Alex", "age": 30, "occupation": "engineer",
             "personality": {}, "habits": {}, "personal_appliances": []},
        ],
    }


class RepairOperationsTests(unittest.TestCase):
    def setUp(self):
        self.home = create_home_from_household(_household())
        self.registry = self.home.appliance_registry

    def test_uids_present(self):
        self.assertIn("kitchen_tv", self.registry)

    def test_valid_operation_kept(self):
        clean, repairs, unknowns = utils.repair_appliance_operations(
            [{"unique_id": "kitchen_tv", "action": "use"}], self.home)
        self.assertEqual(clean, [{"unique_id": "kitchen_tv", "action": "use"}])
        self.assertEqual(repairs, [])
        self.assertEqual(unknowns, [])

    def test_hallucinated_type_repaired_by_family(self):
        clean, repairs, unknown = utils.repair_appliance_operations(
            [{"unique_id": "kitchen_television", "action": "use"}], self.home)
        self.assertEqual(clean, [{"unique_id": "kitchen_tv", "action": "use"}])
        self.assertEqual(repairs, [{"from": "kitchen_television", "to": "kitchen_tv"}])
        self.assertEqual(unknown, [])

    def test_invalid_action_is_unknown(self):
        clean, repairs, unknown = utils.repair_appliance_operations(
            [{"unique_id": "kitchen_tv", "action": "fly"}], self.home)
        self.assertEqual(clean, [])
        self.assertEqual(len(unknown), 1)

    def test_unknown_id_is_unknown(self):
        clean, _repairs, unknown = utils.repair_appliance_operations(
            [{"unique_id": "garage_microwave", "action": "use"}], self.home)
        self.assertEqual(clean, [])
        self.assertEqual(len(unknown), 1)

    def test_non_dict_skipped(self):
        clean, repairs, unknown = utils.repair_appliance_operations(["nope"], self.home)
        self.assertEqual((clean, repairs, unknown), ([], [], []))


class ValidateDecisionsTests(unittest.TestCase):
    def setUp(self):
        self.home = create_home_from_household(_household())

    def test_in_home_operation_kept_valid(self):
        data = {"appliance_decisions": [
            {"time": "08:00-09:00", "location": "Kitchen", "activity": "cook",
             "operations": [{"unique_id": "kitchen_tv", "action": "use"}]}]}
        cleaned, report = utils.validate_and_clean_decisions(data, self.home, member_name="Alex")
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["start_minutes"], 480)
        self.assertEqual(cleaned[0]["end_minutes"], 540)
        self.assertEqual(len(cleaned[0]["operations"]), 1)
        self.assertTrue(report["valid"])

    def test_out_of_home_room_appliance_dropped(self):
        data = {"appliance_decisions": [
            {"time": "08:00-09:00", "location": "Out", "activity": "work",
             "operations": [{"unique_id": "kitchen_tv", "action": "use"}]}]}
        cleaned, report = utils.validate_and_clean_decisions(data, self.home, member_name="Alex")
        self.assertEqual(cleaned[0]["operations"], [])
        self.assertFalse(report["valid"])
        self.assertIn("out of home", report["dropped"][0]["reason"])

    def test_unknown_operation_dropped(self):
        data = {"appliance_decisions": [
            {"time": "08:00-09:00", "location": "Kitchen", "activity": "x",
             "operations": [{"unique_id": "kitchen_oven", "action": "use"}]}]}
        _cleaned, report = utils.validate_and_clean_decisions(data, self.home, member_name="Alex")
        self.assertFalse(report["valid"])
        self.assertEqual(report["operations_kept"], 0)


if __name__ == "__main__":
    unittest.main()
