from .base import ChargingAppliance

class ElectricVehicle(ChargingAppliance):
    def __init__(self, brand=None, power=None, age=0, location=None, owner=None, location_id=None, owner_id=None):
        power_watts = power if power is not None else 7000
        super().__init__("ElectricVehicle", power_watts=power_watts, brand=brand, age=age, is_exclusive=True,
                        location=location, owner=owner, location_id=location_id, owner_id=owner_id)
    
    @classmethod
    def get_config_schema(cls):
        return {
            "type": "ElectricVehicle",
            "description": "Electric vehicle (exclusive resource)",
            "is_exclusive": True,
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "Brand name",
                    "required": False,
                    "example": "Tesla"
                },
                "power": {
                    "type": "number",
                    "description": "Charging power (watts)",
                    "required": False,
                    "default": 7000,
                    "range": [3500, 11000]
                },
                "age": {
                    "type": "number",
                    "description": "Age (years)",
                    "required": False,
                    "default": 0,
                    "range": [0, 10]
                }
            },
            "exclusive_rules": {
                "description": "Exclusive resource usage rules",
                "rules": [
                    "Only one person can use it at a time",
                    "The user is responsible for taking it out and returning it",
                    "Others may choose to ride along",
                    "When returning home, only the person who took it out can drive it back, or pick up others on the way"
                ]
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
            owner_id=owner_id
        )
