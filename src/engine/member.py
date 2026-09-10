import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from appliances import create_appliance

class Member:
    def __init__(self, name, age, occupation, personality, habits,
                 bedroom=None, cultural_background=None, source_persona_index=None,
                 work_schedule=None, health=None):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.personality = personality
        self.habits = habits
        self.bedroom = bedroom
        self.cultural_background = cultural_background
        self.source_persona_index = source_persona_index
        self.work_schedule = work_schedule
        self.health = health
        self.personal_appliances = []
    
    def add_personal_appliance(self, appliance):
        self.personal_appliances.append(appliance)
        return self
    
    def add_personal_appliance_by_name(self, appliance_name):
        appliance = create_appliance(appliance_name, owner=self.name)
        self.personal_appliances.append(appliance)
        return self
    
    def get_personal_appliance(self, appliance_name):
        for appliance in self.personal_appliances:
            if appliance.name == appliance_name:
                return appliance
        return None
    
    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "personality": self.personality,
            "habits": self.habits,
            "personal_appliances": [a.name for a in self.personal_appliances]
        }
