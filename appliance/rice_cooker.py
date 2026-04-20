from .base_appliance import OnDemandAppliance

class RiceCooker(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("电饭煲", power_watts=800, location=location, owner=owner)
