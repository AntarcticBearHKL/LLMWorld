import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from engine import SubAgent, utils
from engine.json_parse import parse as parse_llm_json
from engine.prompt import Prompt
from engine.subagent import LLMCallError
from appliances import get_supported_appliances_text, get_appliance_schemas_text
from appliances.catalog import backfill_power, appliance_family
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

HOUSEHOLD_SCHEMA = {
    "type": "object",
    "required": ["home", "members"],
    "properties": {
        "type": {"type": "string"},
        "season": {"type": "string"},
        "story": {"type": "string"},
        "home": {
            "type": "object",
            "required": ["name", "rooms"],
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "size": {"type": "integer"},
                "rooms": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "appliances"],
                        "properties": {
                            "name": {"type": "string"},
                            "size": {"type": "integer"},
                            "appliances": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["type", "brand", "power", "age"],
                                    "properties": {
                                        "type": {"type": "string"},
                                        "brand": {"type": "string"},
                                        "power": {"type": "integer"},
                                        "age": {"type": "integer"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        "members": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["source_persona_index", "name", "age", "cultural_background", "bedroom"],
                "properties": {
                    "source_persona_index": {"type": "integer"},
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "cultural_background": {"type": "string"},
                    "bedroom": {"type": "string"},
                    "gender": {"type": "string"},
                    "occupation": {"type": "string"},
                    "work_schedule": {"type": "object"},
                    "personality": {
                        "type": "object",
                        "properties": {
                            "energy_awareness": {"type": "string", "enum": ["Low", "Medium", "High"]},
                            "big_five": {
                                "type": "object",
                                "properties": {
                                    "openness": {"type": "number"},
                                    "conscientiousness": {"type": "number"},
                                    "extraversion": {"type": "number"},
                                    "agreeableness": {"type": "number"},
                                    "neuroticism": {"type": "number"},
                                },
                            },
                        },
                    },
                    "habits": {"type": "object"},
                    "health": {"type": "object"},
                    "personal_appliances": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["type"],
                            "properties": {
                                "type": {"type": "string"},
                                "brand": {"type": "string"},
                                "power": {"type": "number"},
                                "age": {"type": "number"},
                            },
                        },
                    },
                },
            },
        },
    },
}

HOME_SCHEMA = {
    "type": "object",
    "required": ["home"],
    "properties": {"home": HOUSEHOLD_SCHEMA["properties"]["home"]},
}


def _home_schema(member_count):
    s = {
        "type": "object",
        "required": ["home"],
        "properties": {"home": HOUSEHOLD_SCHEMA["properties"]["home"]},
    }
    s["properties"]["home"]["properties"]["rooms"]["minItems"] = member_count + 2
    return s

MEMBER_SCHEMA = {
    "type": "object",
    "required": ["member"],
    "properties": {
        "member": {
            "type": "object",
            "required": ["source_persona_index", "name", "age", "cultural_background", "bedroom",
                         "gender", "occupation", "work_schedule", "personality", "habits", "health",
                         "personal_appliances"],
            "properties": HOUSEHOLD_SCHEMA["properties"]["members"]["items"]["properties"],
        }
    },
}


def load_json(path):
    if not os.path.exists(path):
        print(f"[Error] {path} not found; run previous step first")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize_type(t):
    t = dict(t)
    if "type" not in t and "household_type" in t:
        t["type"] = t["household_type"]
    if "housing_hint" not in t:
        for k in ("typical_housing", "housing_need", "housing_type", "housing"):
            if k in t:
                t["housing_hint"] = t[k]
                break
    return t


def _normalize_appliance_entry(entry):
    if isinstance(entry, str):
        token = entry.strip()
        return {"type": token} if token else None
    if isinstance(entry, dict) and entry.get("type"):
        return entry
    return None


def _normalize_personal_appliances(members):
    for member in members:
        if not isinstance(member, dict):
            continue
        personal = member.get("personal_appliances")
        if isinstance(personal, list):
            member["personal_appliances"] = [
                norm for norm in (_normalize_appliance_entry(x) for x in personal) if norm
            ]
    return members


BIG_FIVE_DIMENSIONS = ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")

# Raw persona-CSV columns carrying the Big Five dimensions read by the analysis scripts.
PERSONA_BIG_FIVE_COLUMNS = {
    "openness": "BFI-2 Open-Mindedness",
    "conscientiousness": "BFI-2 Conscientiousness",
    "extraversion": "BFI-2 Extraversion",
    "agreeableness": "BFI-2 Agreeableness",
    "neuroticism": "BFI-2 Negative Emotionality",
}

# Persona BFI-2 cells are 5-point labels; map them to floats in [0, 1].
BFI_LEVEL_SCORES = {
    "very low": 0.1,
    "low": 0.25,
    "slightly low": 0.35,
    "average": 0.5,
    "moderate": 0.5,
    "slightly high": 0.65,
    "high": 0.8,
    "very high": 0.9,
}

# Persona "Energy level" cell -> coarse energy_awareness bucket.
ENERGY_LEVEL_AWARENESS = {
    "very low": "Low",
    "low": "Low",
    "slightly low": "Low",
    "average": "Medium",
    "moderate": "Medium",
    "fair": "Medium",
    "slightly high": "Medium",
    "high": "High",
    "very high": "High",
    "excellent": "High",
}

# Deterministic fallback for rows without BFI-2 columns: each marker hit shifts
# the 0.5 baseline by +-0.1, clamped to [0.1, 0.9]. Same portrait -> same score.
PORTRAIT_BIG_FIVE_MARKERS = {
    "openness": (
        ("curious", "creative", "imaginative", "artistic", "open-minded", "intellectual",
         "adventurous", "aesthetic", "philosophical", "exploratory"),
        ("conventional", "traditional", "routine", "practical", "predictable"),
    ),
    "conscientiousness": (
        ("organized", "organised", "disciplined", "orderly", "dutiful", "punctual",
         "planned", "structured", "thorough", "reliable"),
        ("spontaneous", "messy", "disorganized", "impulsive", "carefree", "last-minute"),
    ),
    "extraversion": (
        ("outgoing", "social", "extrovert", "talkative", "gregarious", "assertive",
         "energetic", "lively", "enthusiastic"),
        ("introvert", "quiet", "solitary", "reserved", "shy", "withdrawn", "reclusive"),
    ),
    "agreeableness": (
        ("kind", "compassionate", "cooperative", "warm", "trusting", "helpful",
         "friendly", "empathetic", "generous", "gentle"),
        ("competitive", "skeptical", "critical", "blunt", "argumentative", "selfish"),
    ),
    "neuroticism": (
        ("anxious", "worried", "stressed", "sensitive", "moody", "nervous", "tense", "insecure"),
        ("calm", "stable", "relaxed", "resilient", "composed", "even-tempered"),
    ),
}

PORTRAIT_ENERGY_MARKERS = (
    ("energetic", "high energy", "very active", "active", "vigorous", "lively"),
    ("tired", "fatigue", "exhausted", "low energy", "lethargic", "sluggish", "drained"),
)


def _marker_hits(text, markers):
    hits = 0
    for marker in markers:
        hits += len(re.findall(r"\b" + re.escape(marker) + r"\b", text))
    return hits


def _portrait_big_five(portrait):
    text = str(portrait or "").lower()
    scores = {}
    for dimension in BIG_FIVE_DIMENSIONS:
        positive, negative = PORTRAIT_BIG_FIVE_MARKERS[dimension]
        raw = 0.5 + 0.1 * (_marker_hits(text, positive) - _marker_hits(text, negative))
        scores[dimension] = round(min(0.9, max(0.1, raw)), 2)
    return scores


def _portrait_energy_awareness(portrait):
    text = str(portrait or "").lower()
    positive, negative = PORTRAIT_ENERGY_MARKERS
    high_hits = _marker_hits(text, positive)
    low_hits = _marker_hits(text, negative)
    if high_hits > low_hits:
        return "High"
    if low_hits > high_hits:
        return "Low"
    return "Medium"


def _level_to_score(value):
    if value is None:
        return None
    return BFI_LEVEL_SCORES.get(str(value).strip().lower())


def _level_to_awareness(value):
    if value is None:
        return None
    return ENERGY_LEVEL_AWARENESS.get(str(value).strip().lower())


def _apply_personality(member, row, portrait):
    """Attach energy_awareness + big_five, preferring the sampled persona row."""
    personality = member.get("personality")
    if not isinstance(personality, dict):
        personality = {}
    big_five = {}
    energy_awareness = None
    if isinstance(row, dict):
        for dimension, column in PERSONA_BIG_FIVE_COLUMNS.items():
            score = _level_to_score(row.get(column))
            if score is not None:
                big_five[dimension] = score
        energy_awareness = _level_to_awareness(row.get("Energy level"))
    if len(big_five) < len(BIG_FIVE_DIMENSIONS) or energy_awareness is None:
        fallback = _portrait_big_five(portrait)
        for dimension in BIG_FIVE_DIMENSIONS:
            big_five.setdefault(dimension, fallback[dimension])
        if energy_awareness is None:
            energy_awareness = _portrait_energy_awareness(portrait)
    personality["energy_awareness"] = energy_awareness
    personality["big_five"] = {dimension: big_five[dimension] for dimension in BIG_FIVE_DIMENSIONS}
    member["personality"] = personality
    return member


def _room_family_set(room):
    families = set()
    for appliance in room.get("appliances", []):
        if isinstance(appliance, dict) and appliance.get("type"):
            families.add(appliance_family(appliance["type"]))
    return families


def _is_protected_room(name):
    lowered = str(name or "").strip().lower()
    return "bedroom" in lowered or "living" in lowered or lowered in ("kitchen", "bathroom")


def _drop_redundant_rooms(home):
    """Drop extra shared rooms whose appliance families duplicate another room."""
    rooms = home.get("rooms")
    if not isinstance(rooms, list):
        return home
    candidates = [index for index, room in enumerate(rooms)
                  if isinstance(room, dict) and not _is_protected_room(room.get("name"))]
    removable = set()
    for index in candidates:
        families = _room_family_set(rooms[index])
        if not families:
            continue
        for other_index, other in enumerate(rooms):
            if other_index == index or not isinstance(other, dict):
                continue
            if families <= _room_family_set(other):
                removable.add(index)
                print(f"[Rooms] removed redundant {rooms[index].get('name')} "
                      f"(appliance families duplicate {other.get('name')})")
                break
    if removable:
        shared_left = False
        for index, room in enumerate(rooms):
            if index in removable or not isinstance(room, dict):
                continue
            name = str(room.get("name") or "").strip().lower()
            if "bedroom" in name or name in ("kitchen", "bathroom"):
                continue
            shared_left = True
            break
        if not shared_left:
            kept_index = candidates[0]
            removable.discard(kept_index)
            print(f"[Rooms] kept {rooms[kept_index].get('name')} as the only shared room")
    home["rooms"] = [room for index, room in enumerate(rooms) if index not in removable]
    return home


def _load_persona_rows(house_dir, htype, member_count, default_seed, aligned_texts):
    """Return (rows, seed) for the personas aligned to this house, in order.

    s2 sampled `member_count` rows with `seed`, so re-sampling with the same
    seed reproduces the same ordered rows. A previously persisted
    persona_rows.json is reused only while it still matches aligned_texts.
    """
    seed = default_seed
    prov_path = os.path.join(house_dir, "persona_provenance.json")
    if os.path.exists(prov_path):
        try:
            with open(prov_path, encoding="utf-8") as file:
                provenance = json.load(file)
            if isinstance(provenance, dict) and isinstance(provenance.get("seed"), int):
                seed = provenance["seed"]
        except (OSError, ValueError):
            pass
    rows_path = os.path.join(house_dir, "persona_rows.json")
    if os.path.exists(rows_path):
        try:
            with open(rows_path, encoding="utf-8") as file:
                cached = json.load(file)
            if (isinstance(cached, dict)
                    and cached.get("aligned_texts") == aligned_texts
                    and isinstance(cached.get("rows"), list)
                    and len(cached["rows"]) >= member_count):
                return cached["rows"][:member_count], seed
        except (OSError, ValueError):
            pass
    try:
        _, rows = gw.sample_personas(htype, seed, n=member_count)
    except Exception as exc:
        print(f"[Personality] persona re-sampling failed: {exc}")
        return [], seed
    return rows, seed


def _call_json_with_retries(label, prompt, schema, logger, prefix, shape_check=None):
    print(f"================ {label} INPUT ================")
    print(prompt)
    resp = SubAgent.single_call(prompt, json_mode=True, json_schema=schema)
    print(f"================ {label} OUTPUT ================")
    print(resp["content"])
    try:
        data = parse_llm_json(resp["content"])
    except Exception as exc:
        logger.record(label.lower().replace(" ", "_"), prompt, resp["content"], reasoning="",
                      ok=False, error=f"JSON parse failed: {exc}", attempt=1, prefix=prefix,
                      schema=schema)
        raise LLMCallError(f"{label} response is not valid JSON: {exc}") from exc
    if shape_check is not None:
        shape_ok, shape_err = shape_check(data)
        if not shape_ok:
            logger.record(label.lower().replace(" ", "_"), prompt, resp["content"], reasoning="",
                          ok=False, error=shape_err, attempt=1, prefix=prefix,
                          schema=schema)
            raise LLMCallError(f"{label} structure rejected: {shape_err}")
    logger.record(label.lower().replace(" ", "_"), prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=prefix, schema=schema, parsed=data)
    return data


def _run_decomposed(htype, aligned, logger, prefix, persona_rows=None):
    home_prompt = Prompt().load(
        "generate_world_step3_home",
        household_type=htype["type"],
        household_description=htype["description"],
        housing_hint=htype["housing_hint"],
        member_count=len(aligned),
        supported_appliances=get_supported_appliances_text(),
        appliance_schemas=get_appliance_schemas_text(),
    )
    def _home_check(d, n=len(aligned)):
        if not (isinstance(d, dict) and isinstance(d.get("home"), dict)):
            return False, "home object missing"
        rooms = d["home"].get("rooms", [])
        names = [str(r.get("name", "")) for r in rooms if isinstance(r, dict)]
        bedrooms = [x for x in names if "bedroom" in x.lower()]
        if len(bedrooms) < n:
            return False, f"only {len(bedrooms)} bedrooms for {n} members"
        return True, None

    home_data = _call_json_with_retries(
        "HOME", home_prompt, _home_schema(len(aligned)), logger, prefix,
        shape_check=_home_check,
    )
    home = home_data["home"]
    _drop_redundant_rooms(home)
    bedroom_names = [str(room.get("name", "")) for room in home.get("rooms", [])
                     if isinstance(room, dict) and "bedroom" in str(room.get("name", "")).lower()]
    if len(bedroom_names) < len(aligned):
        return False, {"stage": "step3_home", "issues": [
            f"only {len(bedroom_names)} bedrooms for {len(aligned)} members"
        ]}

    members = []
    home_summary = json.dumps(home, ensure_ascii=False, separators=(",", ":"))
    for index, portrait in enumerate(aligned, 1):
        member_prompt = Prompt().load(
            "generate_world_step3_member",
            household_type=htype["type"],
            member_index=index,
            member_count=len(aligned),
            portrait=portrait,
            assigned_bedroom=bedroom_names[index - 1],
            home_summary=home_summary,
            supported_appliances=get_supported_appliances_text(),
        )
        member_data = _call_json_with_retries(
            f"MEMBER {index}", member_prompt, MEMBER_SCHEMA, logger, prefix,
            shape_check=lambda d: (True, None) if (isinstance(d, dict) and isinstance(d.get("member"), dict))
            else (False, "member object missing"),
        )
        member = member_data["member"]
        member["name"] = f"Member {index}"
        row = persona_rows[index - 1] if isinstance(persona_rows, list) and index <= len(persona_rows) else None
        _apply_personality(member, row, portrait)
        members.append(member)

    _normalize_personal_appliances(members)

    data = {
        "type": htype["type"],
        "season": "Autumn",
        "story": f"A {htype['type'].lower()} in Clayton, assembled from ordered canonical personas.",
        "home": home,
        "members": members,
        "llm_generated": True,
    }
    return True, data


def run_step(world_id, house=0, seed=42):
    types = load_json(os.path.join(gw.WORLDS_DIR, world_id, gw.CLAYTON_POSTCODE, "household_types.json"))
    if types is None:
        return False, "household_types.json missing"
    types = types["household_types"] if isinstance(types, dict) else types
    if house >= len(types):
        print(f"[Error] house index {house} out of range (0-{len(types)-1})")
        return False, f"house {house} out of range"
    htype = normalize_type(types[house])

    house_dir = os.path.join(gw.WORLDS_DIR, world_id, gw.CLAYTON_POSTCODE, f"house_{house + 1:04d}")
    aligned = load_json(os.path.join(house_dir, "aligned_texts.json"))
    if aligned is None:
        return False, "aligned_texts.json missing (run s2 first)"

    log_dir = os.path.join(house_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    prefix = f"house_{house + 1:04d}_"

    print(f"[House {house}] {htype.get('type')} | members {len(aligned)}")
    persona_rows, persona_seed = _load_persona_rows(house_dir, htype, len(aligned), seed, aligned)
    if persona_rows:
        print(f"[Personality] {len(persona_rows)} persona rows loaded (seed={persona_seed})")
    else:
        print("[Personality] persona rows unavailable; deriving from portraits only")
    ok, result = _run_decomposed(htype, aligned, logger, prefix, persona_rows)
    if not ok:
        print(f"[Error] decomposed household generation failed: {result}")
        return False, result
    data = result
    filled_room = 0
    for room in data.get("home", {}).get("rooms", []):
        if not isinstance(room, dict):
            continue
        appliances = room.get("appliances")
        if not isinstance(appliances, list):
            continue
        for i, cfg in enumerate(appliances):
            if isinstance(cfg, dict):
                appliances[i] = backfill_power(cfg, location=room.get("name"))
                filled_room += 1
    filled_personal = 0
    for member in data.get("members", []):
        if not isinstance(member, dict):
            continue
        personal = member.get("personal_appliances")
        if not isinstance(personal, list):
            continue
        for i, cfg in enumerate(personal):
            if isinstance(cfg, dict):
                personal[i] = backfill_power(cfg, location=None)
                filled_personal += 1
    print(f"[Appliances] power backfilled for {filled_room} room + {filled_personal} personal configs")
    out_path = os.path.join(house_dir, "household.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
    if persona_rows:
        rows_path = os.path.join(house_dir, "persona_rows.json")
        with open(rows_path, "w", encoding="utf-8") as f:
            json.dump({"seed": persona_seed, "aligned_texts": aligned, "rows": persona_rows},
                      f, ensure_ascii=False, indent=2)
        print(f"[Saved] {rows_path}")
    print(f"[Overview] rooms: {len(data.get('home', {}).get('rooms', []))} | members: {len(data.get('members', []))}")
    for m in data.get("members", []):
        print(f"  - P{m.get('source_persona_index')} {m.get('name')} -> {m.get('bedroom')}")
    return True, data


def main():
    parser = argparse.ArgumentParser(description="World step 3: household build (per house)")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--house", type=int, default=0, help="household index (0-based)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    ok, result = run_step(args.world, args.house, args.seed)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
