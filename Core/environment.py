class Appliance:
    def __init__(self, name, always_on=False):
        self.name = name
        self.always_on = always_on
        self.status = [always_on] * 144

class Room:
    def __init__(self, name):
        self.name = name
        self.appliances = []
    
    def add_appliance(self, appliance):
        self.appliances.append(appliance)
        return self
    
    def get_appliances_info(self):
        return [f"{a.name}{'（常开）' if a.always_on else ''}" for a in self.appliances]

class Member:
    def __init__(self, name, age, occupation, personality, habits):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.personality = personality
        self.habits = habits

class Home:
    def __init__(self, name):
        self.name = name
        self.rooms = {}
        self.members = []
    
    def add_room(self, room):
        self.rooms[room.name] = room
        return self
    
    def add_member(self, member):
        self.members.append(member)
        return self
    
    def get_room(self, room_name):
        return self.rooms.get(room_name)
    
    def to_json(self):
        home_structure = {}
        for room_name, room in self.rooms.items():
            home_structure[room_name] = [appliance.name for appliance in room.appliances]
        return home_structure
    
    def get_appliance(self, room_name, appliance_name):
        room = self.get_room(room_name)
        if room:
            for appliance in room.appliances:
                if appliance.name == appliance_name:
                    return appliance
        return None
    
    def get_home_structure(self):
        structure = {}
        for room_name, room in self.rooms.items():
            structure[room_name] = {
                "appliances": [appliance.name for appliance in room.appliances]
            }
        return structure
    
    def get_members_info(self):
        members_info = []
        for member in self.members:
            members_info.append({
                "name": member.name,
                "age": member.age,
                "occupation": member.occupation,
                "personality": member.personality,
                "habits": member.habits
            })
        return members_info

def create_default_home():
    home = Home("家庭")
    
    living_room = Room("客厅")
    living_room.add_appliance(Appliance("电视"))
    living_room.add_appliance(Appliance("空调"))
    living_room.add_appliance(Appliance("吸尘器"))
    living_room.add_appliance(Appliance("灯"))
    
    kitchen = Room("厨房")
    kitchen.add_appliance(Appliance("冰箱", always_on=True))
    kitchen.add_appliance(Appliance("电饭煲"))
    kitchen.add_appliance(Appliance("微波炉"))
    kitchen.add_appliance(Appliance("电磁炉"))
    kitchen.add_appliance(Appliance("油烟机"))
    kitchen.add_appliance(Appliance("灯"))
    
    bedroom1 = Room("卧室1")
    bedroom1.add_appliance(Appliance("空调"))
    bedroom1.add_appliance(Appliance("台灯"))
    bedroom1.add_appliance(Appliance("手机充电器"))
    bedroom1.add_appliance(Appliance("电脑"))

    bedroom2 = Room("卧室2")
    bedroom2.add_appliance(Appliance("空调"))
    bedroom2.add_appliance(Appliance("台灯"))
    bedroom2.add_appliance(Appliance("手机充电器"))

    bedroom3 = Room("卧室3")
    bedroom3.add_appliance(Appliance("空调"))
    bedroom3.add_appliance(Appliance("台灯"))
    bedroom3.add_appliance(Appliance("手机充电器"))
    
    bathroom = Room("卫生间")
    bathroom.add_appliance(Appliance("热水器"))
    bathroom.add_appliance(Appliance("洗衣机"))
    bathroom.add_appliance(Appliance("灯"))

    garage = Room("garage")
    bathroom.add_appliance(Appliance("电动汽车"))
    
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
