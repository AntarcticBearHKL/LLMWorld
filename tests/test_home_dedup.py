"""L1 offline tests for simulate.create_home_from_household dedup logic.

Zero API calls. goal.md §4 lists this function's dedup behaviour as an L1
priority target. Independent of any work-in-progress files.

Run:  .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT_ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from simulate import create_home_from_household  # noqa: E402
from appliances.catalog import appliance_family  # noqa: E402


def _member(name="Alex", bedroom="Bedroom 1", personal=None):
    return {"name": name, "age": 30, "occupation": "engineer", "personality": {},
            "habits": {}, "bedroom": bedroom, "personal_appliances": personal or []}


def _count_family(registry, family):
    return sum(1 for a in registry.values() if appliance_family(getattr(a, "name", None)) == family)


class RoomDedupTests(unittest.TestCase):
    def test_duplicate_room_family_removed(self):
        household = {
            "home": {"name": "H", "rooms": [{"name": "Kitchen", "appliances": [
                {"type": "Computer", "power": 200},
                {"type": "Laptop", "power": 100},
            ]}]},
            "members": [_member(personal=[])],
        }
        home = create_home_from_household(household)
        self.assertEqual(_count_family(home.appliance_registry, "Computer"), 1)
        self.assertEqual(len(home.get_room("Kitchen").appliances), 1)

    def test_distinct_families_kept(self):
        household = {
            "home": {"name": "H", "rooms": [{"name": "Kitchen", "appliances": [
                {"type": "TV", "power": 150},
                {"type": "Refrigerator", "power": 100},
            ]}]},
            "members": [_member(personal=[])],
        }
        home = create_home_from_household(household)
        self.assertEqual(len(home.get_room("Kitchen").appliances), 2)


class PersonalDedupTests(unittest.TestCase):
    def test_personal_device_replaces_room_fixture(self):
        household = {
            "home": {"name": "H", "rooms": [{"name": "Bedroom 1", "appliances": [
                {"type": "Computer", "power": 200},
            ]}]},
            "members": [_member(personal=[{"type": "Laptop", "power": 100}])],
        }
        home = create_home_from_household(household)
        self.assertEqual(len(home.get_room("Bedroom 1").appliances), 0)
        self.assertEqual(len(home.members[0].personal_appliances), 1)
        self.assertEqual(_count_family(home.appliance_registry, "Computer"), 1)
        self.assertEqual(home.members[0].personal_appliances[0].owner, "Alex")

    def test_non_personal_device_does_not_replace_room_fixture(self):
        household = {
            "home": {"name": "H", "rooms": [{"name": "Kitchen", "appliances": [
                {"type": "TV", "power": 150},
            ]}]},
            "members": [_member(bedroom=None, personal=[{"type": "TV", "power": 150}])],
        }
        home = create_home_from_household(household)
        self.assertEqual(len(home.get_room("Kitchen").appliances), 1)
        self.assertEqual(len(home.members[0].personal_appliances), 0)

    def test_duplicate_personal_family_skipped(self):
        household = {
            "home": {"name": "H", "rooms": [{"name": "Bedroom 1", "appliances": []}]},
            "members": [_member(personal=[{"type": "Phone", "power": 20},
                                          {"type": "Phone", "power": 20}])],
        }
        home = create_home_from_household(household)
        self.assertEqual(len(home.members[0].personal_appliances), 1)

    def test_string_entries_and_non_dict_ignored(self):
        household = {
            "home": {"name": "H", "rooms": [{"name": "Bedroom 1", "appliances": ["Phone", {"bad": 1}]}]},
            "members": [_member(personal=["Ebike", 123, {"type": "Monitor"}])],
        }
        home = create_home_from_household(household)
        self.assertEqual(len(home.members[0].personal_appliances), 2)
        self.assertEqual(len(home.get_room("Bedroom 1").appliances), 1)


class StructureTests(unittest.TestCase):
    def test_members_and_rooms_registered(self):
        household = {
            "home": {"name": "H", "rooms": [
                {"name": "Kitchen", "appliances": [{"type": "TV", "power": 150}]},
                {"name": "Bedroom 1", "appliances": []},
            ]},
            "members": [_member()],
        }
        home = create_home_from_household(household)
        self.assertEqual(home.name, "H")
        self.assertEqual(len(home.members), 1)
        self.assertEqual(home.get_room("Kitchen").get_appliance("kitchen_tv").name, "TV")


if __name__ == "__main__":
    unittest.main()
