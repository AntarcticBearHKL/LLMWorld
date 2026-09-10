from .base import ChargingAppliance

class Ebike(ChargingAppliance):
    def __init__(self, brand=None, power=None, age=0, location=None, owner=None, location_id=None, owner_id=None, **meta):
        power_watts = power if power is not None else 350
        super().__init__("Ebike", power_watts=power_watts, brand=brand, age=age,
                        location=location, owner=owner, location_id=location_id, owner_id=owner_id, **meta)

    @classmethod
    def get_config_schema(cls):
        return {
            "type": "Ebike",
            "description": "Electric bicycle (can be charged with home or external power)",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "Brand name",
                    "required": False,
                    "example": "Xiaomi"
                },
                "power": {
                    "type": "number",
                    "description": "Charging power (watts)",
                    "required": False,
                    "default": 350,
                    "range": [100, 800]
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
