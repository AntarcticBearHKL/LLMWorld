from .base_appliance import ChargingAppliance

class ElectricVehicle(ChargingAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("电动汽车", power_watts=7000, location=location, owner=owner)
