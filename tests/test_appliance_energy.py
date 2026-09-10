"""L1 offline tests for appliance energy math and catalog metadata.

Zero API calls. Locks the per-appliance energy formulas used by the load model:
on-demand (power x hours), always-on (daily energy / 24), cycle (per-cycle energy
capped at one cycle), external power = 0, plus apply_appliance_meta.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from appliances.base import OnDemandAppliance, AlwaysOnAppliance, CycleAppliance  # noqa: E402
from appliances.catalog import apply_appliance_meta  # noqa: E402


class _OnDemand(OnDemandAppliance):
    @classmethod
    def get_config_schema(cls):
        return {"type": "X", "config_fields": {}}

    @classmethod
    def from_config(cls, config, location=None, owner=None, location_id=None, owner_id=None):
        return cls("X", 100)


class _AlwaysOn(AlwaysOnAppliance):
    @classmethod
    def get_config_schema(cls):
        return {"type": "Y", "config_fields": {}}

    @classmethod
    def from_config(cls, config, location=None, owner=None, location_id=None, owner_id=None):
        return cls("Y", 100, daily_energy_kwh=2.4)


class _Cycle(CycleAppliance):
    @classmethod
    def get_config_schema(cls):
        return {"type": "Z", "config_fields": {}}

    @classmethod
    def from_config(cls, config, location=None, owner=None, location_id=None, owner_id=None):
        return cls("Z", 500, energy_per_cycle_kwh=0.6, cycle_minutes=90)


class OnDemandEnergyTests(unittest.TestCase):
    def test_power_times_hours(self):
        tv = _OnDemand("TV", 1000)
        self.assertAlmostEqual(tv.calculate_energy(0, 60), 1.0, places=9)
        self.assertAlmostEqual(tv.calculate_energy(0, 30), 0.5, places=9)

    def test_external_power_is_zero(self):
        tv = _OnDemand("TV", 1000)
        self.assertEqual(tv.calculate_energy(0, 60, power_source="external"), 0)


class AlwaysOnEnergyTests(unittest.TestCase):
    def test_daily_energy_scaled_by_hours(self):
        fridge = _AlwaysOn("F", 100, daily_energy_kwh=2.4)
        self.assertAlmostEqual(fridge.calculate_energy(0, 60), 0.1, places=9)
        self.assertAlmostEqual(fridge.calculate_energy(0, 1440), 2.4, places=9)

    def test_default_daily_energy_from_power(self):
        router = _AlwaysOn("R", 240, daily_energy_kwh=None)
        self.assertAlmostEqual(router.daily_energy_kwh, 5.76, places=9)
        self.assertAlmostEqual(router.calculate_energy(0, 1440), 5.76, places=9)


class CycleEnergyTests(unittest.TestCase):
    def test_full_cycle(self):
        wm = _Cycle("W", 500, energy_per_cycle_kwh=0.6, cycle_minutes=90)
        self.assertAlmostEqual(wm.calculate_energy(0, 90), 0.6, places=9)

    def test_partial_cycle_scaled(self):
        wm = _Cycle("W", 500, energy_per_cycle_kwh=0.6, cycle_minutes=90)
        self.assertAlmostEqual(wm.calculate_energy(0, 45), 0.3, places=9)

    def test_over_cycle_is_capped(self):
        wm = _Cycle("W", 500, energy_per_cycle_kwh=0.6, cycle_minutes=90)
        self.assertAlmostEqual(wm.calculate_energy(0, 180), 0.6, places=9)


class ApplyMetaTests(unittest.TestCase):
    def test_on_demand_metadata(self):
        obj = _OnDemand("TV", 150)
        apply_appliance_meta(obj, "TV")
        self.assertEqual(obj.standby_watts, 3)
        self.assertEqual(obj.duty_cycle, 1.0)
        self.assertFalse(obj.flexible)
        self.assertEqual(obj.season, "annual")

    def test_cycle_metadata_sets_cycle_fields(self):
        obj = _Cycle("WashingMachine", 500, energy_per_cycle_kwh=None, cycle_minutes=None)
        apply_appliance_meta(obj, "WashingMachine")
        self.assertEqual(obj.energy_per_cycle_kwh, 0.6)
        self.assertEqual(obj.cycle_minutes, 90)
        self.assertTrue(obj.flexible)

    def test_unknown_type_is_noop(self):
        obj = _OnDemand("Mystery", 100)
        apply_appliance_meta(obj, "Mystery")
        self.assertEqual(obj.standby_watts, 0)


if __name__ == "__main__":
    unittest.main()
