from .base import AlwaysOnAppliance

class Refrigerator(AlwaysOnAppliance):
    def __init__(self, brand=None, power=None, daily_energy_kwh=None, age=0, location=None, owner=None, location_id=None, owner_id=None):
        power_watts = power if power is not None else 100
        daily_kwh = daily_energy_kwh if daily_energy_kwh is not None else 1.2
        super().__init__("Refrigerator", power_watts=power_watts, daily_energy_kwh=daily_kwh, 
                        brand=brand, age=age, location=location, owner=owner, 
                        location_id=location_id, owner_id=owner_id)
    
    @classmethod
    def get_config_schema(cls):
        return {
            "type": "Refrigerator",
            "description": "Household refrigerator (always running)",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "Brand name",
                    "required": False,
                    "example": "Haier"
                },
                "power": {
                    "type": "number",
                    "description": "Rated power (watts)",
                    "required": False,
                    "default": 100,
                    "range": [80, 200]
                },
                "daily_energy_kwh": {
                    "type": "number",
                    "description": "Daily energy consumption (kWh)",
                    "required": False,
                    "default": 1.2,
                    "range": [0.5, 3.0]
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
            daily_energy_kwh=config.get("daily_energy_kwh"),
            age=config.get("age", 0),
            location=location,
            owner=owner,
            location_id=location_id,
            owner_id=owner_id
        )
