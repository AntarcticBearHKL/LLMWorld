"""Unified world generator v1 - single generation pipeline.

Pipeline (per household):
  1. Read the district description from Data/ (clayton_3168_profile.md)
  2. LLM: generate N household types from the district description (specified by --count)
  3. Per household: sample N member personas from the Persona synthesis library by household type
  4. LLM validation: check whether personas are consistent with the household type; on failure
     re-sample a new batch (up to --max-retry times)
  5. LLM: generate room layout, appliance config and member profiles from household type + personas
  6. On structural validation failure -> regenerate (<=2 times) -> fall back to programmatic
     templates (population.py) if still failing

Usage:
  python src/generate_world.py pop03 --count 3 --seed 42 --max-retry 3
"""
import argparse
import json
import os
import random
import re
import sys
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import utils, SubAgent
from engine.prompt import Prompt
import config
from appliances import get_supported_appliances_text, get_appliance_schemas_text

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA_DIR = os.path.join(PROJECT_ROOT, "Persona")
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
DEFAULT_DISTRICT_FILE = os.path.join(DATA_DIR, "clayton_3168_profile_en.md")

CLAYTON_POSTCODE = "3168"
CLAYTON_CITY = "Melbourne"
CLAYTON_DISTRICT = "Clayton"

# Fallback template type keyword mapping (population.py's 8 programmatic household types)
FALLBACK_TYPE_KEYWORDS = [
    (["single parent"], "single_parent"),
    (["living alone"], "single_living"),
    (["share", "roommate"], "share_house"),
    (["student", "international student"], "international_student"),
    (["multigenerational", "three generations"], "multigenerational"),
    (["retired", "elderly"], "retired_couple"),
    (["children", "family"], "family_with_kids"),
]
FALLBACK_DEFAULT = "young_couple"

MAX_BUILD_ATTEMPTS = 3  # LLM retry count for room/appliance generation (including the first attempt)


def load_district_text(path=None):
    path = path or DEFAULT_DISTRICT_FILE
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    print(f"[Warning] District description file not found: {path}; using built-in default description")
    return ("Located in the southeastern part of Melbourne, the Clayton 3168 postcode area is a "
            "multicultural community home to Monash University. The population is young (median age "
            "28) with a high share of students and young professionals; household forms are dominated "
            "by couple-only households, share houses and student households; housing is mostly "
            "townhouses, units and apartments with a high rental share. Median household weekly "
            "income is about AUD 1,778.")


def _escape_newlines_in_strings(text):
    """Escape bare newlines inside JSON string values to \\n (models often emit literal newlines in persona text)."""
    out = []
    in_str = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if in_str:
            if ch == "\\" and i + 1 < n:
                out.append(ch)
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
                out.append(ch)
                i += 1
                continue
            if ch in "\r\n":
                out.append("\\n")
                i += 1
                continue
            out.append(ch)
            i += 1
            continue
        if ch == '"':
            in_str = True
        out.append(ch)
        i += 1
    return "".join(out)


def _parse_json_lenient(text):
    """Lenient parsing of LLM output: tolerates code fences / leading and trailing noise /
    single-quoted keys and values / trailing commas / comments / JS literals.

    Strategy: fix progressively, attempting standard json.loads after each fix;
    if all fixes fail, raise the last exception.
    """
    text = str(text).strip()
    text = utils.clean_json_text(text)  # strip ``` code fences
    if text.startswith("\ufeff"):  # BOM
        text = text[1:].strip()
    text = _escape_newlines_in_strings(text)
    # Extract the first complete JSON (tolerate trailing junk: models often append a
    # second object / </output> tag / explanatory text)
    decoder = json.JSONDecoder()
    start = None
    for i, ch in enumerate(text):
        if ch in "[{":
            start = i
            break
    if start is not None:
        try:
            return decoder.raw_decode(text, start)[0]
        except Exception:
            pass
    # Prefer extracting the ```json code block (models like Matilda often wrap JSON in
    # markdown fences, with explanatory text before and after)
    fence = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.S)
    if fence:
        try:
            return json.loads(fence.group(1).strip())
        except Exception:
            pass
    # Strip leading noise (up to the first { or [)
    start = None
    for i, ch in enumerate(text):
        if ch in "[{":
            start = i
            break
    if start is not None:
        text = text[start:]
    # Remove comments
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)

    def _load(t):
        return json.loads(t)

    # Level 1: as-is
    try:
        return _load(text)
    except Exception:
        pass
    # Level 1.5: normalize double braces (models occasionally copy the {{ }} escaping
    # straight from template examples)
    t1 = re.sub(r"\{\{", "{", text)
    t1 = re.sub(r"\}\}", "}", t1)
    try:
        return _load(t1)
    except Exception:
        pass
    # Level 2: remove trailing commas + convert JS literals -> JSON literals
    t2 = re.sub(r",\s*([}\]])", r"\1", text)
    t2 = re.sub(r"\bTrue\b", "true", t2)
    t2 = re.sub(r"\bFalse\b", "false", t2)
    t2 = re.sub(r"\bNone\b", "null", t2)
    try:
        return _load(t2)
    except Exception:
        pass
    # Level 3: single-quoted property names ({ 'xxx': / , 'xxx': ), string values
    # (: 'xxx' ,), finally convert any remaining single-quote pairs to double quotes
    # (covers array elements like ['a', 'b'])
    t3 = re.sub(r"([{,])\s*'([^']+)'\s*:", r'\1"\2":', t2)
    t3 = re.sub(r":\s*'([^']+)'(\s*[,}\]])", r':"\1"\2', t3)
    t3 = re.sub(r"'([^']*)'", r'"\1"', t3)
    try:
        return _load(t3)
    except Exception as e:
        raise ValueError(f"Lenient JSON parsing failed (first 300 chars of raw output: "
                         f"{text[:300]}): {e}")


class ChatLogger:
    """LLM call logger: writes one readable .md + appends one structured .jsonl per call.

    Readable file: log/<prefix><stage>.md   - full prompt / thinking(thinking) / response
                  prefix belongs to the caller (e.g. house_0001_ / global_); files of the
                  same household share the same suffix
    Structured:   log/llm_chat.jsonl        - one full record per line (ok/error/retries included)
    """

    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.jsonl_path = os.path.join(log_dir, "llm_chat.jsonl")
        self._seq = 0
        self._lock = threading.Lock()  # lock against interleaved writes from parallel households

    def record(self, stage, prompt, response, reasoning=None, ok=True, error=None,
               attempt=1, prefix=""):
        with self._lock:
            self._seq += 1
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = {
                "seq": self._seq, "time": ts, "prefix": prefix, "stage": stage,
                "attempt": attempt, "ok": ok, "prompt": prompt, "response": response,
                "reasoning": reasoning, "error": error,
            }
            with open(self.jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            # Keep only the final .md per house per stage (retries overwrite; suffix fixed, no renumbering)
            md_path = os.path.join(self.log_dir, f"{prefix}{stage}.md")
            lines = [f"# [{ts}] {prefix}{stage}",
                     "\n## Prompt\n", prompt or "(empty)", ]
            if reasoning:
                lines += ["\n## Thinking\n", reasoning]
            lines += ["\n## Response\n", response or "(empty)"]
            if error:
                lines += ["\n## Error\n", str(error)]
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")


def llm_json(prompt, label, attempts=2, logger=None, stage=None, thinking=None,
             prefix=""):
    """Call the LLM and parse the JSON; silently retry attempts times on failure,
    return (data, warnings).

    Retries produce no visible message (engineering fallback); only final failure returns a warning.
    """
    warnings = []
    if thinking is None:
        thinking = config.THINKING
    content = reasoning = None
    last_error = None
    for i in range(attempts):
        try:
            result = SubAgent.single_call(prompt, json_mode=True, thinking=thinking)
            content = result["content"] if isinstance(result, dict) else result
            reasoning = result.get("reasoning_content") if isinstance(result, dict) else None
            try:
                data = utils.parse_json_response(content)
            except Exception:
                data = _parse_json_lenient(content)
            if isinstance(data, dict) or isinstance(data, list):
                if logger:
                    logger.record(stage, prompt, content, reasoning=reasoning,
                                  ok=True, attempt=i + 1, prefix=prefix)
                return data, warnings
            raise ValueError("JSON top level must be an object or array")
        except Exception as e:
            last_error = e
            if logger:
                logger.record(stage, prompt, content, reasoning=reasoning,
                              ok=False, error=str(e), attempt=i + 1, prefix=prefix)
            if i < attempts - 1:
                prompt += ("\n\nImportant: your previous output was not valid JSON. "
                           "Output again: a single valid JSON object only, no explanation, no code fences.")
    warnings.append(f"{label} call failed: {last_error}")
    return None, warnings


def _coerce_household_types(data):
    """Normalize various model return structures into {"household_types": [...]}.

    Supports three shapes: {household_types: [...]} / single object {type: ...} / bare array [...].
    """
    if isinstance(data, list):
        return {"household_types": data}
    if isinstance(data, dict):
        if isinstance(data.get("household_types"), list):
            return data
        if "type" in data or "household_type" in data:
            return {"household_types": [data]}
    return data


def generate_household_types(district_text, count, prompt_obj, logger=None,
                             thinking=None, prefix=""):
    """Step 1: district description -> count household types. Returns [(type, desc, members, housing), ...]"""
    rendered = prompt_obj.load("generate_world_step1_types",
                               district_info=district_text, count=count)
    data, warnings = llm_json(rendered, "Household type generation", logger=logger,
                              stage="step1_types", thinking=thinking, prefix=prefix)
    for w in warnings:
        print(f"  [Warning] {w}")
    data = _coerce_household_types(data)
    if not isinstance(data, dict) or not isinstance(data.get("household_types"), list):
        print("[Error] Household type generation returned an invalid structure; aborting")
        sys.exit(1)
    types = []
    for t in data["household_types"]:
        if not isinstance(t, dict):
            continue
        # Field-name compatibility for models like Matilda: household_type->type; housing
        # fields vary widely, so match by the housing prefix
        if "type" not in t and "household_type" in t:
            t["type"] = t["household_type"]
        if "typical_members" not in t and "typical_member_count" in t:
            t["typical_members"] = t["typical_member_count"]
        if "housing_hint" not in t:
            for k in ("typical_housing", "housing_need", "housing_type", "housing"):
                if k in t:
                    t["housing_hint"] = t[k]
                    break
        if not str(t.get("type", "")).strip():
            continue
        try:
            members = int(t.get("typical_members", 2))
        except (TypeError, ValueError):
            # Models may return strings like "3-5 young students": extract the first number
            m = re.search(r"\d+", str(t.get("typical_members", "")))
            members = int(m.group()) if m else 2
        members = max(1, min(8, members))
        types.append({
            "type": str(t["type"]).strip(),
            "description": str(t.get("description", "")).strip(),
            "typical_members": members,
            "housing_hint": str(t.get("housing_hint", "")).strip(),
        })
    # Models may not strictly obey "generate N households": extras are truncated, fewer are kept as-is
    types = types[:count]
    if not types:
        print("[Error] Household type list is empty; aborting")
        sys.exit(1)
    return types


def sample_personas(household_type, attempt_seed):
    """Step 3: sample personas from the Persona library by member count, render as persona text.
    Returns (texts, rows)."""
    if PERSONA_DIR not in sys.path:
        sys.path.insert(0, PERSONA_DIR)
    from sampler import PersonaSampler
    from persona_render import PersonaRenderer
    n = household_type["typical_members"]
    sampler = PersonaSampler(data_dir=PERSONA_DIR, seed=attempt_seed)
    rows = sampler.sample(n)  # uses internal rng (seeded by attempt_seed)
    renderer = PersonaRenderer(PERSONA_DIR)
    texts = ["Member %d:\n%s" % (i + 1, renderer.render(r)) for i, r in enumerate(rows)]
    return texts, rows


def align_personas(household_type, persona_texts, prompt_obj, logger=None,
                   thinking=None, prefix=""):
    """Step 2: the LLM aligns the sampled personas directly to the household setup -
    rewriting conflicting parts and keeping unrelated parts as-is.

    No validation or explanation of "what is wrong"; returns the final personas matching
    the setup directly. Returns (final_texts, warnings); final_texts is None on abnormal
    output (caller keeps the original personas).
    """
    rendered = prompt_obj.load(
        "generate_world_step2_align",
        household_type=household_type["type"],
        household_description=household_type["description"],
        member_count=household_type["typical_members"],
        persona_texts="\n\n".join(persona_texts),
    )
    data, warnings = llm_json(rendered, "Persona alignment", logger=logger,
                              stage="step2_align", thinking=thinking, prefix=prefix)
    if not isinstance(data, dict) or not isinstance(data.get("members"), list):
        return None, warnings + ["Persona alignment output abnormal; using original personas"]
    aligned = [str(m).strip() for m in data["members"] if str(m).strip()]
    if len(aligned) != len(persona_texts):
        return None, warnings + ["Persona alignment member count mismatch; using original personas"]
    return aligned, warnings


def build_household(household_type, persona_texts, district_text, prompt_obj,
                    logger=None, thinking=None, prefix="", retry_hint=None):
    """Step 3: the LLM generates rooms/appliances and member profiles from aligned personas
    + household setup. Returns household dict."""
    rendered = prompt_obj.load(
        "generate_world_step3_household",
        district_info=district_text,
        household_type=household_type["type"],
        household_description=household_type["description"],
        housing_hint=household_type["housing_hint"],
        member_count=household_type["typical_members"],
        persona_texts="\n\n".join(persona_texts),
        supported_appliances=get_supported_appliances_text(),
        appliance_schemas=get_appliance_schemas_text(),
    )
    if retry_hint:
        rendered += (f"\n\nImportant: your previous output was rejected: {retry_hint}. "
                     "Output a complete JSON object again, containing home (rooms layout) and members.")
    data, warnings = llm_json(rendered, "Household generation", logger=logger,
                              stage="step3_household", thinking=thinking, prefix=prefix)
    return data, warnings


SUPPORTED_APPLIANCES = None


def _supported_set():
    global SUPPORTED_APPLIANCES
    if SUPPORTED_APPLIANCES is None:
        from appliances import get_supported_appliances
        SUPPORTED_APPLIANCES = set(get_supported_appliances())
    return SUPPORTED_APPLIANCES


def _coerce_household_structure(h):
    """Normalize model output structure variants into {home, members, ...}.

    Matilda etc. sometimes put rooms at top level, wrap everything in a
    "household" object, or use home_name/size_sqm instead of home.name/size.
    """
    if not isinstance(h, dict):
        return h
    if "household" in h and isinstance(h["household"], dict):
        inner = h["household"]
        for k, v in inner.items():
            h.setdefault(k, v)
    if "home" not in h and isinstance(h.get("rooms"), list):
        h["home"] = {"rooms": h["rooms"]}
        if "size_sqm" in h:
            h["home"]["size"] = h["size_sqm"]
        h["home"].setdefault("name", h.get("home_name") or h.get("type") or "Home")
    return h


def _repair_household(h, expected_members=None):
    """Lightweight repair: fill missing fields/defaults, filter invalid appliances.
    Returns (ok, problems)."""
    h = _coerce_household_structure(h)
    problems = []
    if not isinstance(h, dict):
        return False, ["Top level is not an object"]
    home = h.get("home")
    if not isinstance(home, dict):
        return False, ["Missing home"]
    rooms = home.get("rooms")
    if not isinstance(rooms, list) or not rooms:
        return False, ["home.rooms missing or empty"]
    supported = _supported_set()
    for room in rooms:
        if not isinstance(room, dict):
            problems.append("Invalid room; skipped")
            continue
        if "name" not in room and "type" in room:
            # Models often put the room name in the type field: move it to name
            # (simulation uses room['name'])
            room["name"] = room["type"]
        room.setdefault("size", 0)
        apps = room.get("appliances")
        if not isinstance(apps, list):
            room["appliances"] = []
            continue
        kept = []
        for app in apps:
            if not isinstance(app, dict) or app.get("type") not in supported:
                problems.append(f"Invalid appliance {app.get('type') if isinstance(app, dict) else app}; removed")
                continue
            app.setdefault("brand", "Generic")
            app.setdefault("power", None)
            app.setdefault("age", 0)
            kept.append(app)
        room["appliances"] = kept
    members = h.get("members")
    if not isinstance(members, list) or not members:
        return False, ["members missing or empty"]
    if expected_members is not None:
        if len(members) > expected_members:
            problems.append(f"Member count {len(members)} > expected {expected_members}; "
                            f"truncated to the first {expected_members}")
            members = members[:expected_members]
            h["members"] = members
        elif len(members) < expected_members:
            return False, [f"Member count {len(members)} < expected {expected_members}"]
    member_names = [str(m.get("name", "")).strip() for m in members if isinstance(m, dict)]
    if len(member_names) != len(set(member_names)):
        return False, [f"Duplicate member names: {member_names}"]
    for m in members:
        if not isinstance(m, dict):
            problems.append("Invalid member; skipped")
            continue
        m.setdefault("gender", "Unknown")
        m.setdefault("occupation", "Unemployed")
        if not isinstance(m.get("work_schedule"), dict):
            m["work_schedule"] = {"start": "09:00", "end": "17:00",
                                   "remote": False, "work_days": [1, 2, 3, 4, 5]}
        pers = m.setdefault("personality", {})
        if not isinstance(pers, dict):
            m["personality"] = {"traits": []}
            pers = m["personality"]
        if isinstance(pers.get("traits"), str):
            pers["traits"] = [pers["traits"]]
        pers.setdefault("traits", [])
        pers.setdefault("behavior_text", "")
        pers.setdefault("energy_awareness", "Low")   # analysis tools group by this; fallback when missing
        pers.setdefault("news_sensitivity", "Medium")  # used when building simulation prompts; fallback
        if not isinstance(pers.get("big_five"), dict):
            pers["big_five"] = {}                   # analysis attribution depends on this; fallback
        habits = m.setdefault("habits", {})
        if not isinstance(habits, dict):
            m["habits"] = {}
            habits = m["habits"]
        # Normalize model field-name variants: wake->wake_time, sleep->sleep_time
        if "wake" in habits and "wake_time" not in habits:
            habits["wake_time"] = habits.pop("wake")
        if "sleep" in habits and "sleep_time" not in habits:
            habits["sleep_time"] = habits.pop("sleep")
        # Models often put work_days/remote into habits: move them back to work_schedule
        if "work_days" in habits and "work_days" not in m["work_schedule"]:
            m["work_schedule"]["work_days"] = habits.pop("work_days")
        if "remote" in habits and isinstance(m.get("work_schedule"), dict):
            m["work_schedule"]["remote"] = habits.pop("remote")
        habits.setdefault("wake_time", "07:30")
        habits.setdefault("sleep_time", "23:00")
        habits.setdefault("exercise", "Occasional walks")
        habits.setdefault("hobbies", [])
        health = m.setdefault("health", {})
        if not isinstance(health, dict):
            m["health"] = {}
            health = m["health"]
        health.setdefault("condition", "Good")
        if not isinstance(health.get("temperature_preference"), dict):
            # Models often return "22°C" or 22: extract the number into
            # {"summer": v, "winter": v}
            nums = re.findall(r"\d+", str(health.get("temperature_preference", "")))
            health["temperature_preference"] = {"summer": int(nums[0]), "winter": int(nums[0])} if nums else {"summer": 26, "winter": 22}
        papps = m.get("personal_appliances")
        if (not isinstance(papps, list) or not papps) and isinstance(m.get("appliances"), list) and m["appliances"]:
            # Models often put personal appliances under the appliances key
            # (personal_appliances missing or an empty array)
            m["personal_appliances"] = m.pop("appliances")
            papps = m["personal_appliances"]
        if not isinstance(papps, list):
            m["personal_appliances"] = []
        else:
            kept = []
            for app in papps:
                if not isinstance(app, dict) or app.get("type") not in supported:
                    problems.append(f"Invalid personal appliance {app.get('type') if isinstance(app, dict) else app}; removed")
                    continue
                app.setdefault("brand", "Generic")
                app.setdefault("power", None)
                app.setdefault("age", 0)
                kept.append(app)
            m["personal_appliances"] = kept
        if not (str(m.get("name", "")).strip() and isinstance(m.get("age"), int)):
            return False, [f"Member missing name/age: {m.get('name', '?')}"]
    return True, problems


def fallback_household(household_type, rng):
    """Programmatic fallback after repeated LLM failures (population.py template)."""
    from population import _build_template
    key = FALLBACK_DEFAULT
    text = household_type["type"] + household_type["description"]
    for keywords, tkey in FALLBACK_TYPE_KEYWORDS:
        if any(k in text for k in keywords):
            key = tkey
            break
    h = _build_template(key, rng)
    h["llm_generated"] = False
    return h


def generate_one_household(household_type, district_text, rng, prompt_obj,
                           logger=None, thinking=None, prefix=""):
    """Full single-household flow: sample -> LLM aligns personas to the household setup ->
    generate rooms/appliances. Straight three steps, no branching.

    Returns (household, notes, persona_texts, original_persona_texts, persona_seed).
    persona_texts is the final adopted persona set (aligned); original_persona_texts is the
    raw sampled persona set.
    """
    notes = []
    attempt_seed = rng.randint(0, 2 ** 31 - 1)
    persona_texts, rows = sample_personas(household_type, attempt_seed)
    original_persona_texts = list(persona_texts)

    aligned_texts, warnings = align_personas(household_type, persona_texts, prompt_obj,
                                             logger=logger, thinking=thinking, prefix=prefix)
    notes.extend(warnings)
    if aligned_texts is not None:
        persona_texts = aligned_texts

    problems = []
    for attempt in range(MAX_BUILD_ATTEMPTS):
        hint = "; ".join(problems) if attempt > 0 else None
        household, warnings = build_household(household_type, persona_texts,
                                              district_text, prompt_obj,
                                              logger=logger, thinking=thinking,
                                              prefix=prefix, retry_hint=hint)
        notes.extend(warnings)
        if household is None:
            continue
        ok, problems = _repair_household(household, len(persona_texts))
        if ok:
            household.setdefault("type", household_type["type"])
            household["llm_generated"] = True
            return household, notes, persona_texts, original_persona_texts, attempt_seed
        notes.append(f"Household structure validation failed (attempt {attempt + 1}): {problems}")

    notes.append("LLM household generation failed repeatedly; falling back to the programmatic template")
    household = fallback_household(household_type, rng)
    household.setdefault("type", household_type["type"])
    return household, notes, persona_texts, original_persona_texts, attempt_seed


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_world(world_id, district_text, seed):
    """Create the world directory + log/ + district.json + world.json skeleton (written
    immediately). Returns (world_dir, log_dir)."""
    world_dir = os.path.join(PROJECT_ROOT, "worlds", world_id)
    district_dir = os.path.join(world_dir, CLAYTON_POSTCODE)
    log_dir = os.path.join(world_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(district_dir, exist_ok=True)

    district = {
        "postcode": CLAYTON_POSTCODE,
        "location": {"city": CLAYTON_CITY, "district": CLAYTON_DISTRICT,
                     "coordinates": {"lat": -37.916, "lon": 145.123}},
        "economic_level": "Medium",
        "description": district_text,
    }
    _write_json(os.path.join(district_dir, "district.json"), district)

    world_meta = {
        "world_id": world_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_prompt": (f"Unified generator: district description -> household types -> "
                        f"Persona sampling/validation -> rooms and appliances (seed={seed})"),
        "generator": "generate_world.py v2",
        "district": {
            "postcode": CLAYTON_POSTCODE,
            "city": CLAYTON_CITY,
            "district": CLAYTON_DISTRICT,
            "economic_level": "Medium",
        },
        "households": [],
    }
    _write_json(os.path.join(world_dir, "world.json"), world_meta)
    return world_dir, log_dir


def save_household_types(world_id, household_types):
    """Write the household type list to disk immediately after step 1."""
    _write_json(os.path.join(PROJECT_ROOT, "worlds", world_id, "household_types.json"),
                {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "household_types": household_types})


def save_household_artifacts(world_id, idx, persona_texts, original_persona_texts,
                             persona_seed, household):
    """Write personas.json (original + final personas) + household.json immediately after
    each household is generated."""
    district_dir = os.path.join(PROJECT_ROOT, "worlds", world_id, CLAYTON_POSTCODE)
    house_id = f"house_{idx + 1:04d}"
    house_dir = os.path.join(district_dir, house_id)
    os.makedirs(house_dir, exist_ok=True)

    _write_json(os.path.join(house_dir, "personas.json"), {
        "seed": persona_seed,
        "persona_texts": persona_texts,                    # final aligned personas
        "original_persona_texts": original_persona_texts,  # raw sampled personas (for comparison)
    })
    _write_json(os.path.join(house_dir, "household.json"), household)
    return house_id


def update_world_meta(world_id, house_meta):
    """Incrementally update the households list in world.json after each household."""
    world_path = os.path.join(PROJECT_ROOT, "worlds", world_id, "world.json")
    with open(world_path, "r", encoding="utf-8") as f:
        world_meta = json.load(f)
    world_meta.setdefault("households", []).append(house_meta)
    _write_json(world_path, world_meta)
    return world_meta


def _household_worker(idx, htype, world_id, district_text, prompt_obj, log_dir,
                      thinking, base_seed):
    """Full single-household flow in a separate process: sample -> align personas ->
    generate rooms/appliances -> check -> write to disk.

    Returns (house_meta, household, notes, error, tokens). All multiprocessing args must be
    picklable.
    """
    try:
        rng = random.Random(base_seed * 10007 + idx)  # per-household independent seed; reproducible in parallel or serial
        prefix = f"house_{idx + 1:04d}_"              # fixed log file suffix per household
        logger = ChatLogger(log_dir)                  # created inside the process (logger objects cannot cross processes)
        household, notes, personas, original_personas, p_seed = \
            generate_one_household(htype, district_text, rng, prompt_obj,
                                   logger=logger, thinking=thinking, prefix=prefix)
        house_id = save_household_artifacts(world_id, idx, personas, original_personas,
                                            p_seed, household)
        house_meta = {
            "house_id": house_id,
            "type": household.get("type", "?"),
            "members_count": len(household.get("members", [])),
            "rooms_count": len(household.get("home", {}).get("rooms", [])),
            "llm_generated": household.get("llm_generated", False),
        }
        tokens = SubAgent.get_tokens()  # (cache miss, hit, output) accumulated in this process
        return house_meta, household, notes, None, tokens
    except Exception as e:
        return None, None, [f"Process error: {e}"], str(e), (0, 0, 0)
