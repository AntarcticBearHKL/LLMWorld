from .base import OnDemandAppliance

class Light(OnDemandAppliance):
    def __init__(self, brand=None, power=None, age=0, location=None, owner=None, location_id=None, owner_id=None):
        if power is None:
            power_map = {"客厅": 60, "厨房": 40, "卫生间": 30}
            power = power_map.get(location, 40)
        super().__init__("灯", power_watts=power, brand=brand, age=age,
                        location=location, owner=owner, location_id=location_id, owner_id=owner_id)
    
    @classmethod
    def get_config_schema(cls):
        return {
            "type": "灯",
            "description": "房间主灯",
            "config_fields": {
                "brand": {
                    "type": "string",
                    "description": "品牌名称",
                    "required": False,
                    "example": "飞利浦"
                },
                "power": {
                    "type": "number",
                    "description": "功率（瓦）",
                    "required": False,
                    "default": 40,
                    "range": [10, 100]
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
