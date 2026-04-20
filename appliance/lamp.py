from .base_appliance import OnDemandAppliance

class Lamp(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("台灯", power_watts=15, location=location, owner=owner)
