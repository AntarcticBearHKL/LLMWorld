from abc import ABC, abstractmethod

from .catalog import battery_kwh as catalog_battery_kwh, default_soc as catalog_default_soc

class BaseAppliance(ABC):
    def __init__(self, name, power_watts, appliance_type, brand=None, age=0, 
                 is_exclusive=False, location=None, owner=None, location_id=None, owner_id=None,
                 standby_watts=0, duty_cycle=1.0, flexible=False, season="annual", preferred_window=""):
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
        self.standby_watts = standby_watts
        self.duty_cycle = duty_cycle
        self.flexible = flexible
        self.season = season
        self.preferred_window = preferred_window
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
            "standby_watts": self.standby_watts,
            "duty_cycle": self.duty_cycle,
            "flexible": self.flexible,
            "season": self.season,
            "preferred_window": self.preferred_window,
            "available_actions": self.get_available_actions()
        }


class OnDemandAppliance(BaseAppliance):
    def __init__(self, name, power_watts, brand=None, age=0, is_exclusive=False, 
                 location=None, owner=None, location_id=None, owner_id=None, **meta):
        super().__init__(name, power_watts, "on_demand", brand, age, is_exclusive,
                        location, owner, location_id, owner_id, **meta)
    
    def get_available_actions(self):
        return ["use", "idle"]
    
    def to_dict(self):
        base = super().to_dict()
        base["description"] = "Device that only consumes power when in use (switchable)"
        base["action_description"] = {
            "use": "Use the device (consumes power)",
            "idle": "Do not use the device (no power consumption)"
        }
        if self.is_exclusive:
            base["exclusive_note"] = "Exclusive resource: only one person can use it at a time"
        return base


class ChargingAppliance(BaseAppliance):
    def __init__(self, name, power_watts, brand=None, age=0, is_exclusive=False,
                 location=None, owner=None, location_id=None, owner_id=None,
                 battery_kwh=None, soc=None, **meta):
        super().__init__(name, power_watts, "charging", brand, age, is_exclusive,
                        location, owner, location_id, owner_id, **meta)
        self.battery_kwh = battery_kwh if battery_kwh is not None else catalog_battery_kwh(self.name)
        self.soc = soc if soc is not None else catalog_default_soc(self.name)

    def charge_deficit_kwh(self):
        """Energy (kWh) needed to fill the battery from its current state of charge."""
        if self.battery_kwh is None:
            return None
        soc = self.soc if self.soc is not None else 0.0
        return max(0.0, (1.0 - soc) * self.battery_kwh)

    def get_available_actions(self):
        return ["charge_home", "charge_external", "use", "idle"]
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "description": "Charging device (can be charged using home or external power)",
            "battery_kwh": self.battery_kwh,
            "soc": self.soc,
            "action_description": {
                "charge_home": "Charge with home power (counts toward home electricity)",
                "charge_external": "Charge with external power (not counted toward home electricity)",
                "use": "Use the device (consumes previously stored charge, no direct power draw)",
                "idle": "Neither use nor charge"
            }
        })
        if self.is_exclusive:
            base["exclusive_note"] = "Exclusive resource: only one person can use it at a time; the user is responsible for taking it out and returning it"
        return base


class AlwaysOnAppliance(BaseAppliance):
    def __init__(self, name, power_watts, daily_energy_kwh=None, brand=None, age=0, 
                 location=None, owner=None, location_id=None, owner_id=None, **meta):
        super().__init__(name, power_watts, "always_on", brand, age, False,
                        location, owner, location_id, owner_id, **meta)
        self.daily_energy_kwh = daily_energy_kwh if daily_energy_kwh is not None else (power_watts / 1000.0) * 24
    
    def _calculate_energy_logic(self, duration_hours, **kwargs):
        return (self.daily_energy_kwh / 24.0) * duration_hours
    
    def get_available_actions(self):
        return []
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "description": "Always-on device (runs automatically, no operation needed)",
            "daily_energy_kwh": self.daily_energy_kwh,
            "action_description": {}
        })
        return base


class CycleAppliance(BaseAppliance):
    def __init__(self, name, power_watts, energy_per_cycle_kwh, cycle_minutes=60, brand=None, age=0,
                 is_exclusive=False, location=None, owner=None, location_id=None, owner_id=None, **meta):
        super().__init__(name, power_watts, "cycle", brand, age, is_exclusive,
                        location, owner, location_id, owner_id, **meta)
        self.energy_per_cycle_kwh = energy_per_cycle_kwh
        self.cycle_minutes = cycle_minutes
    
    def get_available_actions(self):
        return ["run", "idle"]
    
    def _calculate_energy_logic(self, duration_hours, **kwargs):
        cycle_hours = self.cycle_minutes / 60.0
        return self.energy_per_cycle_kwh * min(1.0, duration_hours / cycle_hours)
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "energy_per_cycle_kwh": self.energy_per_cycle_kwh,
            "cycle_minutes": self.cycle_minutes,
            "action_description": {
                "run": "run one cycle (consumes cycle energy)",
                "idle": "not running"
            }
        })
        return base
