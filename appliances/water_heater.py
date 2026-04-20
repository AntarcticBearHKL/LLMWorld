from .base import OnDemandAppliance

class WaterHeater(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("热水器", power_watts=3000, location=location, owner=owner)
