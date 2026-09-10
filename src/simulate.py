from engine import Home, Room, Member
from appliances import create_appliance_from_config
from appliances.catalog import appliance_family, PERSONAL_DEVICE_TYPES, backfill_power


def _personality_str(member_config):

    pers = member_config.get("personality", {})
    parts = [', '.join(pers.get("traits", []))]
    if pers.get("behavior_text"):
        parts.append("Behavior tendency: " + pers["behavior_text"])
    if pers.get("news_sensitivity"):
        parts.append("News/policy sensitivity: " + pers["news_sensitivity"])
    return ". ".join(p for p in parts if p)


def _family_of(appliance):

    return appliance_family(getattr(appliance, "name", None))


GLOBAL_UNIQUE_FAMILIES = {"ElectricVehicle"}


def _find_family_room_fixture(home, family, bedroom):

    if family in GLOBAL_UNIQUE_FAMILIES:
        for appliance in home.appliance_registry.values():
            if _family_of(appliance) == family:
                room = home.get_room(appliance.location) if appliance.location else None
                return room, appliance
        return None, None

    if bedroom is not None:
        for appliance in bedroom.appliances:
            if _family_of(appliance) == family:
                return bedroom, appliance
        return None, None

    for appliance in home.appliance_registry.values():
        if getattr(appliance, "owner", None) is not None:
            continue
        if _family_of(appliance) == family:
            room = home.get_room(appliance.location) if appliance.location else None
            return room, appliance
    return None, None


def _remove_room_appliance(home, room, appliance):

    if room is not None and appliance in room.appliances:
        room.appliances.remove(appliance)
    home.appliance_registry.pop(appliance.unique_id, None)


def create_home_from_household(household):

    home_config = household['home']
    members_config = household['members']

    home = Home(home_config['name'])
    dedup_removed = 0

    rooms_by_name = {}
    for room_config in home_config['rooms']:
        room = Room(room_config['name'])
        seen_families = set()
        for appliance in room_config['appliances']:
            if isinstance(appliance, str):
                appliance = {"type": appliance}
            if not isinstance(appliance, dict):
                continue
            app_type = appliance.get('type')
            if not app_type:
                continue
            family = appliance_family(app_type)
            if family in seen_families:
                dedup_removed += 1
                print(f"[Dedup] removed duplicate {app_type} in {room_config['name']} (family {family})")
                continue
            seen_families.add(family)
            appliance_cfg = backfill_power(appliance, location=room_config['name'])
            appliance_obj = create_appliance_from_config(
                app_type, appliance_cfg, location=room_config['name'])
            room.add_appliance(appliance_obj)
        rooms_by_name[room.name] = room
        home.add_room(room)

    for member_config in members_config:
        member = Member(
            member_config['name'],
            member_config['age'],
            member_config['occupation'],
            _personality_str(member_config),
            member_config['habits'],
            bedroom=member_config.get('bedroom'),
            cultural_background=member_config.get('cultural_background'),
            source_persona_index=member_config.get('source_persona_index'),
            work_schedule=member_config.get('work_schedule'),
            health=member_config.get('health'),
        )

        bedroom = rooms_by_name.get(member_config.get('bedroom'))

        seen_personal_families = set()
        for appliance in member_config.get('personal_appliances', []):
            if isinstance(appliance, str):
                appliance = {"type": appliance}
            if not isinstance(appliance, dict):
                continue
            app_type = appliance.get('type')
            if not app_type:
                continue
            family = appliance_family(app_type)
            if family in seen_personal_families:
                dedup_removed += 1
                print(f"[Dedup] skipped duplicate personal {app_type} of {member_config['name']} "
                      f"(family {family})")
                continue
            fixture_room, fixture = _find_family_room_fixture(home, family, bedroom)
            if fixture is not None:
                if app_type in PERSONAL_DEVICE_TYPES:
                    _remove_room_appliance(home, fixture_room, fixture)
                    dedup_removed += 1
                    print(f"[Dedup] personal {app_type} of {member_config['name']} replaces room appliance "
                          f"{fixture.unique_id}")
                else:
                    dedup_removed += 1
                    print(f"[Dedup] skipped personal {app_type} of {member_config['name']} "
                          f"(room fixture {fixture.unique_id} kept)")
                    continue
            seen_personal_families.add(family)
            appliance_cfg = backfill_power(appliance, location=None)
            appliance_obj = create_appliance_from_config(
                app_type, appliance_cfg, owner=member_config['name'])
            member.add_personal_appliance(appliance_obj)

        home.add_member(member)

    print(f"[Dedup] removed {dedup_removed} duplicate appliances")
    return home

