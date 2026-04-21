from abc import ABC, abstractmethod

class BaseAppliance(ABC):
    def __init__(self, name, power_watts, appliance_type, brand=None, age=0, 
                 is_exclusive=False, location=None, owner=None, location_id=None, owner_id=None):
        self.name = name
        self.power_watts = power_watts
        self.appliance_type = appliance_type
        self.brand = brand
        self.age = age
        self.is_exclusive = is_exclusive
        self.location = location
        self.owner = owner
        self.location_id = location_id
        self.owner_id = owner_id
        self.usage_log = []
        self.unique_id = self._generate_unique_id()
    
    def _generate_unique_id(self):
        parts = []
        
        if self.location_id:
            parts.append(self.location_id)
        elif self.location:
            parts.append(self._to_snake_case(self.location))
        
        if self.owner_id:
            parts.append(self.owner_id)
        elif self.owner:
            parts.append(self._to_snake_case(self.owner))
        
        parts.append(self._to_snake_case(self.name))
        
        return "_".join(parts)
    
    def _to_snake_case(self, text):
        import re
        text = text.strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s-]+', '_', text)
        text = text.lower()
        return text
    
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
    
    @classmethod
    @abstractmethod
    def get_config_schema(cls):
        pass
    
    @classmethod
    @abstractmethod
    def from_config(cls, config, location=None, owner=None, location_id=None, owner_id=None):
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
            "brand": self.brand,
            "age": self.age,
            "is_exclusive": self.is_exclusive,
            "available_actions": self.get_available_actions()
        }


class OnDemandAppliance(BaseAppliance):
    def __init__(self, name, power_watts, brand=None, age=0, is_exclusive=False, 
                 location=None, owner=None, location_id=None, owner_id=None):
        super().__init__(name, power_watts, "on_demand", brand, age, is_exclusive,
                        location, owner, location_id, owner_id)
    
    def get_available_actions(self):
        return ["use", "idle"]
    
    def to_dict(self):
        base = super().to_dict()
        base["description"] = "使用时才耗电的设备（可开关）"
        base["action_description"] = {
            "use": "使用该设备（耗电）",
            "idle": "不使用该设备（不耗电）"
        }
        if self.is_exclusive:
            base["exclusive_note"] = "独占资源：同一时间只能一人使用"
        return base


class ChargingAppliance(BaseAppliance):
    def __init__(self, name, power_watts, brand=None, age=0, is_exclusive=False,
                 location=None, owner=None, location_id=None, owner_id=None):
        super().__init__(name, power_watts, "charging", brand, age, is_exclusive,
                        location, owner, location_id, owner_id)
    
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
        if self.is_exclusive:
            base["exclusive_note"] = "独占资源：同一时间只能一人使用，使用者负责开出和归还"
        return base


class AlwaysOnAppliance(BaseAppliance):
    def __init__(self, name, power_watts, daily_energy_kwh=None, brand=None, age=0, 
                 location=None, owner=None, location_id=None, owner_id=None):
        super().__init__(name, power_watts, "always_on", brand, age, False,
                        location, owner, location_id, owner_id)
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
