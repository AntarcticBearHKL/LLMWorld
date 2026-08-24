import json
import os
import random
from datetime import datetime

CLAYTON_POSTCODE = "3168"
CLAYTON_CITY = "Melbourne"
CLAYTON_DISTRICT = "Clayton"


FIRST_NAMES_M = ["David", "Jack", "Lucas", "Ethan", "James", "Daniel", "Ryan", "Ben",
                 "Arjun", "Rohan", "Minh", "Tuan", "Liam", "Noah", "William"]
FIRST_NAMES_F = ["Alice", "Sophia", "Emma", "Olivia", "Chloe", "Grace", "Mia", "Lily",
                 "Priya", "Ananya", "Linh", "Hana", "Ava", "Ella", "Zoe"]
SURNAMES = ["Chen", "Wang", "Li", "Zhang", "Smith", "Nguyen", "Patel", "Brown",
            "Tran", "Singh", "Kumar", "Wilson", "Gao", "Liu", "Taylor", "Pham"]
KID_NAMES = ["Liam", "Noah", "Emma", "Olivia", "Ava", "Mia", "Ethan", "Lucas",
             "Arjun", "Minh", "Hana", "Zoe"]



OCCUPATIONS_PROFESSIONAL = ["Software Engineer", "Data Analyst", "Accountant", "Lawyer", "Doctor",
                            "University Professor", "Bank Manager", "Architect", "Pharmacist"]
OCCUPATIONS_MIDDLE = ["Nurse", "Teacher", "Sales Manager", "Electrician", "Chef", "Mechanic",
                      "Supermarket Supervisor", "Construction Supervisor", "Driver",
                      "Administrative Assistant"]
OCCUPATIONS_SERVICE = ["Supermarket Cashier", "Cleaner", "Waiter", "Warehouse Worker",
                       "Courier", "Gardener"]
STUDENT_LEVELS = ["Master's Student", "PhD Student", "Undergraduate Student"]

INCOME_BY_OCCUPATION = {
    "High": OCCUPATIONS_PROFESSIONAL,
    "Medium": OCCUPATIONS_MIDDLE,
    "Low": OCCUPATIONS_SERVICE,
}



BIG_FIVE_ZH = {
    "openness": "Openness",
    "conscientiousness": "Conscientiousness",
    "extraversion": "Extraversion",
    "agreeableness": "Agreeableness",
    "neuroticism": "Neuroticism",
}

BIG_FIVE_TEXT = {
    "openness": {
        "high": "Curious and enjoys trying new things",
        "low": "Prefers familiar routines and rarely tries new things",
    },
    "conscientiousness": {
        "high": "Organized, keeps a regular routine, detail-oriented",
        "low": "Easygoing, with a relaxed daily rhythm",
    },
    "extraversion": {
        "high": "Enjoys social gatherings and often goes out",
        "low": "Quiet and reserved, spends more time at home",
    },
    "agreeableness": {
        "high": "Values neighborly relationships and is open to others' advice",
        "low": "Independent and headstrong, not easily influenced",
    },
    "neuroticism": {
        "high": "Anxious, sensitive to price fluctuations and news events",
        "low": "Emotionally stable and unflappable",
    },
}

TRAITS_BY_LEVEL = {
    "openness": {"high": "Curious", "low": "Traditional"},
    "conscientiousness": {"high": "Organized", "low": "Easygoing"},
    "extraversion": {"high": "Outgoing", "low": "Quiet"},
    "agreeableness": {"high": "Agreeable", "low": "Stubborn"},
    "neuroticism": {"high": "Sensitive", "low": "Composed"},
}


def sample_big_five(rng, bias=None):

    bias = bias or {}
    scores = {}
    for dim in BIG_FIVE_ZH:
        b = bias.get(dim, 0)
        scores[dim] = max(1, min(10, rng.randint(1, 10) + b))
    return scores


def big_five_to_text(bf):

    parts = []
    for dim, zh in BIG_FIVE_ZH.items():
        v = bf[dim]
        level = "high" if v >= 7 else ("low" if v <= 4 else None)
        if level:
            parts.append(f"{zh} {'High' if level == 'high' else 'Low'}: {BIG_FIVE_TEXT[dim][level]}")
    return "; ".join(parts) if parts else "Balanced personality, no strong tendency"


def big_five_to_traits(bf, rng):

    traits = []
    for dim in BIG_FIVE_ZH:
        v = bf[dim]
        if v >= 7:
            traits.append(TRAITS_BY_LEVEL[dim]["high"])
        elif v <= 4:
            traits.append(TRAITS_BY_LEVEL[dim]["low"])
    rng.shuffle(traits)
    return traits[:3] if traits else ["Easygoing"]


def big_five_to_news_sensitivity(bf):

    n = bf["neuroticism"]
    if n >= 7:
        return "High"
    if n >= 4:
        return "Medium"
    return "Low"





def _make_member(rng, name, gender, age, occupation, income_bracket,
                 big_five=None, wake=None, sleep=None, personal=None, role="member"):

    bf = big_five or sample_big_five(rng)
    traits = big_five_to_traits(bf, rng)


    if wake is None:
        if occupation == "Retired":
            wake = rng.choice(["06:30", "07:00", "07:30"])
        elif occupation in ("Undergraduate Student", "Master's Student", "PhD Student"):
            wake = rng.choice(["08:30", "09:00", "09:30"])
        else:
            wake = rng.choice(["06:45", "07:00", "07:15", "07:30"])
        if bf["extraversion"] >= 7 and occupation != "Retired":
            wake = rng.choice(["06:45", "07:00"])
        elif bf["conscientiousness"] >= 7:
            wake = rng.choice(["06:30", "06:45"])
    if sleep is None:
        sleep = rng.choice(["22:30", "23:00", "23:30", "00:00"])
        if occupation in ("Undergraduate Student", "Master's Student", "PhD Student"):
            sleep = rng.choice(["00:00", "00:30", "01:00"])
        elif bf["conscientiousness"] >= 7:
            sleep = rng.choice(["22:00", "22:30"])

    hobbies_pool = {
        "High": ["Reading", "Gardening", "Baking", "Hiking", "Photography", "Cooking"],
        "Medium": ["Movies", "Running", "Fishing", "Gaming", "Fitness"],
        "Low": ["Scrolling phone", "Gaming", "Watching livestreams"],
    }
    hobbies = rng.sample(hobbies_pool.get(income_bracket, hobbies_pool["Medium"]), 2)

    return {
        "name": name, "age": age, "gender": gender, "occupation": occupation,
        "work_schedule": {"start": "09:00", "end": "17:00", "remote": rng.random() < 0.25,
                          "work_days": [1, 2, 3, 4, 5]},
        "personality": {
            "traits": traits,
            "big_five": bf,
            "behavior_text": big_five_to_text(bf),
            "news_sensitivity": big_five_to_news_sensitivity(bf),
        },
        "habits": {"wake_time": wake, "sleep_time": sleep,
                   "exercise": rng.choice(["Weekly running", "Occasional walks", "Gym", "None"]),
                   "hobbies": hobbies},
        "health": {"condition": "Good",
                   "temperature_preference": {"summer": rng.choice([24, 25, 26]),
                                              "winter": rng.choice([21, 22, 23])}},
        "personal_appliances": [{"type": t, "brand": "Generic", "power": None, "age": 0}
                                for t in (personal or ["Phone", "Computer"])],
    }


def _pick_occupation(rng, income_bracket):
    return rng.choice(INCOME_BY_OCCUPATION[income_bracket])


def _income_by_age(rng, age):

    if age >= 65:
        return "Low"
    if age < 25:
        return rng.choice(["Low", "Medium"])
    r = rng.random()
    if r < 0.3:
        return "High"
    if r < 0.75:
        return "Medium"
    return "Low"




def _home_by_income(rng, name, income_bracket, size_override=None):




    sizes = {"High": rng.choice([120, 135, 150, 180]),
             "Medium": rng.choice([85, 95, 105, 115]),
             "Low": rng.choice([55, 65, 75])}
    size = size_override or sizes[income_bracket]

    rooms = {}


    living = ["TV", "Light"]
    if income_bracket != "Low":
        living.append("AirConditioner")
    rooms["Living Room"] = living


    kitchen = ["Refrigerator", "Light"]
    if income_bracket in ("Medium", "High"):
        kitchen += ["RiceCooker", "Microwave"]
    if income_bracket == "High":
        kitchen += ["InductionCooker", "RangeHood"]
    else:
        kitchen += ["InductionCooker"]
    rooms["Kitchen"] = kitchen


    rooms["Bathroom"] = ["WaterHeater", "WashingMachine", "Light"]


    n_bedrooms = 1 if size <= 65 else (2 if size <= 105 else 3)
    for i in range(n_bedrooms):
        bed = ["Light", "DeskLamp"]
        if income_bracket == "High" or (income_bracket == "Medium" and i == 0):
            bed.append("AirConditioner")
        rooms[f"Bedroom {i + 1}"] = bed

    home = {"name": name, "type": "Townhouse" if size <= 115 else "Detached House",
            "size": size, "rooms": []}
    for room_name, appliance_types in rooms.items():
        home["rooms"].append({
            "name": room_name, "size": 0,
            "appliances": [{"type": t, "brand": "Generic", "power": None, "age": 0}
                           for t in appliance_types],
        })
    return home




def _build_template(household_type, rng):

    surname = rng.choice(SURNAMES)
    income = rng.choice(["Low", "Medium", "Medium", "High"])

    if household_type == "young_couple":
        age_w = rng.randint(26, 33)
        age_m = age_w + rng.randint(0, 4)
        bf_w = sample_big_five(rng, bias={"conscientiousness": rng.choice([0, 1, 2]),
                                          "openness": rng.choice([0, 1, 1])})
        bf_m = sample_big_five(rng, bias={"conscientiousness": rng.choice([0, 0, -1])})
        return {
            "type": "Young Couple (DINK)", "season": "Spring",
            "home": _home_by_income(rng, "Clayton Cozy Townhouse", income),
            "members": [
                _make_member(rng, f"{rng.choice(FIRST_NAMES_F)} {surname}", "Female", age_w,
                             _pick_occupation(rng, income), income, big_five=bf_w,
                             personal=["Phone", "Computer", "DeskLamp"]),
                _make_member(rng, f"{rng.choice(FIRST_NAMES_M)} {surname}", "Male", age_m,
                             _pick_occupation(rng, income), income, big_five=bf_m),
            ],
        }

    if household_type == "family_with_kids":
        age_m = rng.randint(32, 42)
        age_w = age_m + rng.randint(-3, 3)
        kid_age = age_m - rng.randint(24, 34)
        kid_age = max(4, kid_age)
        bf_parents = sample_big_five(rng, bias={"conscientiousness": 2, "agreeableness": 1})
        bf_kid = sample_big_five(rng, bias={"extraversion": 2})
        home = _home_by_income(rng, "Clayton Family Home", "High" if rng.random() < 0.6 else "Medium")
        home["rooms"].append({"name": "Kids' Room", "size": 0,
                              "appliances": [{"type": "Light", "brand": "Generic", "power": None, "age": 0},
                                             {"type": "DeskLamp", "brand": "Generic", "power": None, "age": 0}]})
        return {
            "type": "Family with Children", "season": "Spring", "home": home,
            "members": [
                _make_member(rng, f"{rng.choice(FIRST_NAMES_F)} {surname}", "Female", age_w,
                             _pick_occupation(rng, "High" if income == "High" else "Medium"),
                             "High" if income == "High" else "Medium", big_five=bf_parents,
                             personal=["Phone", "Computer"]),
                _make_member(rng, f"{rng.choice(FIRST_NAMES_M)} {surname}", "Male", age_m,
                             _pick_occupation(rng, "High" if income == "High" else "Medium"),
                             "High" if income == "High" else "Medium", big_five=bf_parents),
                _make_member(rng, f"{rng.choice(KID_NAMES)} {surname}", rng.choice(["Male", "Female"]),
                             kid_age, "Primary School Student", "Low", big_five=bf_kid,
                             wake="07:00", sleep="21:00", personal=["Phone"]),
            ],
        }

    if household_type == "single_living":
        age = rng.randint(22, 30) if rng.random() < 0.6 else rng.randint(62, 78)
        occ = _pick_occupation(rng, _income_by_age(rng, age)) if age < 60 else "Retired"
        return {
            "type": "Living Alone", "season": "Spring",
            "home": _home_by_income(rng, "Clayton One-Bedroom Unit", _income_by_age(rng, age)),
            "members": [_make_member(rng, f"{rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {surname}",
                                     rng.choice(["Male", "Female"]), age, occ,
                                     "Low" if age >= 60 else "Medium")],
        }

    if household_type == "share_house":
        members = []
        for i in range(3):
            age = rng.randint(20, 29)
            bf = sample_big_five(rng, bias={"extraversion": 1, "conscientiousness": -1})
            members.append(_make_member(
                rng, f"{rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {rng.choice(SURNAMES)}",
                rng.choice(["Male", "Female"]), age, _pick_occupation(rng, "Medium"), "Medium",
                big_five=bf, wake=rng.choice(["08:30", "09:00"]),
                sleep=rng.choice(["00:00", "00:30", "01:00"])))
        return {
            "type": "Share House", "season": "Spring",
            "home": _home_by_income(rng, "Clayton Share House", "Medium"),
            "members": members,
        }

    if household_type == "international_student":

        members = []
        for i in range(rng.choice([2, 3])):
            age = rng.randint(19, 27)
            country = rng.choice(["China", "India", "Vietnam", "Malaysia", "Indonesia"])
            bf = sample_big_five(rng, bias={"openness": 2, "conscientiousness": 1})
            members.append(_make_member(
                rng, f"{rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {rng.choice(SURNAMES)}",
                rng.choice(["Male", "Female"]), age, rng.choice(STUDENT_LEVELS), "Low",
                big_five=bf, wake=rng.choice(["09:00", "09:30", "10:00"]),
                sleep=rng.choice(["00:30", "01:00", "01:30"]),
                personal=["Phone", "Computer", "DeskLamp"]))
        return {
            "type": "International Student Share House", "season": "Spring",
            "home": _home_by_income(rng, "Clayton Student Apartment", "Low"),
            "members": members,
        }

    if household_type == "multigenerational":

        grandpa = rng.randint(62, 76)
        grandma = grandpa + rng.randint(-3, 2)
        parent_age = grandpa - rng.randint(24, 32)
        kid_age = parent_age - rng.randint(24, 34)
        kid_age = max(5, kid_age)
        return {
            "type": "Multigenerational Household", "season": "Spring",
            "home": _home_by_income(rng, "Clayton Multigenerational Home", "Medium",
                                    size_override=rng.choice([120, 140])),
            "members": [
                _make_member(rng, f"{rng.choice(FIRST_NAMES_M)} {surname}", "Male", grandpa,
                             "Retired", "Low", wake="06:30", sleep="21:30",
                             personal=["Phone"]),
                _make_member(rng, f"{rng.choice(FIRST_NAMES_F)} {surname}", "Female", grandma,
                             "Retired", "Low", wake="06:30", sleep="21:30",
                             personal=["Phone"]),
                _make_member(rng, f"{rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {surname}",
                             rng.choice(["Male", "Female"]), parent_age,
                             _pick_occupation(rng, "Medium"), "Medium"),
                _make_member(rng, f"{rng.choice(KID_NAMES)} {surname}", rng.choice(["Male", "Female"]),
                             kid_age, "Primary School Student", "Low", wake="07:00", sleep="21:00",
                             personal=["Phone"]),
            ],
        }

    if household_type == "single_parent":
        age = rng.randint(29, 45)
        kid_age = age - rng.randint(22, 32)
        kid_age = max(4, kid_age)
        bf = sample_big_five(rng, bias={"conscientiousness": 1})
        return {
            "type": "Single-Parent Family", "season": "Spring",
            "home": _home_by_income(rng, "Clayton Single-Parent Home", "Medium"),
            "members": [
                _make_member(rng, f"{rng.choice(FIRST_NAMES_F + FIRST_NAMES_M)} {surname}",
                             rng.choice(["Female", "Male"]), age, _pick_occupation(rng, "Medium"),
                             "Medium", big_five=bf, personal=["Phone", "Computer"]),
                _make_member(rng, f"{rng.choice(KID_NAMES)} {surname}", rng.choice(["Male", "Female"]),
                             kid_age, "Primary School Student", "Low", wake="07:00", sleep="21:00",
                             personal=["Phone"]),
            ],
        }


    age_m = rng.randint(66, 80)
    age_w = age_m + rng.randint(-3, 3)
    return {
        "type": "Retired Couple", "season": "Spring",
        "home": _home_by_income(rng, "Clayton Retirement Home", "Low",
                                size_override=rng.choice([65, 75, 85])),
        "members": [
            _make_member(rng, f"{rng.choice(FIRST_NAMES_M)} {surname}", "Male", age_m, "Retired",
                         "Low", wake="06:30", sleep="21:00", personal=["Phone"]),
            _make_member(rng, f"{rng.choice(FIRST_NAMES_F)} {surname}", "Female", age_w, "Retired",
                         "Low", wake="06:30", sleep="21:00", personal=["Phone"]),
        ],
    }




HOUSEHOLD_QUOTAS = [
    ("young_couple", 25),
    ("family_with_kids", 20),
    ("share_house", 15),
    ("single_living", 15),
    ("international_student", 10),
    ("multigenerational", 5),
    ("single_parent", 5),
    ("retired_couple", 5),
]


def _quota_distribution(count, rng):




    n_types = len(HOUSEHOLD_QUOTAS)
    counts = {t: 0 for t, _ in HOUSEHOLD_QUOTAS}
    if count >= n_types:
        for t, _ in HOUSEHOLD_QUOTAS:
            counts[t] = 1
    remaining = count - sum(counts.values())
    if remaining > 0:
        wheel = [t for t, w in HOUSEHOLD_QUOTAS for _ in range(w)]
        rng.shuffle(wheel)
        for t in wheel[:remaining]:
            counts[t] += 1
    return counts




def _dedupe_names(household):

    seen = set()
    for m in household["members"]:
        name = m["name"]
        if name in seen:
            i = 2
            while f"{name} {i}" in seen:
                i += 1
            m["name"] = f"{name} {i}"
        seen.add(m["name"])


def build_population(world_id, count, seed=42, household_types=None):




    if count > 10:
        raise ValueError(f"At most 10 households per world (received {count}). "
                         f"Please split into multiple worlds.")

    rng = random.Random(seed)

    if household_types is None:
        type_counts = _quota_distribution(count, rng)
        household_types = [t for t, n in type_counts.items() for _ in range(n)]
        rng.shuffle(household_types)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    world_dir = os.path.join(project_root, "worlds", world_id)
    district_dir = os.path.join(world_dir, CLAYTON_POSTCODE)
    os.makedirs(district_dir, exist_ok=True)

    households_meta = []
    for i in range(count):
        htype = household_types[i % len(household_types)]
        household = _build_template(htype, rng)
        _dedupe_names(household)

        house_id = f"house_{i + 1:04d}"
        house_dir = os.path.join(district_dir, house_id)
        os.makedirs(house_dir, exist_ok=True)

        with open(os.path.join(house_dir, "household.json"), "w", encoding="utf-8") as f:
            json.dump(household, f, ensure_ascii=False, indent=2)

        households_meta.append({
            "house_id": house_id,
            "type": household["type"],
            "members_count": len(household["members"]),
            "rooms_count": len(household["home"]["rooms"]),
        })
        print(f"  Generated {house_id}: {household['type']} "
              f"({len(household['members'])} members/{len(household['home']['rooms'])} rooms)")

    district = {
        "postcode": CLAYTON_POSTCODE,
        "location": {"city": CLAYTON_CITY, "district": CLAYTON_DISTRICT,
                     "coordinates": {"lat": -37.916, "lon": 145.123}},
        "economic_level": "Medium",
    }
    with open(os.path.join(district_dir, "district.json"), "w", encoding="utf-8") as f:
        json.dump(district, f, ensure_ascii=False, indent=2)

    world_meta = {
        "world_id": world_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_prompt": (f"Population builder v2 (seed={seed}, Big Five personality + "
                        f"8 household types + census calibration)"),
        "generator": "population.py v2",
        "district": {
            "postcode": CLAYTON_POSTCODE,
            "city": CLAYTON_CITY,
            "district": CLAYTON_DISTRICT,
            "economic_level": "Medium",
        },
        "households": households_meta,
    }
    with open(os.path.join(world_dir, "world.json"), "w", encoding="utf-8") as f:
        json.dump(world_meta, f, ensure_ascii=False, indent=2)

    return world_meta
