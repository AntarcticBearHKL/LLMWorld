"""Turn s4 appliance decisions into a 1440-minute household load profile.

The profile is a list of 1440 floats (watts per minute) plus a per-appliance
energy breakdown in kWh. Appliance parameters (rated power, duty cycle,
standby, cycle energy) come from the appliance registry built by
`simulate.create_home_from_household(household)`.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(_HERE)
for _path in (_HERE, _SRC):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from engine.utils import parse_time_range
from simulate import create_home_from_household
from appliances.base import AlwaysOnAppliance, ChargingAppliance
from appliances.catalog import appliance_family
import config


POWERED_ACTIONS = {"use", "run", "charge_home"}


def _cap_minutes(appliance):
    """Daily powered-minute cap for this appliance type (None = no cap)."""
    caps = getattr(config, "APPLIANCE_DAILY_CAP_MINUTES", {}) or {}
    return caps.get(getattr(appliance, "name", None))


def empty_profile():
    return [0.0] * 1440


def _segment_bounds(segment):
    if not isinstance(segment, dict):
        return None, None
    time_range = segment.get("time")
    if not time_range:
        return None, None
    return parse_time_range(time_range)


def _operation_watts(appliance, action, seg_minutes):
    """Constant watts drawn by one operation across its whole segment."""
    category = appliance.appliance_type

    if category == "on_demand":
        if action == "use":
            return (appliance.power_watts or 0) * (appliance.duty_cycle or 1.0)
        if action == "idle":
            return appliance.standby_watts or 0
        return 0.0

    if category == "charging":
        if action == "charge_home":
            return appliance.power_watts or 0
        return 0.0

    if category == "cycle":
        if action in ("run", "use"):
            cycle_minutes = appliance.cycle_minutes or 0
            factor = min(1.0, seg_minutes / cycle_minutes) if cycle_minutes > 0 else 1.0
            energy_kwh = (appliance.energy_per_cycle_kwh or 0.0) * factor
            seg_hours = seg_minutes / 60.0
            if seg_hours <= 0:
                return 0.0
            return energy_kwh / seg_hours * 1000.0
        if action == "idle":
            return appliance.standby_watts or 0
        return 0.0

    return 0.0


def _accumulate(registry, decisions_by_member):
    """Collect per-appliance minute contributions from every member's operations.

    Returns (contrib, referenced, best_action):
      contrib      {unique_id: [watts per minute]}, max over members per appliance-minute
      referenced   {unique_id: [bool per minute]}, minute touched by any operation
      best_action  {(unique_id, minute): (watts, action)}, explicit winners only
    """
    contrib = {unique_id: [0.0] * 1440 for unique_id in registry}
    referenced = {unique_id: [False] * 1440 for unique_id in registry}
    powered = {unique_id: set() for unique_id in registry}
    best_action = {}

    for segments in (decisions_by_member or {}).values():
        for segment in segments or []:
            start, end = _segment_bounds(segment)
            if start is None:
                continue
            seg_minutes = end - start
            for operation in segment.get("operations") or []:
                if not isinstance(operation, dict):
                    continue
                unique_id = operation.get("unique_id")
                appliance = registry.get(unique_id)
                if appliance is None:
                    continue
                action = operation.get("action")
                watts = _operation_watts(appliance, action, seg_minutes)
                for minute in range(start, end):
                    index = minute % 1440
                    referenced[unique_id][index] = True
                    if watts > contrib[unique_id][index]:
                        contrib[unique_id][index] = watts
                    if watts > 0:
                        key = (unique_id, index)
                        current = best_action.get(key)
                        if current is None or watts > current[0]:
                            best_action[key] = (watts, action)
                        if action in POWERED_ACTIONS:
                            powered[unique_id].add(index)

    # Clip each appliance's powered minutes to its daily cap (the s4 prompt
    # explicitly delegates this clipping to the downstream energy calculator).
    for unique_id, appliance in registry.items():
        cap = _cap_minutes(appliance)
        if cap is None:
            continue
        minutes = sorted(powered[unique_id])
        if len(minutes) <= cap:
            continue
        for index in minutes[cap:]:
            contrib[unique_id][index] = 0.0
            best_action.pop((unique_id, index), None)
            referenced[unique_id][index] = False

    # Battery ceiling for charging appliances: a day's home charging cannot
    # exceed the battery deficit (capacity x (1 - soc)). Walk the day in order;
    # once the deficit is met the remaining charge_home minutes draw nothing,
    # and the crossing minute is scaled to land exactly on the deficit.
    for unique_id, appliance in registry.items():
        if not isinstance(appliance, ChargingAppliance):
            continue
        deficit = appliance.charge_deficit_kwh()
        if deficit is None:
            continue
        remaining = deficit
        minutes = contrib[unique_id]
        for index in range(1440):
            watts = minutes[index]
            if watts <= 0:
                continue
            energy = watts / 60.0 / 1000.0
            if energy <= remaining:
                remaining -= energy
                continue
            watts = 0.0 if remaining <= 0 else remaining * 60.0 * 1000.0
            minutes[index] = watts
            key = (unique_id, index)
            if watts > 0:
                if key in best_action:
                    best_action[key] = (watts, best_action[key][1])
            else:
                best_action.pop(key, None)
                referenced[unique_id][index] = False
            remaining = 0.0

    return contrib, referenced, best_action


def build_load_profile(household, decisions_by_member, exclude_families=None):
    """household: the household.json dict; decisions_by_member: {member: [segment, ...]}.

    exclude_families: optional set of appliance family names (see
    appliances.catalog.appliance_family, e.g. {"ElectricVehicle", "Refrigerator"}).
    Matching appliances contribute 0.0 W to the profile and 0.0 to
    per_appliance_kwh (keys stay present so the shape is stable); this yields a
    behavior-attributable profile. Default None counts every appliance.

    Returns (profile_watts, per_appliance_kwh, total_kwh).
    """
    home = create_home_from_household(household)
    registry = home.appliance_registry
    contrib, referenced, _best = _accumulate(registry, decisions_by_member)
    excluded = set(exclude_families or ())

    for unique_id, appliance in registry.items():
        if isinstance(appliance, AlwaysOnAppliance):
            baseload_watts = (appliance.daily_energy_kwh or 0.0) / 24.0 * 1000.0
            contrib[unique_id] = [baseload_watts] * 1440
        elif isinstance(appliance, ChargingAppliance):
            continue
        else:
            standby_watts = appliance.standby_watts or 0
            if not standby_watts:
                continue
            for minute in range(1440):
                if not referenced[unique_id][minute]:
                    contrib[unique_id][minute] = standby_watts

    profile = empty_profile()
    per_appliance_kwh = {}
    for unique_id, minutes in contrib.items():
        appliance = registry.get(unique_id)
        if excluded and appliance_family(getattr(appliance, "name", None)) in excluded:
            per_appliance_kwh[unique_id] = 0.0
            continue
        energy = 0.0
        for minute in range(1440):
            watts = minutes[minute]
            energy += watts
            profile[minute] += watts
        per_appliance_kwh[unique_id] = energy / 60.0 / 1000.0

    total_kwh = sum(profile) / 60.0 / 1000.0
    return profile, per_appliance_kwh, total_kwh


def appliance_energy_by_action(household, decisions_by_member):
    """Explicit operation energy (kWh) per appliance and action.

    Only minutes named by an operation are counted (standby/baseload excluded);
    when two members use the same appliance in one minute the larger draw wins.
    Returns {unique_id: {action: kwh}}.
    """
    home = create_home_from_household(household)
    _contrib, _referenced, best_action = _accumulate(home.appliance_registry, decisions_by_member)
    result = {}
    for (unique_id, _minute), (watts, action) in best_action.items():
        by_action = result.setdefault(unique_id, {})
        by_action[action] = by_action.get(action, 0.0) + watts / 60.0 / 1000.0
    return result
