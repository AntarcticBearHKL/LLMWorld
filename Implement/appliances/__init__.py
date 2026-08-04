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

APPLIANCE_REGISTRY = {
    "电视": TV,
    "空调": AirConditioner,
    "冰箱": Refrigerator,
    "电饭煲": RiceCooker,
    "微波炉": Microwave,
    "电磁炉": InductionCooker,
    "油烟机": RangeHood,
    "灯": Light,
    "台灯": Lamp,
    "电脑": Computer,
    "手机": Phone,
    "电动汽车": ElectricVehicle,
    "热水器": WaterHeater,
    "洗衣机": WashingMachine,
    "吸尘器": VacuumCleaner,
}

def create_appliance(name, location=None, owner=None, location_id=None, owner_id=None):
    if name not in APPLIANCE_REGISTRY:
        raise ValueError(f"未知的电器类型: {name}")
    
    appliance_class = APPLIANCE_REGISTRY[name]
    return appliance_class(location=location, owner=owner, location_id=location_id, owner_id=owner_id)

def create_appliance_from_config(appliance_type, config, location=None, owner=None, location_id=None, owner_id=None):
    if appliance_type not in APPLIANCE_REGISTRY:
        raise ValueError(f"未知的电器类型: {appliance_type}")
    
    appliance_class = APPLIANCE_REGISTRY[appliance_type]
    return appliance_class.from_config(config, location=location, owner=owner, 
                                      location_id=location_id, owner_id=owner_id)

def get_supported_appliances():
    return list(APPLIANCE_REGISTRY.keys())

def get_supported_appliances_text():
    return "、".join(get_supported_appliances())

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
                field_desc += "[必填]"
            if 'default' in field_info:
                field_desc += f"[默认:{field_info['default']}]"
            fields.append(field_desc)
        lines.append(f"{name}: {', '.join(fields)}")
    return "\n".join(lines)
