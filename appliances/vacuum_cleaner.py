from .base import OnDemandAppliance

class VacuumCleaner(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("吸尘器", power_watts=1200, location=location, owner=owner)
