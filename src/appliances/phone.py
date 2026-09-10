from .base import ChargingAppliance

class Phone(ChargingAppliance):
    def __init__(self, brand=None, power=None, age=0, location=None, owner=None, location_id=None, owner_id=None,
                 battery_kwh=None, soc=None):
        power_watts = power if power is not None else 20
        super().__init__("Phone", power_watts=power_watts, brand=brand, age=age,
                        location=location, owner=owner, location_id=location_id, owner_id=owner_id,
                        battery_kwh=battery_kwh, soc=soc)
    
    @classmethod
    def get_config_schema(cls):
        return {
            "type": "Phone",
            "description": "Smartphone",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "Brand name",
                    "required": False,
                    "example": "Apple"
                },
                "power": {
                    "type": "number",
                    "description": "Charging power (watts)",
                    "required": False,
                    "default": 20,
                    "range": [10, 100]
                },
                "age": {
                    "type": "number",
                    "description": "Age (years)",
                    "required": False,
                    "default": 0,
                    "range": [0, 5]
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
            battery_kwh=config.get("battery_kwh"),
            soc=config.get("soc")
        )
