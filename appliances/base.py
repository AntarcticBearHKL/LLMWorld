from abc import ABC, abstractmethod

class BaseAppliance(ABC):
    def __init__(self, name, power_watts, appliance_type, location=None, owner=None):
        self.name = name
        self.power_watts = power_watts
        self.appliance_type = appliance_type
        self.location = location
        self.owner = owner
        self.usage_log = []
        self.unique_id = self._generate_unique_id()
    
    def _generate_unique_id(self):
        parts = []
        if self.location:
            location_map = {
                "客厅": "living",
                "厨房": "kitchen",
                "卧室1": "bedroom1",
                "卧室2": "bedroom2",
                "卧室3": "bedroom3",
                "卫生间": "bathroom",
                "车库": "garage"
            }
            parts.append(location_map.get(self.location, self.location.lower()))
        
        if self.owner:
            owner_map = {
                "爸爸": "dad",
                "妈妈": "mom",
                "儿子": "son"
            }
            parts.append(owner_map.get(self.owner, self.owner.lower()))
        
        name_map = {
            "电视": "tv",
            "空调": "ac",
            "冰箱": "fridge",
            "电饭煲": "rice_cooker",
            "微波炉": "microwave",
            "电磁炉": "induction",
            "油烟机": "hood",
            "灯": "light",
            "台灯": "lamp",
            "电脑": "computer",
            "手机": "phone",
            "电动汽车": "ev",
            "热水器": "heater",
            "洗衣机": "washer",
            "吸尘器": "vacuum"
        }
        parts.append(name_map.get(self.name, self.name.lower()))
        
        return "_".join(parts)
    
    def calculate_energy(self, start_minutes, end_minutes, power_source="home", **kwargs):
        duration_minutes = end_minutes - start_minutes
        duration_hours = duration_minutes / 60.0
        
        if power_source == "external":
            return 0
        
        energy_kwh = self._calculate_energy_logic(duration_hours, **kwargs)
        return energy_kwh
    
    def _calculate_energy_logic(self, duration_hours, **kwargs):
        return (self.power_watts / 1000.0) * duration_hours
    
    @abstractmethod
    def get_available_actions(self):
        pass
    
    def log_usage(self, start_time, end_time, energy_kwh, **kwargs):
        self.usage_log.append({
            "start_time": start_time,
            "end_time": end_time,
            "energy_kwh": energy_kwh,
            **kwargs
        })
    
    def get_total_energy(self):
        return sum(log["energy_kwh"] for log in self.usage_log)
    
    def to_dict(self):
        return {
            "unique_id": self.unique_id,
            "name": self.name,
            "type": self.appliance_type,
            "power_watts": self.power_watts,
            "available_actions": self.get_available_actions()
        }


class OnDemandAppliance(BaseAppliance):
    def __init__(self, name, power_watts, location=None, owner=None):
        super().__init__(name, power_watts, "on_demand", location, owner)
    
    def get_available_actions(self):
        return ["use", "idle"]
    
    def to_dict(self):
        base = super().to_dict()
        base["description"] = "使用时才耗电的设备（可开关）"
        base["action_description"] = {
            "use": "使用该设备（耗电）",
            "idle": "不使用该设备（不耗电）"
        }
        return base


class ChargingAppliance(BaseAppliance):
    def __init__(self, name, power_watts, location=None, owner=None):
        super().__init__(name, power_watts, "charging", location, owner)
    
    def get_available_actions(self):
        return ["charge_home", "charge_external", "use", "idle"]
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "description": "充电设备（可使用家庭电力或外部电力充电）",
            "action_description": {
                "charge_home": "使用家庭电力充电（计入家庭用电）",
                "charge_external": "使用外部电力充电（不计入家庭用电）",
                "use": "使用设备（消耗之前充入的电量，不耗电）",
                "idle": "不使用也不充电"
            }
        })
        return base


class AlwaysOnAppliance(BaseAppliance):
    def __init__(self, name, power_watts, daily_energy_kwh=None, location=None, owner=None):
        super().__init__(name, power_watts, "always_on", location, owner)
        self.daily_energy_kwh = daily_energy_kwh if daily_energy_kwh is not None else (power_watts / 1000.0) * 24
    
    def _calculate_energy_logic(self, duration_hours, **kwargs):
        return (self.daily_energy_kwh / 24.0) * duration_hours
    
    def get_available_actions(self):
        return []
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "description": "持续耗电设备（无需操作，自动运行）",
            "daily_energy_kwh": self.daily_energy_kwh,
            "action_description": {}
        })
        return base
