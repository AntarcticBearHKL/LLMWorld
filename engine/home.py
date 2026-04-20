from .room import Room
from .member import Member
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
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
                structure[f"{member.name}的个人电器"] = {
                    "appliances": [appliance.name for appliance in member.personal_appliances]
                }
        
        return structure
    
    def get_home_structure_with_details(self):
        structure = {}
        for room_name, room in self.rooms.items():
            structure[room_name] = {
                "appliances": [
                    {
                        "unique_id": a.unique_id,
                        "name": a.name,
                        "type": a.appliance_type,
                        "power_watts": a.power_watts
                    }
                    for a in room.appliances
                ]
            }
        
        for member in self.members:
            if member.personal_appliances:
                structure[f"{member.name}的个人电器"] = {
                    "appliances": [
                        {
                            "unique_id": a.unique_id,
                            "name": a.name,
                            "type": a.appliance_type,
                            "power_watts": a.power_watts
                        }
                        for a in member.personal_appliances
                    ]
                }
        
        return structure
    
    def get_members_info(self):
        return [member.to_dict() for member in self.members]
    
    def get_total_energy_consumption(self):
        total = 0
        for appliance in self.appliance_registry.values():
            total += appliance.get_total_energy()
        return total


