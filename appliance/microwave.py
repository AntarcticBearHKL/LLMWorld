from .base_appliance import OnDemandAppliance

class Microwave(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("微波炉", power_watts=1000, location=location, owner=owner)
