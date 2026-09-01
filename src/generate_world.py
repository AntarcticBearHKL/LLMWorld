import json
import os
import sys
import threading
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMPORT_DIR = os.path.join(PROJECT_ROOT, "import")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
PERSONA_DIR = os.path.join(IMPORT_DIR, "persona")
DATA_DIR = os.path.join(IMPORT_DIR, "worldinfo")
WORLDS_DIR = os.path.join(OUTPUT_DIR, "worlds")
SIMULATION_DIR = os.path.join(OUTPUT_DIR, "simulation")
DEFAULT_DISTRICT_FILE = os.path.join(DATA_DIR, "clayton_3168_profile_en.md")

CLAYTON_POSTCODE = "3168"
CLAYTON_CITY = "Melbourne"
CLAYTON_DISTRICT = "Clayton"


class ChatLogger:

    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.inputs_path = os.path.join(log_dir, "inputs.json")
        self.responses_path = os.path.join(log_dir, "llm_responses.json")
        self.transfer_path = os.path.join(log_dir, "transfer.json")
        self._seq = 0
        self._lock = threading.Lock()  

    def _append_entries(self, path, entries):
        data = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []
        data.extend(entries)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def record(self, stage, prompt, response, reasoning=None, ok=True, error=None,
               attempt=1, prefix=""):
        with self._lock:
            self._seq += 1
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            input_entry = {
                "seq": self._seq, "time": ts, "prefix": prefix, "stage": stage,
                "attempt": attempt, "prompt": prompt,
                "reasoning": reasoning,
            }
            response_entry = {
                "seq": self._seq, "time": ts, "prefix": prefix, "stage": stage,
                "attempt": attempt, "ok": ok, "response": response, "error": error,
            }
            self._append_entries(self.inputs_path, [input_entry])
            self._append_entries(self.responses_path, [response_entry])

    def record_transfer(self, stage, request, response=None, error=None, attempt=1, prefix=""):
        with self._lock:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = {"time": ts, "prefix": prefix, "stage": stage, "attempt": attempt,
                     "request": request, "response": response, "error": error}
            self._append_entries(self.transfer_path, [entry])


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


def sample_personas(household_type, attempt_seed, n=None):
    if PERSONA_DIR not in sys.path:
        sys.path.insert(0, PERSONA_DIR)
    from sampler import PersonaSampler
    from persona_render import PersonaRenderer
    n = n if n is not None else household_type.get("typical_members", household_type.get("members_min", 2))
    sampler = PersonaSampler(data_dir=PERSONA_DIR, seed=attempt_seed)
    rows = sampler.sample(n)
    renderer = PersonaRenderer(PERSONA_DIR)
    texts = ["Member %d:\n%s" % (i + 1, renderer.render(r)) for i, r in enumerate(rows)]
    return texts, rows


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_world(world_id, district_text, seed):
    world_dir = os.path.join(WORLDS_DIR, world_id)
    district_dir = os.path.join(world_dir, CLAYTON_POSTCODE)
    log_dir = os.path.join(district_dir, "log")
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
        "districts": [
            {
                "postcode": CLAYTON_POSTCODE,
                "city": CLAYTON_CITY,
                "district": CLAYTON_DISTRICT,
                "economic_level": "Medium",
            }
        ],
    }
    _write_json(os.path.join(world_dir, "world.json"), world_meta)
    return world_dir, log_dir


def save_household_artifacts(world_id, idx, persona_texts, original_persona_texts,
                             persona_seed, household):
    district_dir = os.path.join(WORLDS_DIR, world_id, CLAYTON_POSTCODE)
    house_id = f"house_{idx + 1:04d}"
    house_dir = os.path.join(district_dir, house_id)
    os.makedirs(house_dir, exist_ok=True)

    _write_json(os.path.join(house_dir, "personas.json"), {
        "seed": persona_seed,
        "persona_texts": persona_texts,                    
        "original_persona_texts": original_persona_texts,  
    })
    _write_json(os.path.join(house_dir, "household.json"), household)
    return house_id


def update_world_meta(world_id, house_meta):
    district_dir = os.path.join(WORLDS_DIR, world_id, CLAYTON_POSTCODE)
    district_meta_path = os.path.join(district_dir, "households.json")
    if os.path.exists(district_meta_path):
        with open(district_meta_path, "r", encoding="utf-8") as f:
            district_meta = json.load(f)
    else:
        district_meta = {"households": []}
    district_meta.setdefault("households", []).append(house_meta)
    _write_json(district_meta_path, district_meta)
    return district_meta
