from engine import Home, Room, Member
from appliances import create_appliance_from_config


def _personality_str(member_config):

    pers = member_config.get("personality", {})
    parts = [', '.join(pers.get("traits", []))]
    if pers.get("behavior_text"):
        parts.append("Behavior tendency: " + pers["behavior_text"])
    if pers.get("news_sensitivity"):
        parts.append("News/policy sensitivity: " + pers["news_sensitivity"])
    return ". ".join(p for p in parts if p)


def create_home_from_household(household):

    home_config = household['home']
    members_config = household['members']

    home = Home(home_config['name'])

    for room_config in home_config['rooms']:
        room = Room(room_config['name'])
        for appliance in room_config['appliances']:
            appliance_obj = create_appliance_from_config(
                appliance['type'], appliance, location=room_config['name'])
            room.add_appliance(appliance_obj)
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

        for appliance in member_config.get('personal_appliances', []):
            appliance_obj = create_appliance_from_config(
                appliance['type'], appliance, owner=member_config['name'])
            member.add_personal_appliance(appliance_obj)

        home.add_member(member)

    return home

