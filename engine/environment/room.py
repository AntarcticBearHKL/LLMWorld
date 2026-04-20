import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from appliance import create_appliance

class Room:
    def __init__(self, name):
        self.name = name
        self.appliances = []
    
    def add_appliance(self, appliance):
        self.appliances.append(appliance)
        return self
    
    def add_appliance_by_name(self, appliance_name):
        appliance = create_appliance(appliance_name, location=self.name)
        self.appliances.append(appliance)
        return self
    
    def get_appliance(self, unique_id):
        for appliance in self.appliances:
            if appliance.unique_id == unique_id:
                return appliance
        return None
    
    def get_appliances_info(self):
        return [f"{a.name} ({a.appliance_type})" for a in self.appliances]
    
    def to_dict(self):
        return {
            "name": self.name,
            "appliances": [a.to_dict() for a in self.appliances]
        }
