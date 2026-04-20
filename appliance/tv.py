from .base_appliance import OnDemandAppliance

class TV(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("电视", power_watts=150, location=location, owner=owner)
