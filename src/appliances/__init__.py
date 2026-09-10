from .base import BaseAppliance
from .television import TV
from .air_conditioner import AirConditioner
from .refrigerator import Refrigerator
from .rice_cooker import RiceCooker
from .microwave import Microwave
from .induction_cooker import InductionCooker
from .range_hood import RangeHood
from .light import Light
from .lamp import Lamp
from .computer import Computer
from .phone import Phone
from .electric_vehicle import ElectricVehicle
from .water_heater import WaterHeater
from .washing_machine import WashingMachine
from .vacuum_cleaner import VacuumCleaner
from .space_heater import SpaceHeater
from .fan import Fan
from .dehumidifier import Dehumidifier
from .clothes_dryer import ClothesDryer
from .dishwasher import Dishwasher
from .kettle import Kettle
from .toaster import Toaster
from .oven import Oven
from .freezer import Freezer
from .router import Router
from .game_console import GameConsole
from .monitor import Monitor
from .ebike import Ebike
from .catalog import apply_appliance_meta

APPLIANCE_REGISTRY = {
    "TV": TV,
    "AirConditioner": AirConditioner,
    "Refrigerator": Refrigerator,
    "RiceCooker": RiceCooker,
    "Microwave": Microwave,
    "InductionCooker": InductionCooker,
    "RangeHood": RangeHood,
    "Light": Light,
    "DeskLamp": Lamp,
    "Computer": Computer,
    "Laptop": Computer,
    "Phone": Phone,
    "ElectricVehicle": ElectricVehicle,
    "WaterHeater": WaterHeater,
    "WashingMachine": WashingMachine,
    "VacuumCleaner": VacuumCleaner,
    "SpaceHeater": SpaceHeater,
    "Fan": Fan,
    "Dehumidifier": Dehumidifier,
    "ClothesDryer": ClothesDryer,
    "Dishwasher": Dishwasher,
    "Kettle": Kettle,
    "Toaster": Toaster,
    "Oven": Oven,
    "Freezer": Freezer,
    "Router": Router,
    "GameConsole": GameConsole,
    "Monitor": Monitor,
    "Ebike": Ebike,
}

def create_appliance(name, location=None, owner=None, location_id=None, owner_id=None):
    if name not in APPLIANCE_REGISTRY:
        raise ValueError(f"Unknown appliance type: {name}")
    
    appliance_class = APPLIANCE_REGISTRY[name]
    appliance = appliance_class(location=location, owner=owner, location_id=location_id, owner_id=owner_id)
    return apply_appliance_meta(appliance, name)

def create_appliance_from_config(appliance_type, config, location=None, owner=None, location_id=None, owner_id=None):
    if appliance_type not in APPLIANCE_REGISTRY:
        raise ValueError(f"Unknown appliance type: {appliance_type}")
    
    appliance_class = APPLIANCE_REGISTRY[appliance_type]
    appliance = appliance_class.from_config(config, location=location, owner=owner, 
                                            location_id=location_id, owner_id=owner_id)
    return apply_appliance_meta(appliance, appliance_type)

def get_supported_appliances():
    return list(APPLIANCE_REGISTRY.keys())

def get_supported_appliances_text():
    return ", ".join(get_supported_appliances())

def get_all_appliance_schemas():
    schemas = {}
    for name, appliance_class in APPLIANCE_REGISTRY.items():
        schemas[name] = appliance_class.get_config_schema()
    return schemas

def get_appliance_schemas_text():
    schemas = get_all_appliance_schemas()
    lines = []
    for name, schema in schemas.items():
        fields = []
        for field_name, field_info in schema['config_fields'].items():
            field_desc = f"{field_name}({field_info['type']})"
            if field_info.get('required'):
                field_desc += "[required]"
            if 'default' in field_info:
                field_desc += f"[default:{field_info['default']}]"
            fields.append(field_desc)
        lines.append(f"{name}: {', '.join(fields)}")
    return "\n".join(lines)
