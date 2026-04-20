from .room import Room
from .member import Member
from .appliance import OnDemandAppliance, ChargingAppliance, AlwaysOnAppliance

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
        return structure
    
    def get_home_structure_with_details(self):
        structure = {}
        for room_name, room in self.rooms.items():
            structure[room_name] = {
                "appliances": [
                    {
                        "unique_id": a.unique_id,
                        "name": a.name,
                        "type": a.get_type(),
                        "power_watts": a.power_watts
                    }
                    for a in room.appliances
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


def create_default_home():
    home = Home("家庭")
    
    living_room = Room("客厅")
    living_room.add_appliance(OnDemandAppliance("living_tv", "电视", 150))
    living_room.add_appliance(OnDemandAppliance("living_ac", "空调", 2000))
    living_room.add_appliance(OnDemandAppliance("living_vacuum", "吸尘器", 1200))
    living_room.add_appliance(OnDemandAppliance("living_light", "灯", 60))
    
    kitchen = Room("厨房")
    kitchen.add_appliance(AlwaysOnAppliance("kitchen_fridge", "冰箱", 100, daily_energy_kwh=1.2))
    kitchen.add_appliance(OnDemandAppliance("kitchen_rice_cooker", "电饭煲", 800))
    kitchen.add_appliance(OnDemandAppliance("kitchen_microwave", "微波炉", 1000))
    kitchen.add_appliance(OnDemandAppliance("kitchen_induction", "电磁炉", 2000))
    kitchen.add_appliance(OnDemandAppliance("kitchen_hood", "油烟机", 200))
    kitchen.add_appliance(OnDemandAppliance("kitchen_light", "灯", 40))
    
    bedroom1 = Room("卧室1")
    bedroom1.add_appliance(OnDemandAppliance("bedroom1_ac", "空调", 1800))
    bedroom1.add_appliance(OnDemandAppliance("bedroom1_lamp", "台灯", 15))
    bedroom1.add_appliance(ChargingAppliance("bedroom1_phone", "手机", 20, battery_capacity_kwh=0.015))
    bedroom1.add_appliance(OnDemandAppliance("bedroom1_computer", "电脑", 200))

    bedroom2 = Room("卧室2")
    bedroom2.add_appliance(OnDemandAppliance("bedroom2_ac", "空调", 1800))
    bedroom2.add_appliance(OnDemandAppliance("bedroom2_lamp", "台灯", 15))
    bedroom2.add_appliance(ChargingAppliance("bedroom2_phone", "手机", 20, battery_capacity_kwh=0.015))

    bedroom3 = Room("卧室3")
    bedroom3.add_appliance(OnDemandAppliance("bedroom3_ac", "空调", 1800))
    bedroom3.add_appliance(OnDemandAppliance("bedroom3_lamp", "台灯", 15))
    bedroom3.add_appliance(ChargingAppliance("bedroom3_phone", "手机", 20, battery_capacity_kwh=0.015))
    
    bathroom = Room("卫生间")
    bathroom.add_appliance(OnDemandAppliance("bathroom_heater", "热水器", 3000))
    bathroom.add_appliance(OnDemandAppliance("bathroom_washer", "洗衣机", 500))
    bathroom.add_appliance(OnDemandAppliance("bathroom_light", "灯", 30))

    garage = Room("garage")
    garage.add_appliance(ChargingAppliance("garage_ev", "电动汽车", 7000, battery_capacity_kwh=60, charge_efficiency=0.85))
    
    home.add_room(living_room)
    home.add_room(kitchen)
    home.add_room(bedroom1)
    home.add_room(bedroom2)
    home.add_room(bedroom3)
    home.add_room(bathroom)
    home.add_room(garage)
    
    mem1 = Member("爸爸", 45, "工程师", "勤劳、负责", "节能意识中等")
    mem2 = Member("妈妈", 43, "教师", "勤劳、负责", "节能意识中等")
    
    home.add_member(mem1)
    home.add_member(mem2)
    
    return home
