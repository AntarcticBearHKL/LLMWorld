"""L1 offline tests for the charging-battery ceiling and behavior-attributable load.

Zero API calls. Covers Feature B1:
  - appliances.catalog.battery_kwh / default_soc
  - base.ChargingAppliance defaults + charge_deficit_kwh
  - ElectricVehicle / Ebike / Phone from_config plumbing
  - analyze.load_model._accumulate battery ceiling (cap + ceiling interaction)
  - analyze.load_model.build_load_profile exclude_families
  - analyze.analyze_behavior_load.build_report new keys (skipped if deps missing)

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
ANALYZE = os.path.join(SRC, "analyze")
for _p in (SRC, ANALYZE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from appliances.catalog import battery_kwh, default_soc  # noqa: E402
from appliances.base import ChargingAppliance  # noqa: E402
from appliances import create_appliance_from_config  # noqa: E402
from appliances.phone import Phone  # noqa: E402
from appliances.electric_vehicle import ElectricVehicle  # noqa: E402
from appliances.ebike import Ebike  # noqa: E402
from simulate import create_home_from_household  # noqa: E402
import load_model as lm  # noqa: E402


class _Widget(ChargingAppliance):
    """A charging appliance with no catalog battery entry and no daily cap."""

    def __init__(self, power_watts=100, battery_kwh=None, soc=None):
        super().__init__("Widget", power_watts=power_watts, battery_kwh=battery_kwh, soc=soc)

    @classmethod
    def get_config_schema(cls):
        return {"type": "Widget", "config_fields": {}}

    @classmethod
    def from_config(cls, config, location=None, owner=None, location_id=None, owner_id=None):
        return cls()


def _decisions(uid, action="charge_home", time_range="00:00-24:00"):
    return {"M": [{"time": time_range, "operations": [{"unique_id": uid, "action": action}]}]}


def _total_kwh(watts_per_minute):
    return sum(watts_per_minute) / 60.0 / 1000.0


class CatalogBatteryTests(unittest.TestCase):
    def test_known_types(self):
        self.assertEqual(battery_kwh("ElectricVehicle"), 60.0)
        self.assertEqual(battery_kwh("Ebike"), 0.5)
        self.assertEqual(battery_kwh("Phone"), 0.02)
        self.assertEqual(default_soc("ElectricVehicle"), 0.5)
        self.assertEqual(default_soc("Phone"), 0.3)

    def test_unknown_types(self):
        self.assertIsNone(battery_kwh("Nope"))
        self.assertIsNone(default_soc("Nope"))
        self.assertIsNone(battery_kwh(None))


class ChargingApplianceTests(unittest.TestCase):
    def test_catalog_defaults(self):
        self.assertEqual((Phone().battery_kwh, Phone().soc), (0.02, 0.3))
        self.assertEqual((Ebike().battery_kwh, Ebike().soc), (0.5, 0.5))
        self.assertEqual((ElectricVehicle().battery_kwh, ElectricVehicle().soc), (60.0, 0.5))

    def test_deficit_math(self):
        self.assertAlmostEqual(Phone().charge_deficit_kwh(), 0.014, places=9)
        self.assertAlmostEqual(Ebike().charge_deficit_kwh(), 0.25, places=9)
        self.assertAlmostEqual(ElectricVehicle().charge_deficit_kwh(), 30.0, places=9)

    def test_explicit_overrides(self):
        phone = Phone(battery_kwh=1.0, soc=0.25)
        self.assertEqual((phone.battery_kwh, phone.soc), (1.0, 0.25))
        self.assertAlmostEqual(phone.charge_deficit_kwh(), 0.75, places=9)

    def test_full_soc_gives_zero_deficit(self):
        self.assertEqual(Phone(soc=1.0).charge_deficit_kwh(), 0.0)

    def test_unknown_battery_is_none(self):
        widget = _Widget()
        self.assertIsNone(widget.battery_kwh)
        self.assertIsNone(widget.charge_deficit_kwh())

    def test_to_dict_exposes_battery_fields(self):
        payload = Phone().to_dict()
        self.assertEqual(payload["battery_kwh"], 0.02)
        self.assertEqual(payload["soc"], 0.3)


class FromConfigTests(unittest.TestCase):
    def test_phone_threads_battery(self):
        phone = create_appliance_from_config(
            "Phone", {"type": "Phone", "power": 20, "battery_kwh": 1.5, "soc": 0.2})
        self.assertIsInstance(phone, Phone)
        self.assertEqual((phone.battery_kwh, phone.soc), (1.5, 0.2))

    def test_ev_defaults_when_unset(self):
        ev = create_appliance_from_config("ElectricVehicle", {"type": "ElectricVehicle", "power": 7000})
        self.assertEqual((ev.battery_kwh, ev.soc), (60.0, 0.5))

    def test_ebike_threads_battery(self):
        ebike = create_appliance_from_config(
            "Ebike", {"type": "Ebike", "power": 350, "battery_kwh": 0.75, "soc": 0.4})
        self.assertEqual((ebike.battery_kwh, ebike.soc), (0.75, 0.4))


class AccumulateCeilingTests(unittest.TestCase):
    def test_phone_ceiling_binds_after_cap(self):
        phone = Phone()
        contrib, _ref, _best = lm._accumulate({phone.unique_id: phone},
                                              _decisions(phone.unique_id))
        total = _total_kwh(contrib[phone.unique_id])
        # cap=240min (0.08 kWh) > deficit=0.014 kWh -> ceiling is binding
        self.assertAlmostEqual(total, phone.charge_deficit_kwh(), places=9)
        self.assertLessEqual(max(contrib[phone.unique_id]), phone.power_watts + 1e-9)

    def test_cap_binds_when_deficit_larger(self):
        ev = ElectricVehicle()
        contrib, _ref, _best = lm._accumulate({ev.unique_id: ev}, _decisions(ev.unique_id))
        total = _total_kwh(contrib[ev.unique_id])
        # cap=240min * 7000W = 28 kWh < deficit=30 kWh -> cap is binding
        self.assertAlmostEqual(total, 28.0, places=9)

    def test_no_ceiling_when_charge_below_deficit(self):
        phone = Phone()
        contrib, _ref, _best = lm._accumulate(
            {phone.unique_id: phone},
            _decisions(phone.unique_id, time_range="08:00-08:10"))
        expected = 20.0 * 10 / 60.0 / 1000.0
        self.assertAlmostEqual(_total_kwh(contrib[phone.unique_id]), expected, places=9)

    def test_unknown_battery_not_clipped(self):
        widget = _Widget(power_watts=100)
        contrib, _ref, _best = lm._accumulate({widget.unique_id: widget},
                                              _decisions(widget.unique_id))
        self.assertAlmostEqual(_total_kwh(contrib[widget.unique_id]), 2.4, places=9)

    def test_ceiling_lands_exactly_on_deficit(self):
        widget = _Widget(power_watts=100, battery_kwh=1.0, soc=0.0)
        contrib, _ref, _best = lm._accumulate({widget.unique_id: widget},
                                              _decisions(widget.unique_id))
        # 100 W for a full day = 2.4 kWh, ceiling must land exactly on 1.0 kWh
        self.assertAlmostEqual(_total_kwh(contrib[widget.unique_id]), 1.0, places=9)


def _minimal_household():
    return {
        "home": {
            "name": "Test Home",
            "rooms": [
                {"name": "Kitchen", "appliances": [
                    {"type": "Phone", "power": 20},
                    {"type": "Refrigerator", "power": 100},
                ]},
            ],
        },
        "members": [
            {"name": "Alex", "age": 30, "occupation": "engineer",
             "personality": {}, "habits": {}, "personal_appliances": []},
        ],
    }


class BuildLoadProfileExcludeTests(unittest.TestCase):
    def _uids(self):
        home = create_home_from_household(_minimal_household())
        return home.appliance_registry

    def test_phone_battery_floor_on_profile(self):
        registry = self._uids()
        phone_uid = next(u for u, a in registry.items() if isinstance(a, ChargingAppliance))
        decisions = _decisions(phone_uid)
        profile, per_app, total = lm.build_load_profile(_minimal_household(), decisions)
        self.assertAlmostEqual(per_app[phone_uid], Phone().charge_deficit_kwh(), places=9)
        self.assertAlmostEqual(total, per_app[phone_uid] + per_app.get(
            next(u for u, a in registry.items() if u != phone_uid), 0.0), places=6)

    def test_exclude_family_zeroes_and_keeps_keys(self):
        registry = self._uids()
        phone_uid = next(u for u, a in registry.items() if isinstance(a, ChargingAppliance))
        decisions = _decisions(phone_uid)
        profile, per_app, total = lm.build_load_profile(
            _minimal_household(), decisions, exclude_families={"Phone", "Refrigerator"})
        self.assertEqual(total, 0.0)
        self.assertEqual(max(profile), 0.0)
        self.assertIn(phone_uid, per_app)
        self.assertEqual(per_app[phone_uid], 0.0)
        for value in per_app.values():
            self.assertEqual(value, 0.0)

    def test_partial_exclude_only_affects_matching_family(self):
        registry = self._uids()
        phone_uid = next(u for u, a in registry.items() if isinstance(a, ChargingAppliance))
        decisions = _decisions(phone_uid)
        _profile, per_app, total = lm.build_load_profile(
            _minimal_household(), decisions, exclude_families={"Refrigerator"})
        self.assertAlmostEqual(per_app[phone_uid], Phone().charge_deficit_kwh(), places=9)
        self.assertGreater(total, 0.0)


class BehaviorReportTests(unittest.TestCase):
    def test_build_report_reports_raw_and_behavior_totals(self):
        try:
            import analyze_behavior_load as abl
        except Exception as exc:  # pandas/matplotlib/etc. absent in a bare env
            self.skipTest(f"analyze_behavior_load import failed: {exc}")
        profile = [0.0] * 1440
        for minute in range(1080, 1260):
            profile[minute] = 100.0
        activities = [
            {"time": "00:00-08:00", "start": 0, "end": 480, "location": "Bedroom",
             "activity": "Sleeping", "at_home": True},
            {"time": "08:00-18:00", "start": 480, "end": 1080, "location": "Out",
             "activity": "Working", "at_home": False},
            {"time": "18:00-24:00", "start": 1080, "end": 1440, "location": "Living Room",
             "activity": "Relaxing", "at_home": True},
        ]
        report = abl.build_report([{
            "house_id": "house_0001", "member_count": 1, "activities": activities,
            "behavior_profile_watts": profile, "total_kwh": 5.0, "behavior_total_kwh": 4.0,
        }])
        self.assertEqual(report["households"], 1)
        row = report["per_house"][0]
        self.assertEqual(row["total_kwh"], 5.0)
        self.assertEqual(row["behavior_total_kwh"], 4.0)
        self.assertEqual(row["peak_hour"], 18)
        self.assertIn("exclude_families", report)
        self.assertIn("ElectricVehicle", report["exclude_families"])


if __name__ == "__main__":
    unittest.main()
