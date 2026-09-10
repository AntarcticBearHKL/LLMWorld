from .base import AlwaysOnAppliance

class Router(AlwaysOnAppliance):
    def __init__(self, brand=None, power=None, daily_energy_kwh=None, age=0, location=None, owner=None, location_id=None, owner_id=None, **meta):
        power_watts = power if power is not None else 12
        daily_kwh = daily_energy_kwh if daily_energy_kwh is not None else 0.29
        super().__init__("Router", power_watts=power_watts, daily_energy_kwh=daily_kwh,
                        brand=brand, age=age, location=location, owner=owner,
                        location_id=location_id, owner_id=owner_id, **meta)

    @classmethod
    def get_config_schema(cls):
        return {
            "type": "Router",
            "description": "Internet router / modem (always running)",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "Brand name",
                    "required": False,
                    "example": "TP-Link"
                },
                "power": {
                    "type": "number",
                    "description": "Rated power (watts)",
                    "required": False,
                    "default": 12,
                    "range": [5, 30]
                },
                "daily_energy_kwh": {
                    "type": "number",
                    "description": "Daily energy consumption (kWh)",
                    "required": False,
                    "default": 0.29,
                    "range": [0.1, 0.6]
                },
                "age": {
                    "type": "number",
                    "description": "Age (years)",
                    "required": False,
                    "default": 0,
                    "range": [0, 10]
                }
            }
        }

    @classmethod
    def from_config(cls, config, location=None, owner=None, location_id=None, owner_id=None):
        return cls(
            brand=config.get("brand"),
            power=config.get("power"),
            daily_energy_kwh=config.get("daily_energy_kwh"),
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
