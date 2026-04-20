from .base_appliance import OnDemandAppliance

class Computer(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("电脑", power_watts=200, location=location, owner=owner)
