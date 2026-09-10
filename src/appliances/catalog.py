"""Canonical appliance catalog shared by world generation and simulation.

Provides:
  - DEFAULT_POWER_WATTS: estimated rated power (watts) per supported appliance type
  - DEFAULT_DAILY_ENERGY_KWH: estimated daily energy for always-on devices
  - BATTERY_KWH: nominal battery capacity for charging appliances
  - DEFAULT_SOC: default state of charge for charging appliances
  - PERSONAL_DEVICE_TYPES: device classes owned by a person (person-bound)
  - APPLIANCE_META: per-type experiment metadata (category/standby/duty/flexible/season)
  - appliance_meta(): copy of the metadata entry for a type
  - apply_appliance_meta(): copy metadata fields onto a constructed appliance
  - appliance_family(): collapse type aliases (Laptop/Computer) to one family
  - estimated_power_watts(): location-aware power estimate
  - battery_kwh(): nominal battery capacity for a charging appliance type
  - default_soc(): default state of charge for a charging appliance type
  - backfill_power(): return a config dict guaranteed to carry a numeric `power`
  - ID_TYPE_SYNONYMS: map hallucinated id fragments back to canonical type tokens

This module has no dependencies on the engine so it can be imported anywhere.
"""

# Estimated rated power (watts) per supported appliance type.
DEFAULT_POWER_WATTS = {
    "TV": 150,
    "AirConditioner": 2000,
    "Refrigerator": 100,
    "RiceCooker": 800,
    "Microwave": 1000,
    "InductionCooker": 2000,
    "RangeHood": 200,
    "Light": 40,
    "DeskLamp": 15,
    "Computer": 200,
    "Laptop": 200,
    "Phone": 20,
    "ElectricVehicle": 7000,
    "WaterHeater": 3000,
    "WashingMachine": 500,
    "VacuumCleaner": 1200,
    "SpaceHeater": 2000,
    "Fan": 60,
    "Dehumidifier": 500,
    "ClothesDryer": 2500,
    "Dishwasher": 1800,
    "Kettle": 2000,
    "Toaster": 1200,
    "Oven": 2200,
    "Freezer": 100,
    "Router": 12,
    "GameConsole": 150,
    "Monitor": 30,
    "Ebike": 350,
}

# Plausible rated-power bounds (watts) per type; LLM-generated values outside
# these ranges are clamped, because strict json_schema drops minimum/maximum.
POWER_BOUNDS = {
    "TV": (30, 400),
    "AirConditioner": (700, 4000),
    "Refrigerator": (50, 300),
    "RiceCooker": (300, 1200),
    "Microwave": (600, 2000),
    "InductionCooker": (1000, 3500),
    "RangeHood": (50, 400),
    "Light": (3, 120),
    "DeskLamp": (3, 60),
    "Computer": (50, 600),
    "Laptop": (20, 300),
    "Phone": (2, 60),
    "ElectricVehicle": (1400, 11000),
    "WaterHeater": (1200, 5000),
    "WashingMachine": (300, 2500),
    "VacuumCleaner": (300, 2400),
    "SpaceHeater": (500, 3000),
    "Fan": (10, 150),
    "Dehumidifier": (150, 1000),
    "ClothesDryer": (1000, 4000),
    "Dishwasher": (700, 2500),
    "Kettle": (1000, 3000),
    "Toaster": (500, 2000),
    "Oven": (1000, 4000),
    "Freezer": (50, 300),
    "Router": (3, 40),
    "GameConsole": (30, 400),
    "Monitor": (10, 80),
    "Ebike": (100, 1000),
}

# Estimated daily energy (kWh/day) for always-on devices.
DEFAULT_DAILY_ENERGY_KWH = {
    "Refrigerator": 1.2,
    "Freezer": 1.0,
    "Router": 0.29,
}

# Nominal battery capacity (kWh) and default state of charge (0-1) for charging
# appliances. The usable charge in one day is bounded by the remaining deficit
# (1 - soc) * capacity, so a device can never absorb more than one battery.
BATTERY_KWH = {
    "ElectricVehicle": 60.0,
    "Ebike": 0.5,
    "Phone": 0.02,
}

DEFAULT_SOC = {
    "ElectricVehicle": 0.5,
    "Ebike": 0.5,
    "Phone": 0.3,
}


def battery_kwh(appliance_type):
    """Nominal battery capacity (kWh) for a charging appliance type (None if unknown)."""
    return BATTERY_KWH.get(appliance_type)


def default_soc(appliance_type):
    """Default state of charge (0-1) for a charging appliance type (None if unknown)."""
    return DEFAULT_SOC.get(appliance_type)

# Device classes that belong to a person rather than a room.
PERSONAL_DEVICE_TYPES = {"Phone", "Laptop", "Computer", "DeskLamp", "Ebike", "Monitor", "ElectricVehicle"}

# Per-type experiment metadata. `category` matches the appliance class category
# (on_demand / cycle / charging / always_on). Cycle types also carry the energy
# and duration of one full cycle.
APPLIANCE_META = {
    "TV": {"category": "on_demand", "standby_watts": 3, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "AirConditioner": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 0.6, "flexible": True, "season": "annual"},
    "Refrigerator": {"category": "always_on", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Freezer": {"category": "always_on", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Router": {"category": "always_on", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "RiceCooker": {"category": "cycle", "cycle_kwh": 0.25, "cycle_minutes": 40, "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Microwave": {"category": "on_demand", "standby_watts": 2, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "InductionCooker": {"category": "on_demand", "standby_watts": 1, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Oven": {"category": "cycle", "cycle_kwh": 1.5, "cycle_minutes": 60, "standby_watts": 2, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Kettle": {"category": "on_demand", "standby_watts": 1, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Toaster": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "RangeHood": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Light": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "DeskLamp": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Computer": {"category": "on_demand", "standby_watts": 2, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Laptop": {"category": "on_demand", "standby_watts": 1, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "Monitor": {"category": "on_demand", "standby_watts": 1, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "GameConsole": {"category": "on_demand", "standby_watts": 1, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "VacuumCleaner": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "annual"},
    "SpaceHeater": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "heating"},
    "Fan": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 1.0, "flexible": False, "season": "cooling"},
    "Dehumidifier": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 0.7, "flexible": False, "season": "heating"},
    "WaterHeater": {"category": "on_demand", "standby_watts": 0, "duty_cycle": 1.0, "flexible": True, "season": "annual"},
    "WashingMachine": {"category": "cycle", "cycle_kwh": 0.6, "cycle_minutes": 90, "standby_watts": 0, "duty_cycle": 1.0, "flexible": True, "season": "annual"},
    "ClothesDryer": {"category": "cycle", "cycle_kwh": 2.5, "cycle_minutes": 120, "standby_watts": 0, "duty_cycle": 1.0, "flexible": True, "season": "annual"},
    "Dishwasher": {"category": "cycle", "cycle_kwh": 1.1, "cycle_minutes": 120, "standby_watts": 2, "duty_cycle": 1.0, "flexible": True, "season": "annual"},
    "Phone": {"category": "charging", "standby_watts": 0, "duty_cycle": 1.0, "flexible": True, "season": "annual"},
    "ElectricVehicle": {"category": "charging", "standby_watts": 0, "duty_cycle": 1.0, "flexible": True, "season": "annual"},
    "Ebike": {"category": "charging", "standby_watts": 0, "duty_cycle": 1.0, "flexible": True, "season": "annual"},
}


def appliance_meta(appliance_type):
    """Return a copy of the metadata entry for an appliance type (empty if unknown)."""
    return dict(APPLIANCE_META.get(appliance_type) or {})


def apply_appliance_meta(obj, appliance_type):
    """Copy catalog metadata (standby/duty/flexible/season/cycle) onto an appliance."""
    meta = appliance_meta(appliance_type)
    if not meta:
        return obj
    obj.standby_watts = meta.get("standby_watts", 0)
    obj.duty_cycle = meta.get("duty_cycle", 1.0)
    obj.flexible = meta.get("flexible", False)
    obj.season = meta.get("season", "annual")
    obj.preferred_window = meta.get("preferred_window", "")
    if meta.get("category") == "cycle":
        if getattr(obj, "energy_per_cycle_kwh", None) is None:
            obj.energy_per_cycle_kwh = meta.get("cycle_kwh")
        if getattr(obj, "cycle_minutes", None) is None:
            obj.cycle_minutes = meta.get("cycle_minutes")
    return obj

# Type aliases that describe the same physical device family.
_TYPE_ALIASES = {
    "Laptop": "Computer",
    "Computer": "Computer",
    "DeskLamp": "DeskLamp",
}


def appliance_family(appliance_type):
    """Return a canonical family token for an appliance type.

    Laptop and Computer share one family so a home is never double-counted.
    """
    if appliance_type is None:
        return None
    return _TYPE_ALIASES.get(appliance_type, appliance_type)


def estimated_power_watts(appliance_type, location=None):
    """Location-aware estimated rated power (watts)."""
    if appliance_type == "AirConditioner" and location and "bedroom" in str(location).lower():
        return 1800
    if appliance_type == "Light":
        key = str(location or "").lower().replace(" ", "_")
        return {"living_room": 60, "kitchen": 40, "bathroom": 30}.get(
            key, DEFAULT_POWER_WATTS["Light"]
        )
    return DEFAULT_POWER_WATTS.get(appliance_type)


def backfill_power(config, location=None):
    """Return a copy of an appliance config with a usable numeric `power`.

    If `power` is missing or non-positive, fill it from the estimate for the
    type/location. Also fills daily_energy_kwh for refrigerators.
    """
    cfg = dict(config or {})
    power = cfg.get("power")
    if not isinstance(power, (int, float)) or isinstance(power, bool) or power <= 0:
        est = estimated_power_watts(cfg.get("type"), location)
        if est is not None:
            cfg["power"] = est
    bounds = POWER_BOUNDS.get(cfg.get("type"))
    power = cfg.get("power")
    if bounds and isinstance(power, (int, float)) and not isinstance(power, bool):
        low, high = bounds
        if power < low or power > high:
            est = estimated_power_watts(cfg.get("type"), location)
            cfg["power"] = est if est is not None else min(max(power, low), high)
    if cfg.get("type") == "Refrigerator" and not cfg.get("daily_energy_kwh"):
        cfg["daily_energy_kwh"] = DEFAULT_DAILY_ENERGY_KWH["Refrigerator"]
    return cfg


# Hallucinated id fragment -> canonical appliance type token.
ID_TYPE_SYNONYMS = {
    "laptop": "Laptop",
    "computer": "Computer",
    "pc": "Computer",
    "desktop": "Computer",
    "notebook": "Laptop",
    "macbook": "Laptop",
    "tv": "TV",
    "television": "TV",
    "ac": "AirConditioner",
    "aircon": "AirConditioner",
    "airconditioner": "AirConditioner",
    "air_conditioner": "AirConditioner",
    "heater": "WaterHeater",
    "waterheater": "WaterHeater",
    "water_heater": "WaterHeater",
    "boiler": "WaterHeater",
    "fridge": "Refrigerator",
    "refrigerator": "Refrigerator",
    "lamp": "DeskLamp",
    "desklamp": "DeskLamp",
    "desk_lamp": "DeskLamp",
    "light": "Light",
    "bulb": "Light",
    "washer": "WashingMachine",
    "washingmachine": "WashingMachine",
    "washing_machine": "WashingMachine",
    "vacuum": "VacuumCleaner",
    "vacuumcleaner": "VacuumCleaner",
    "vacuum_cleaner": "VacuumCleaner",
    "ricecooker": "RiceCooker",
    "rice_cooker": "RiceCooker",
    "microwave": "Microwave",
    "inductioncooker": "InductionCooker",
    "induction_cooker": "InductionCooker",
    "cooker": "InductionCooker",
    "rangehood": "RangeHood",
    "range_hood": "RangeHood",
    "hood": "RangeHood",
    "phone": "Phone",
    "mobile": "Phone",
    "smartphone": "Phone",
    "ev": "ElectricVehicle",
    "electricvehicle": "ElectricVehicle",
    "electric_vehicle": "ElectricVehicle",
    "spaceheater": "SpaceHeater",
    "electricheater": "SpaceHeater",
    "portableheater": "SpaceHeater",
    "fan": "Fan",
    "dehumidifier": "Dehumidifier",
    "dryer": "ClothesDryer",
    "clothesdryer": "ClothesDryer",
    "dishwasher": "Dishwasher",
    "kettle": "Kettle",
    "toaster": "Toaster",
    "oven": "Oven",
    "freezer": "Freezer",
    "router": "Router",
    "modem": "Router",
    "wifi": "Router",
    "gameconsole": "GameConsole",
    "console": "GameConsole",
    "monitor": "Monitor",
    "display": "Monitor",
    "ebike": "Ebike",
    "scooter": "Ebike",
    "ebikescooter": "Ebike",
}
