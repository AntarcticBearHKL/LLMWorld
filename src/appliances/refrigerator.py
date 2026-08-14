from .base import AlwaysOnAppliance

class Refrigerator(AlwaysOnAppliance):
    def __init__(self, brand=None, power=None, daily_energy_kwh=None, age=0, location=None, owner=None, location_id=None, owner_id=None):
        power_watts = power if power is not None else 100
        daily_kwh = daily_energy_kwh if daily_energy_kwh is not None else 1.2
        super().__init__("冰箱", power_watts=power_watts, daily_energy_kwh=daily_kwh, 
                        brand=brand, age=age, location=location, owner=owner, 
                        location_id=location_id, owner_id=owner_id)
    
    @classmethod
    def get_config_schema(cls):
        return {
            "type": "冰箱",
            "description": "家用冰箱（持续运行）",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "品牌名称",
                    "required": False,
                    "example": "海尔"
                },
                "power": {
                    "type": "number",
                    "description": "额定功率（瓦）",
                    "required": False,
                    "default": 100,
                    "range": [80, 200]
                },
                "daily_energy_kwh": {
                    "type": "number",
                    "description": "日耗电量（千瓦时）",
                    "required": False,
                    "default": 1.2,
                    "range": [0.5, 3.0]
                },
                "age": {
                    "type": "number",
                    "description": "使用年限",
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
