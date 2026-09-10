from .room import Room
from .member import Member
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from appliances import create_appliance

class Home:
    def __init__(self, name):
        self.name = name
        self.rooms = {}
        self.members = []
        self.appliance_registry = {}
    
    def add_room(self, room):
        self.rooms[room.name] = room
        for appliance in room.appliances:
            self.appliance_registry[appliance.unique_id] = appliance
        return self
    
    def add_member(self, member):
        self.members.append(member)
        for appliance in member.personal_appliances:
            self.appliance_registry[appliance.unique_id] = appliance
        return self
    
    def get_room(self, room_name):
        return self.rooms.get(room_name)
    
    def get_appliance(self, unique_id):
        return self.appliance_registry.get(unique_id)
    
    def get_appliance_by_room_and_name(self, room_name, appliance_name):
        room = self.get_room(room_name)
        if room:
            for appliance in room.appliances:
                if appliance.name == appliance_name:
                    return appliance
        return None
    
    def to_json(self):
        home_structure = {}
        for room_name, room in self.rooms.items():
            home_structure[room_name] = [appliance.name for appliance in room.appliances]
        return home_structure
    
    def get_home_structure(self):
        structure = {}
        for room_name, room in self.rooms.items():
            structure[room_name] = {
                "appliances": [appliance.name for appliance in room.appliances]
            }
        
        for member in self.members:
            if member.personal_appliances:
                structure[f"{member.name} personal appliances"] = {
                    "appliances": [appliance.name for appliance in member.personal_appliances]
                }
        
        return structure
    
    def _appliance_details(self, appliance):
        details = {
            "unique_id": appliance.unique_id,
            "name": appliance.name,
            "type": appliance.appliance_type,
            "power_watts": appliance.power_watts,
            "standby_watts": appliance.standby_watts,
            "duty_cycle": appliance.duty_cycle,
            "flexible": appliance.flexible,
            "season": appliance.season
        }
        if hasattr(appliance, "energy_per_cycle_kwh"):
            details["energy_per_cycle_kwh"] = appliance.energy_per_cycle_kwh
        if hasattr(appliance, "cycle_minutes"):
            details["cycle_minutes"] = appliance.cycle_minutes
        return details

    def get_home_structure_with_details(self):
        structure = {}
        for room_name, room in self.rooms.items():
            structure[room_name] = {
                "appliances": [self._appliance_details(a) for a in room.appliances]
            }
        
        for member in self.members:
            if member.personal_appliances:
                structure[f"{member.name} personal appliances"] = {
                    "appliances": [self._appliance_details(a) for a in member.personal_appliances]
                }
        
        return structure
    
    def get_members_info(self):
        return [member.to_dict() for member in self.members]
    
    def get_exclusive_resources(self):
        exclusive_resources = []
        for appliance in self.appliance_registry.values():
            if hasattr(appliance, 'is_exclusive') and appliance.is_exclusive:
                exclusive_resources.append({
                    "unique_id": appliance.unique_id,
                    "name": appliance.name,
                    "type": appliance.appliance_type,
                    "owner": appliance.owner,
                    "location": appliance.location,
                    "rules": self._get_exclusive_rules(appliance)
                })
        return exclusive_resources
    
    def _get_exclusive_rules(self, appliance):
        if appliance.name == "ElectricVehicle":
            return [
                "Only one person can use it at a time",
                "The user is responsible for taking it out and returning it",
                "Others may choose to ride along",
                "When returning home, only the person who took it out can drive it back, or pick up others on the way"
            ]
        return ["Only one person can use it at a time"]
    
    def get_total_energy_consumption(self):
        total = 0
        for appliance in self.appliance_registry.values():
            total += appliance.get_total_energy()
        return total


