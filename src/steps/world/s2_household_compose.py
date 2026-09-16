"""World step: compose one household for a district and align its members.

For a district (default: the world's primary district) this step runs two
sub-operations:

(a) composition - ``generate_world_household.md`` receives the district
    description and returns the household that should live here next: a type
    name, a member count and a one-line rationale.
(b) members - the decided member count drives ``gw.sample_personas`` against the
    local persona bank; the sampled personas plus the household type are handed
    to the existing ``generate_world_step2_align.md`` prompt, which rewrites only
    the parts that do not fit the district/household and returns one aligned
    portrait per member. Those portraits become the household's members.

Outputs ``<district>/house_XXXX/household.json`` (household type plus members;
this step never writes ``home``), plus ``aligned_texts.json`` and
``persona_provenance.json`` with the same shapes ``s2_persona_align`` writes,
and registers the household via ``gw.update_world_meta``.

Additive: the s1-s4 world steps and ``run.py`` are untouched; a later task
switches the pipeline over.

Run:
  .venv\\Scripts\\python.exe src\\steps\\world\\s2_household_compose.py --world <id>
  .venv\\Scripts\\python.exe src\\steps\\world\\s2_household_compose.py --world <id> --house 0
  .venv\\Scripts\\python.exe src\\steps\\world\\s2_household_compose.py --world <id> --all
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from engine import SubAgent
from engine.json_parse import parse as parse_llm_json
from engine.subagent import LLMCallError
from engine.prompt import Prompt
from steps.world.s3_household_build import _apply_personality, _normalize_personal_appliances
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

MIN_MEMBERS = 1
MAX_MEMBERS = 8
DEFAULT_MEMBER_AGE = 30
DEFAULT_GENDER = "Unknown"

# DeepSeek does not enforce json_schema, so the aligned member count is validated
# here and retried / replaced with the canonical personas on mismatch.
MAX_MEMBER_ATTEMPTS = 3

COMPOSE_STAGE = "household_compose"
MEMBERS_STAGE = "household_members"

_HOUSE_ID_RE = re.compile(r"^house_(\d{4})$")


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError):
        return None


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def _household_schema():
    return {
        "type": "object",
        "required": ["household_type", "member_count", "rationale"],
        "properties": {
            "household_type": {"type": "string"},
            "member_count": {"type": "integer", "minimum": MIN_MEMBERS, "maximum": MAX_MEMBERS},
            "rationale": {"type": "string"},
        },
    }


def _members_schema(member_count):
    return {
        "type": "object",
        "required": ["members"],
        "properties": {
            "members": {
                "type": "array",
                "minItems": member_count,
                "maxItems": member_count,
                "items": {
                    "type": "object",
                    "required": ["portrait", "age", "gender"],
                    "properties": {
                        "portrait": {"type": "string"},
                        "age": {"type": "integer"},
                        "gender": {"type": "string"},
                    },
                },
            }
        },
    }


def _district_description(world_id, district):
    """The district description text, or "" when absent."""
    data = _read_json(os.path.join(gw.district_dir(world_id, district), "district.json"))
    if isinstance(data, dict):
        description = data.get("description")
        if isinstance(description, str):
            return description.strip()
    return ""


def _house_ids(district_path):
    try:
        children = os.listdir(district_path)
    except OSError:
        return []
    return sorted(name for name in children if _HOUSE_ID_RE.match(name))


def _existing_households(district_path, exclude=None):
    """[(house_id, household_dict)] for houses that already hold a household.json."""
    found = []
    for house_id in _house_ids(district_path):
        if house_id == exclude:
            continue
        data = _read_json(os.path.join(district_path, house_id, "household.json"))
        if isinstance(data, dict):
            found.append((house_id, data))
    return found


def _next_house_id(district_path):
    highest = 0
    for house_id in _house_ids(district_path):
        highest = max(highest, int(_HOUSE_ID_RE.match(house_id).group(1)))
    return "house_%04d" % (highest + 1)


def _resolve_house_id(district_path, house):
    """Resolve the house selector to a ``house_XXXX`` id.

    ``None`` selects the next free house in the district (append a new
    household); an int is a 0-based index and a ``house_XXXX`` string selects an
    existing household to overwrite.
    """
    if house is None:
        return _next_house_id(district_path)
    if isinstance(house, bool):
        raise ValueError("invalid house selector %r" % (house,))
    if isinstance(house, int):
        if house < 0:
            raise ValueError("house index must be >= 0; got %d" % house)
        return "house_%04d" % (house + 1)
    token = str(house).strip()
    if not token:
        return _next_house_id(district_path)
    if token.isdigit():
        return "house_%04d" % (int(token) + 1)
    if _HOUSE_ID_RE.match(token):
        return token
    raise ValueError("invalid house selector %r; use an index or house_XXXX" % (house,))


def _existing_types_text(existing):
    types = []
    for _, household in existing:
        household_type = household.get("type")
        if isinstance(household_type, str) and household_type.strip():
            types.append(household_type.strip())
    return ", ".join(types) if types else "none"


def _plan_problem(data):
    if not isinstance(data, dict):
        return "response is not a JSON object"
    household_type = data.get("household_type")
    if not isinstance(household_type, str) or not household_type.strip():
        return "response lacks a non-empty household_type"
    member_count = data.get("member_count")
    if isinstance(member_count, bool) or not isinstance(member_count, int):
        return "member_count must be an integer"
    if not (MIN_MEMBERS <= member_count <= MAX_MEMBERS):
        return "member_count %d is outside %d..%d" % (member_count, MIN_MEMBERS, MAX_MEMBERS)
    rationale = data.get("rationale")
    if rationale is not None and not isinstance(rationale, str):
        return "rationale must be a string"
    return None


def _coerce_age(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        age = value
    elif isinstance(value, str) and value.strip().isdigit():
        age = int(value.strip())
    else:
        return None
    return age if 1 <= age <= 120 else None


def _coerce_gender(value):
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _normalize_member_items(data, member_count):
    """Return (items, problem); items are {portrait, age, gender} dicts."""
    members = data.get("members") if isinstance(data, dict) else data
    if not isinstance(members, list) or not members:
        return [], "response lacks a members list"
    if len(members) != member_count:
        return [], "returned %d members, expected exactly %d" % (len(members), member_count)
    items = []
    seen = set()
    for member in members:
        if not isinstance(member, dict):
            return [], "a member entry is not an object"
        portrait = member.get("portrait")
        if not isinstance(portrait, str) or not portrait.strip():
            return [], "a member entry has an empty portrait"
        portrait = portrait.strip()
        if portrait in seen:
            return [], "returned duplicate portraits"
        seen.add(portrait)
        items.append({
            "portrait": portrait,
            "age": _coerce_age(member.get("age")),
            "gender": _coerce_gender(member.get("gender")),
        })
    return items, None


def _fallback_items(fallback_texts, member_count):
    items = []
    seen = set()
    for text in fallback_texts or []:
        if not isinstance(text, str):
            continue
        text = text.strip()
        if not text or text in seen:
            continue
        items.append({"portrait": text, "age": None, "gender": ""})
        seen.add(text)
        if len(items) >= member_count:
            break
    return items


def _call_compose(prompt, logger, prefix):
    schema = _household_schema()
    print("================ COMPOSE INPUT ================")
    print(prompt)
    resp = SubAgent.single_call(prompt, json_mode=True, json_schema=schema)
    print("================ COMPOSE OUTPUT ================")
    print(resp["content"])
    try:
        data = parse_llm_json(resp["content"])
    except Exception as exc:
        logger.record(COMPOSE_STAGE, prompt, resp["content"], reasoning="", ok=False,
                      error="JSON parse failed: %s" % exc, attempt=1, prefix=prefix, schema=schema)
        raise LLMCallError("compose response is not valid JSON: %s" % exc) from exc
    problem = _plan_problem(data)
    if problem is not None:
        logger.record(COMPOSE_STAGE, prompt, resp["content"], reasoning="", ok=False,
                      error=problem, attempt=1, prefix=prefix, schema=schema)
        raise LLMCallError("compose structure rejected: %s" % problem)
    plan = {
        "household_type": data["household_type"].strip(),
        "member_count": int(data["member_count"]),
        "rationale": (data.get("rationale") or "").strip(),
    }
    logger.record(COMPOSE_STAGE, prompt, resp["content"], reasoning="", ok=True,
                  attempt=1, prefix=prefix, schema=schema, parsed=data)
    return plan


def _call_members(prompt, logger, prefix, member_count, fallback_texts=None):
    """Call the existing align prompt and return ([{portrait, age, gender}], source)."""
    schema = _members_schema(member_count)
    last_error = None
    last_content = ""
    current = prompt
    for attempt in range(1, MAX_MEMBER_ATTEMPTS + 1):
        print("================ MEMBERS INPUT ================")
        print(current)
        resp = SubAgent.single_call(current, json_mode=True, json_schema=schema)
        print("================ MEMBERS OUTPUT ================")
        print(resp["content"])
        last_content = resp["content"]
        try:
            data = parse_llm_json(resp["content"])
        except Exception as exc:
            logger.record(MEMBERS_STAGE, current, resp["content"], reasoning="", ok=False,
                          error="JSON parse failed: %s" % exc, attempt=attempt,
                          prefix=prefix, schema=schema)
            raise LLMCallError("members response is not valid JSON: %s" % exc) from exc
        items, problem = _normalize_member_items(data, member_count)
        if problem is None:
            logger.record(MEMBERS_STAGE, current, resp["content"], reasoning="", ok=True,
                          attempt=attempt, prefix=prefix, schema=schema, parsed=data)
            return items, "llm"
        last_error = problem
        logger.record(MEMBERS_STAGE, current, resp["content"], reasoning="", ok=False,
                      error=problem, attempt=attempt, prefix=prefix, schema=schema)
        if attempt >= MAX_MEMBER_ATTEMPTS:
            break
        current = prompt + (
            "\n\n## Correction\n"
            "You returned %d portraits but EXACTLY %d are required. "
            "Return exactly %d distinct English third-person portraits in the same order, "
            "one per person, each with an integer age and a gender."
            % (len(data.get("members", []) if isinstance(data, dict) else []), member_count, member_count)
        )
    fallback = _fallback_items(fallback_texts, member_count)
    if len(fallback) < member_count:
        raise LLMCallError("member count mismatch after %d attempts: %s" % (MAX_MEMBER_ATTEMPTS, last_error))
    print("[Fallback] aligned member count failed after %d attempts (%s); "
          "using %d canonical personas" % (MAX_MEMBER_ATTEMPTS, last_error, len(fallback)))
    logger.record(MEMBERS_STAGE + "_fallback", prompt, last_content, reasoning="", ok=False,
                  error="count mismatch after %d attempts: %s" % (MAX_MEMBER_ATTEMPTS, last_error),
                  attempt=MAX_MEMBER_ATTEMPTS, prefix=prefix, schema=schema)
    return fallback, "fallback"


def _build_member(index, item, row):
    age = item.get("age")
    if not isinstance(age, int) or isinstance(age, bool) or not (1 <= age <= 120):
        age = DEFAULT_MEMBER_AGE
    member = {
        "source_persona_index": index,
        "name": "Member %d" % index,
        "age": age,
        "gender": item.get("gender") or DEFAULT_GENDER,
        "cultural_background": "",
        "bedroom": "Bedroom %d" % index,
        "occupation": "",
        "work_schedule": {},
        "personality": {},
        "habits": {},
        "health": {},
        "personal_appliances": [],
    }
    _apply_personality(member, row, item.get("portrait", ""))
    return member


def _upsert_household_meta(world_id, house_meta, district):
    """Replace any existing entry for this house, then register the fresh one."""
    path = os.path.join(gw.district_dir(world_id, district), "households.json")
    data = _read_json(path)
    if not isinstance(data, dict):
        data = {}
    entries = data.get("households")
    if not isinstance(entries, list):
        entries = []
    house_id = str(house_meta.get("house_id"))
    data["households"] = [
        entry for entry in entries
        if not (isinstance(entry, dict) and str(entry.get("house_id")) == house_id)
    ]
    _write_json(path, data)
    return gw.update_world_meta(world_id, house_meta, district)


def run_step(world_id, district=None, house=None, *, seed=42) -> tuple[bool, str]:
    """Compose one household for a district and persist its aligned members.

    ``house=None`` appends a new ``house_XXXX``; an int (0-based) or a
    ``house_XXXX`` string overwrites an existing household. Returns
    ``(True, house_dir)`` on success and ``(False, error)`` otherwise.
    """
    district = district or gw.primary_district(world_id)
    if not district:
        return False, "no districts in world %s" % world_id

    description = _district_description(world_id, district)
    if not description:
        return False, "district description missing; run the district-description step first"

    district_path = gw.district_dir(world_id, district)
    try:
        house_id = _resolve_house_id(district_path, house)
    except ValueError as exc:
        return False, str(exc)

    house_dir = os.path.join(district_path, house_id)
    os.makedirs(house_dir, exist_ok=True)
    log_dir = os.path.join(house_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)
    prefix = "%s_" % house_id

    existing = _existing_households(district_path, exclude=house_id)
    compose_prompt = Prompt().load(
        "generate_world_household",
        district_description=description,
        household_count=len(existing),
        existing_types=_existing_types_text(existing),
    )
    try:
        plan = _call_compose(compose_prompt, logger, prefix)
    except LLMCallError as exc:
        print("[Compose failed] %s" % exc)
        return False, str(exc)

    household_type = plan["household_type"]
    member_count = plan["member_count"]
    rationale = plan["rationale"]
    print("[House %s] %s | members %d | %s" % (house_id, household_type, member_count, rationale))

    minimal_type = {
        "type": household_type,
        "description": rationale,
        "members_min": member_count,
        "members_max": member_count,
        "typical_members": member_count,
    }
    persona_texts, persona_rows = gw.sample_personas(minimal_type, seed, n=member_count)

    align_prompt = Prompt().load(
        "generate_world_step2_align",
        household_type=household_type,
        household_description=rationale or description,
        household_member_count=member_count,
        persona_texts="\n\n".join(persona_texts),
    )
    try:
        items, align_source = _call_members(align_prompt, logger, prefix, member_count, persona_texts)
    except LLMCallError as exc:
        print("[Members failed] %s" % exc)
        return False, str(exc)

    members = []
    for index, item in enumerate(items, 1):
        row = persona_rows[index - 1] if isinstance(persona_rows, list) and index <= len(persona_rows) else None
        members.append(_build_member(index, item, row))
    _normalize_personal_appliances(members)
    aligned_texts = [item["portrait"] for item in items]

    household = {
        "type": household_type,
        "llm_generated": True,
        "story": rationale,
        "members": members,
    }
    household_path = os.path.join(house_dir, "household.json")
    _write_json(household_path, household)
    print("[Saved] %s" % household_path)

    aligned_path = os.path.join(house_dir, "aligned_texts.json")
    _write_json(aligned_path, aligned_texts)
    print("[Saved] %s" % aligned_path)

    provenance = {
        "seed": seed,
        "member_count": member_count,
        "canonical_persona_texts": persona_texts,
        "aligned_texts": aligned_texts,
        "source": align_source,
    }
    provenance_path = os.path.join(house_dir, "persona_provenance.json")
    _write_json(provenance_path, provenance)
    print("[Saved] %s (source=%s)" % (provenance_path, align_source))

    house_meta = {
        "house_id": house_id,
        "type": household_type,
        "members_count": len(members),
        "rooms_count": 0,
        "llm_generated": True,
    }
    _upsert_household_meta(world_id, house_meta, district)
    print("[Overview] %s | members: %d" % (household_type, len(members)))
    for member in members:
        print("  - P%s %s | age %s | %s | %s"
              % (member.get("source_persona_index"), member.get("name"),
                 member.get("age"), member.get("gender"), member.get("bedroom")))
    return True, house_dir


def main():
    parser = argparse.ArgumentParser(description="World step: compose a household (type + members) for a district")
    parser.add_argument("--world", required=True, help="world ID")
    parser.add_argument("--district", default=None, help="district name (default: world's primary district)")
    parser.add_argument("--house", default=None,
                        help="household index (0-based) or house_XXXX; default appends the next household")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--all", action="store_true", help="compose one household for every district")
    args = parser.parse_args()

    if args.all:
        ok = True
        districts = gw.districts(args.world)
        if not districts:
            print("[Error] no districts in world %s" % args.world)
            sys.exit(1)
        for district in districts:
            step_ok, result = run_step(args.world, district, None, seed=args.seed)
            if step_ok:
                print(result)
            else:
                print("[Error] %s: %s" % (district, result))
            ok = ok and step_ok
        sys.exit(0 if ok else 1)

    ok, result = run_step(args.world, args.district, args.house, seed=args.seed)
    if ok:
        print(result)
    else:
        print("[Error] %s" % result)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
