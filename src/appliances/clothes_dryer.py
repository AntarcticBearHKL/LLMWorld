from .base import CycleAppliance

class ClothesDryer(CycleAppliance):
    def __init__(self, brand=None, power=None, energy_per_cycle_kwh=None, cycle_minutes=None, age=0,
                 location=None, owner=None, location_id=None, owner_id=None, **meta):
        power_watts = power if power is not None else 2500
        cycle_kwh = energy_per_cycle_kwh if energy_per_cycle_kwh is not None else 2.5
        minutes = cycle_minutes if cycle_minutes is not None else 120
        super().__init__("ClothesDryer", power_watts, cycle_kwh, minutes, brand=brand, age=age,
                        location=location, owner=owner, location_id=location_id, owner_id=owner_id, **meta)

    @classmethod
    def get_config_schema(cls):
        return {
            "type": "ClothesDryer",
            "description": "Clothes dryer (cycle appliance)",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "Brand name",
                    "required": False,
                    "example": "Bosch"
                },
                "power": {
                    "type": "number",
                    "description": "Power (watts)",
                    "required": False,
                    "default": 2500,
                    "range": [1500, 3500]
                },
                "energy_per_cycle_kwh": {
                    "type": "number",
                    "description": "Energy consumed by one full cycle (kWh)",
                    "required": False,
                    "default": 2.5,
                    "range": [1.0, 4.0]
                },
                "cycle_minutes": {
                    "type": "number",
                    "description": "Duration of one full cycle (minutes)",
                    "required": False,
                    "default": 120,
                    "range": [60, 180]
                },
                "age": {
                    "type": "number",
                    "description": "Age (years)",
                    "required": False,
                    "default": 0,
                    "range": [0, 15]
                }
            }
        }

    @classmethod
    def from_config(cls, config, location=None, owner=None, location_id=None, owner_id=None):
        return cls(
            brand=config.get("brand"),
            power=config.get("power"),
            energy_per_cycle_kwh=config.get("energy_per_cycle_kwh"),
            cycle_minutes=config.get("cycle_minutes"),
            age=config.get("age", 0),
            location=location,
            owner=owner,
            location_id=location_id,
            owner_id=owner_id,
            standby_watts=config.get("standby_watts", 0),
            duty_cycle=config.get("duty_cycle", 1.0),
            flexible=config.get("flexible", False),
            season=config.get("season", "annual"),
            preferred_window=config.get("preferred_window", "")
        )
