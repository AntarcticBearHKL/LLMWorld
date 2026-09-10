from .base import OnDemandAppliance

class SpaceHeater(OnDemandAppliance):
    def __init__(self, brand=None, power=None, age=0, location=None, owner=None, location_id=None, owner_id=None, **meta):
        power_watts = power if power is not None else 2000
        super().__init__("SpaceHeater", power_watts=power_watts, brand=brand, age=age,
                        location=location, owner=owner, location_id=location_id, owner_id=owner_id, **meta)

    @classmethod
    def get_config_schema(cls):
        return {
            "type": "SpaceHeater",
            "description": "Portable electric space heater",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "Brand name",
                    "required": False,
                    "example": "Dyson"
                },
                "power": {
                    "type": "number",
                    "description": "Power (watts)",
                    "required": False,
                    "default": 2000,
                    "range": [800, 3000]
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
