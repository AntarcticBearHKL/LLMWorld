from .base_appliance import AlwaysOnAppliance

class Fridge(AlwaysOnAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("冰箱", power_watts=100, daily_energy_kwh=1.2, 
                        location=location, owner=owner)
