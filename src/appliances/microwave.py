from .base import OnDemandAppliance

class Microwave(OnDemandAppliance):
    def __init__(self, brand=None, power=None, age=0, location=None, owner=None, location_id=None, owner_id=None):
        power_watts = power if power is not None else 1000
        super().__init__("微波炉", power_watts=power_watts, brand=brand, age=age,
                        location=location, owner=owner, location_id=location_id, owner_id=owner_id)
    
    @classmethod
    def get_config_schema(cls):
        return {
            "type": "微波炉",
            "description": "微波炉",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "品牌名称",
                    "required": False,
                    "example": "格兰仕"
                },
                "power": {
                    "type": "number",
                    "description": "功率（瓦）",
                    "required": False,
                    "default": 1000,
                    "range": [700, 1500]
                },
                "age": {
                    "type": "number",
                    "description": "使用年限",
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
            owner_id=owner_id
        )
