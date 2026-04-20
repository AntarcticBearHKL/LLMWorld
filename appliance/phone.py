from .base_appliance import ChargingAppliance

class Phone(ChargingAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("手机", power_watts=20, location=location, owner=owner)
