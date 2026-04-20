from .base_appliance import OnDemandAppliance

class AirConditioner(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        power = 1800 if location and "卧室" in location else 2000
        super().__init__("空调", power_watts=power, location=location, owner=owner)
