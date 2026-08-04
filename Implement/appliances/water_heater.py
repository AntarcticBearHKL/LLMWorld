from .base import OnDemandAppliance

class WaterHeater(OnDemandAppliance):
    def __init__(self, brand=None, power=None, age=0, location=None, owner=None, location_id=None, owner_id=None):
        power_watts = power if power is not None else 3000
        super().__init__("热水器", power_watts=power_watts, brand=brand, age=age,
                        location=location, owner=owner, location_id=location_id, owner_id=owner_id)
    
    @classmethod
    def get_config_schema(cls):
        return {
            "type": "热水器",
            "description": "电热水器",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "品牌名称",
                    "required": False,
                    "example": "史密斯"
                },
                "power": {
                    "type": "number",
                    "description": "功率（瓦）",
                    "required": False,
                    "default": 3000,
                    "range": [1500, 5000]
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
            age=config.get("age", 0),
            location=location,
            owner=owner,
            location_id=location_id,
            owner_id=owner_id
        )
