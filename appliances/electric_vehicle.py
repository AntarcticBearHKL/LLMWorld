from .base import ChargingAppliance

class ElectricVehicle(ChargingAppliance):
    def __init__(self, brand=None, power=None, age=0, location=None, owner=None, location_id=None, owner_id=None):
        power_watts = power if power is not None else 7000
        super().__init__("电动汽车", power_watts=power_watts, brand=brand, age=age, is_exclusive=True,
                        location=location, owner=owner, location_id=location_id, owner_id=owner_id)
    
    @classmethod
    def get_config_schema(cls):
        return {
            "type": "电动汽车",
            "description": "电动汽车（独占资源）",
            "is_exclusive": True,
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "品牌名称",
                    "required": False,
                    "example": "特斯拉"
                },
                "power": {
                    "type": "number",
                    "description": "充电功率（瓦）",
                    "required": False,
                    "default": 7000,
                    "range": [3500, 11000]
                },
                "age": {
                    "type": "number",
                    "description": "使用年限",
                    "required": False,
                    "default": 0,
                    "range": [0, 10]
                }
            },
            "exclusive_rules": {
                "description": "独占资源使用规则",
                "rules": [
                    "同一时间只能一人使用",
                    "使用者负责开出和归还",
                    "其他人可以选择同乘",
                    "回家时只能由开出去的人开回来，或顺路接回其他人"
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
