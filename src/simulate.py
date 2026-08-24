import argparse
import json
import os
import sys
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from engine import Home, Room, Member, World, DateHelper, WeatherAPI
from engine import utils
from appliances import create_appliance_from_config
import config


def load_world(world_id):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    world_path = os.path.join(project_root, 'worlds', world_id)

    if not os.path.exists(world_path):
        print(f"Error: world '{world_id}' not found")
        print(f"Please first run 'python src/generate_world.py {world_id} --count 3' to generate the world")
        exit(1)

    with open(os.path.join(world_path, 'world.json'), 'r', encoding='utf-8') as f:
        world_meta = json.load(f)

    postcode = world_meta['district']['postcode']
    district_path = os.path.join(world_path, postcode)

    with open(os.path.join(district_path, 'district.json'), 'r', encoding='utf-8') as f:
        district_info = json.load(f)

    households = []
    for house_info in world_meta['households']:
        house_id = house_info['house_id']
        house_path = os.path.join(district_path, house_id)

        with open(os.path.join(house_path, 'household.json'), 'r', encoding='utf-8') as f:
            household = json.load(f)

        households.append({
            'house_id': house_id,
            'household': household
        })

    return world_meta, district_info, households


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
            member_config['habits']
        )

        for appliance in member_config.get('personal_appliances', []):
            appliance_obj = create_appliance_from_config(
                appliance['type'], appliance, owner=member_config['name'])
            member.add_personal_appliance(appliance_obj)

        home.add_member(member)

    return home


def parse_args():
    parser = argparse.ArgumentParser(description="LLM household electricity simulation")
    parser.add_argument("world_id", help="World ID (folder name under worlds/)")
    parser.add_argument("--days", type=int, default=None, help=f"Simulation days (default {config.DEFAULT_DAYS})")
    parser.add_argument("--date", type=str, default=None, help="Start date, e.g. '2026-04-21' (default: auto-resume)")
    parser.add_argument("--house", type=int, default=None, help="Household index (0-based, default 0)")
    parser.add_argument("--season", type=str, default=None, help=f"Season (default {config.DEFAULT_SEASON})")
    parser.add_argument("--weather", type=str, default=None, help=f"Weather (default {config.DEFAULT_WEATHER})")
    parser.add_argument("--temp", type=float, default=None, help=f"Temperature (default {config.DEFAULT_TEMPERATURE})")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED, help="Random seed (reproducible)")
    parser.add_argument("--no-input", action="store_true", help="Automatic mode: do not ask any input, use default values")
    return parser.parse_args()
