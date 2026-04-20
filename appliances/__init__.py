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

def create_appliance(name, location=None, owner=None):
    if name not in APPLIANCE_REGISTRY:
        raise ValueError(f"未知的电器类型: {name}")
    
    appliance_class = APPLIANCE_REGISTRY[name]
    return appliance_class(location=location, owner=owner)
