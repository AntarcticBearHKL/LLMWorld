class Room:
    def __init__(self, name):
        self.name = name
        self.appliances = []
    
    def add_appliance(self, appliance):
        self.appliances.append(appliance)
        return self
    
    def get_appliance(self, unique_id):
        for appliance in self.appliances:
            if appliance.unique_id == unique_id:
                return appliance
        return None
    
    def get_appliances_info(self):
        return [f"{a.name} ({a.get_type()})" for a in self.appliances]
    
    def to_dict(self):
        return {
            "name": self.name,
            "appliances": [a.to_dict() for a in self.appliances]
        }
