import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from engine import SubAgent, utils
from engine.prompt import Prompt
from engine.subagent import LLMCallError
from appliances import get_supported_appliances_text, get_appliance_schemas_text
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
                    "personality": {"type": "object"},
                    "habits": {"type": "object"},
                    "health": {"type": "object"},
                    "personal_appliances": {"type": "array"},
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


def _call_json_with_retries(label, prompt, schema, logger, prefix, shape_check=None):
    print(f"================ {label} INPUT ================")
    print(prompt)
    resp = SubAgent.single_call(prompt, json_mode=True, json_schema=schema)
    print(f"================ {label} OUTPUT ================")
    print(resp["content"])
    try:
        data = utils.parse_json_response(resp["content"])
    except Exception as exc:
        logger.record(label.lower().replace(" ", "_"), prompt, resp["content"], reasoning="",
                      ok=False, error=f"JSON parse failed: {exc}", attempt=1, prefix=prefix)
        raise LLMCallError(f"{label} response is not valid JSON: {exc}") from exc
    if shape_check is not None:
        shape_ok, shape_err = shape_check(data)
        if not shape_ok:
            logger.record(label.lower().replace(" ", "_"), prompt, resp["content"], reasoning="",
                          ok=False, error=shape_err, attempt=1, prefix=prefix)
            raise LLMCallError(f"{label} structure rejected: {shape_err}")
    logger.record(label.lower().replace(" ", "_"), prompt, resp["content"], reasoning="",
                  ok=True, attempt=1, prefix=prefix)
    return data


def _run_decomposed(htype, aligned, logger, prefix):
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
        "HOME", home_prompt, HOME_SCHEMA, logger, prefix,
        shape_check=_home_check,
    )
    home = home_data["home"]
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
        members.append(member)

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
    ok, result = _run_decomposed(htype, aligned, logger, prefix)
    if not ok:
        print(f"[Error] decomposed household generation failed: {result}")
        return False, result
    data = result
    out_path = os.path.join(house_dir, "household.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Saved] {out_path}")
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
