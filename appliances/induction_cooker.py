from .base import OnDemandAppliance

class InductionCooker(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("电磁炉", power_watts=2000, location=location, owner=owner)
