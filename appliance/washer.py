from .base_appliance import OnDemandAppliance

class WashingMachine(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("洗衣机", power_watts=500, location=location, owner=owner)
