"""L1 offline tests for engine.tariff + policy.parse_tariff (cost-context pipeline).

Zero API calls. Covers the price-response capability: turning a price policy into
concrete per-appliance peak/off-peak cost figures injected into s4.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from engine import policy, tariff  # noqa: E402


class ParseTariffTests(unittest.TestCase):
    def test_none_and_non_price(self):
        self.assertIsNone(policy.parse_tariff(None))
        self.assertIsNone(policy.parse_tariff(""))
        self.assertIsNone(policy.parse_tariff("nudge"))

    def test_tou_default_and_custom(self):
        cfg = policy.parse_tariff("tou")
        self.assertEqual(cfg["peak_rate"], 0.60)
        self.assertEqual(cfg["valley_rate"], 0.18)
        self.assertEqual(cfg["peak_window"], ("16:00", "21:00"))
        self.assertEqual(policy.parse_tariff("tou:0.9,0.20")["peak_rate"], 0.9)

    def test_cpp_rate(self):
        cfg = policy.parse_tariff("cpp:1.20")
        self.assertEqual(cfg["peak_rate"], 1.20)
        self.assertEqual(cfg["peak_window"], ("17:00", "20:00"))


class RenderCostContextTests(unittest.TestCase):
    DETAILS = {"kitchen": {"appliances": [
        {"unique_id": "kitchen_washingmachine", "type": "WashingMachine",
         "flexible": True, "energy_per_cycle_kwh": 0.6},
        {"unique_id": "kitchen_kettle", "type": "Kettle", "flexible": False, "power_watts": 2000},
        {"unique_id": "living_room_airconditioner", "type": "AirConditioner",
         "flexible": True, "power_watts": 2000},
        {"unique_id": "kitchen_refrigerator", "type": "always_on", "flexible": False},
    ]}}
    TARIFF = {"peak_window": ("16:00", "21:00"), "valley_window": ("22:00", "07:00"),
              "peak_rate": 0.60, "valley_rate": 0.18, "shoulder_rate": 0.35}

    def test_empty_when_no_tariff(self):
        self.assertEqual(tariff.render_cost_context(self.DETAILS, None), "")
        self.assertEqual(tariff.render_cost_context(None, self.TARIFF), "")
        self.assertEqual(tariff.render_cost_context(self.DETAILS, {}), "")

    def test_renders_flexible_only(self):
        text = tariff.render_cost_context(self.DETAILS, self.TARIFF)
        self.assertIn("kitchen_washingmachine", text)
        self.assertIn("living_room_airconditioner", text)
        self.assertNotIn("kitchen_kettle", text)
        self.assertNotIn("kitchen_refrigerator", text)

    def test_sensitivity_note(self):
        self.assertEqual(tariff.sensitivity_note(None), "")
        self.assertEqual(tariff.sensitivity_note("other"), "")
        self.assertIn("cost-conscious", tariff.sensitivity_note("high"))
        self.assertIn("not very price-sensitive", tariff.sensitivity_note("low"))

    def test_cost_numbers(self):
        text = tariff.render_cost_context(self.DETAILS, self.TARIFF)
        self.assertIn("0.36 AUD", text)   # 0.6 kWh x 0.60
        self.assertIn("0.11 AUD", text)   # 0.6 kWh x 0.18
        self.assertIn("1.20 AUD", text)   # 2.0 kW x 1h x 0.60
        self.assertIn("move it to an off-peak segment", text)


if __name__ == "__main__":
    unittest.main()
