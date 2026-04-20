from .base_appliance import OnDemandAppliance

class Hood(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("油烟机", power_watts=200, location=location, owner=owner)
