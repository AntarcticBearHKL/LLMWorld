from .base_appliance import OnDemandAppliance

class Light(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        power_map = {
            "客厅": 60,
            "厨房": 40,
            "卫生间": 30
        }
        power = power_map.get(location, 40)
        super().__init__("灯", power_watts=power, location=location, owner=owner)
