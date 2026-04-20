from abc import ABC, abstractmethod

class Appliance(ABC):
    def __init__(self, unique_id, name, power_watts):
        self.unique_id = unique_id
        self.name = name
        self.power_watts = power_watts
        self.usage_log = []
    
    @abstractmethod
    def calculate_energy(self, start_time, end_time, **kwargs):
        pass
    
    @abstractmethod
    def get_type(self):
        pass
    
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
            "type": self.get_type(),
            "power_watts": self.power_watts,
            "available_actions": self.get_available_actions()
        }


class OnDemandAppliance(Appliance):
    def __init__(self, unique_id, name, power_watts):
        super().__init__(unique_id, name, power_watts)
    
    def calculate_energy(self, start_time, end_time, **kwargs):
        duration_minutes = end_time - start_time
        duration_hours = duration_minutes / 60.0
        energy_kwh = (self.power_watts / 1000.0) * duration_hours
        return energy_kwh
    
    def get_type(self):
        return "on_demand"
    
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


class ChargingAppliance(Appliance):
    def __init__(self, unique_id, name, power_watts, battery_capacity_kwh, charge_efficiency=0.9):
        super().__init__(unique_id, name, power_watts)
        self.battery_capacity_kwh = battery_capacity_kwh
        self.charge_efficiency = charge_efficiency
        self.current_charge_kwh = 0
    
    def calculate_energy(self, start_time, end_time, charge_amount_kwh=None, **kwargs):
        if charge_amount_kwh is not None:
            actual_energy = charge_amount_kwh / self.charge_efficiency
            self.current_charge_kwh = min(self.current_charge_kwh + charge_amount_kwh, self.battery_capacity_kwh)
            return actual_energy
        else:
            duration_minutes = end_time - start_time
            duration_hours = duration_minutes / 60.0
            max_charge_energy = (self.power_watts / 1000.0) * duration_hours
            remaining_capacity = self.battery_capacity_kwh - self.current_charge_kwh
            charge_amount = min(max_charge_energy * self.charge_efficiency, remaining_capacity)
            actual_energy = charge_amount / self.charge_efficiency
            self.current_charge_kwh += charge_amount
            return actual_energy
    
    def discharge(self, amount_kwh):
        self.current_charge_kwh = max(0, self.current_charge_kwh - amount_kwh)
    
    def get_charge_percentage(self):
        return (self.current_charge_kwh / self.battery_capacity_kwh) * 100 if self.battery_capacity_kwh > 0 else 0
    
    def get_type(self):
        return "charging"
    
    def get_available_actions(self):
        return ["charge", "use", "idle"]
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "description": "可充电设备（充电时耗电，使用时放电）",
            "battery_capacity_kwh": self.battery_capacity_kwh,
            "charge_efficiency": self.charge_efficiency,
            "current_charge_kwh": self.current_charge_kwh,
            "charge_percentage": self.get_charge_percentage(),
            "action_description": {
                "charge": "充电（耗电）",
                "use": "使用设备（放电，不耗电）",
                "idle": "不使用也不充电"
            }
        })
        return base


class AlwaysOnAppliance(Appliance):
    def __init__(self, unique_id, name, power_watts, daily_energy_kwh=None):
        super().__init__(unique_id, name, power_watts)
        self.daily_energy_kwh = daily_energy_kwh if daily_energy_kwh is not None else (power_watts / 1000.0) * 24
    
    def calculate_energy(self, start_time, end_time, **kwargs):
        duration_minutes = end_time - start_time
        duration_hours = duration_minutes / 60.0
        energy_kwh = (self.daily_energy_kwh / 24.0) * duration_hours
        return energy_kwh
    
    def get_type(self):
        return "always_on"
    
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
