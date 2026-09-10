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
WORLD_CONFIG_DIR = os.path.join(IMPORT_DIR, "world")
WORLDS_DIR = os.path.join(OUTPUT_DIR, "worlds")
SIMULATION_DIR = os.path.join(OUTPUT_DIR, "simulation")

CLAYTON_POSTCODE = "3168"
CLAYTON_CITY = "Melbourne"
CLAYTON_DISTRICT = "Clayton"
DEFAULT_WORLD_CONFIG = "Melbourne"


def load_world_config(world_config_name=None):
    """Load a world configuration: import/world/<name>/<postcode>/info.md -> list of blocks."""
    world_config_name = world_config_name or DEFAULT_WORLD_CONFIG
    config_root = os.path.join(WORLD_CONFIG_DIR, world_config_name)
    if not os.path.isdir(config_root):
        raise FileNotFoundError(
            f"world config '{world_config_name}' not found under {WORLD_CONFIG_DIR} "
            f"(available: {sorted(os.listdir(WORLD_CONFIG_DIR)) if os.path.isdir(WORLD_CONFIG_DIR) else []})"
        )
    blocks = []
    for entry in sorted(os.listdir(config_root)):
        block_dir = os.path.join(config_root, entry)
        if not os.path.isdir(block_dir):
            continue
        info_path = os.path.join(block_dir, "info.md")
        if not os.path.isfile(info_path):
            continue
        with open(info_path, "r", encoding="utf-8") as f:
            info_text = f.read().strip()
        blocks.append({
            "postcode": entry,
            "world": world_config_name,
            "info": info_text,
        })
    if not blocks:
        raise FileNotFoundError(f"no block configs (info.md) found in world config '{world_config_name}'")
    return {"world": world_config_name, "blocks": blocks}


def load_district_text(postcode=None, world_config_name=None):
    """Load one block's info.md text by postcode from the world config."""
    config = load_world_config(world_config_name)
    postcode = postcode or CLAYTON_POSTCODE
    for block in config["blocks"]:
        if block["postcode"] == postcode:
            return block["info"]
    raise FileNotFoundError(
        f"postcode '{postcode}' not found in world config '{config['world']}' "
        f"(available: {[b['postcode'] for b in config['blocks']]})"
    )


class ChatLogger:

    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
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
               attempt=1, prefix="", schema=None, parsed=None):
        with self._lock:
            self._seq += 1
            seq = self._seq
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            md_path = os.path.join(self.log_dir, f"{seq:05d}_{stage}.md")
            lines = [f"# {stage}  (attempt {attempt})",
                     "",
                     "## 对话信息",
                     "",
                     f"- time: {ts}",
                     f"- seq: {seq}",
                     f"- prefix: {prefix}",
                     f"- stage: {stage}",
                     f"- attempt: {attempt}",
                     f"- ok: {ok}",
                     ]
            if error:
                lines.append(f"- error: {error}")
            lines += ["",
                      "## 输入",
                      "",
                      "```",
                      prompt or "(empty)",
                      "```",
                      "",
                      "## Schema",
                      "",
                      "```json",
                      ]
            if schema is not None:
                lines.append(json.dumps(schema, ensure_ascii=False, indent=2))
            else:
                lines.append("(none)")
            lines += ["```",
                      "",
                      "## 返回(原始)",
                      "",
                      "```",
                      response or "(empty)",
                      "```",
                      ]
            if parsed is not None:
                lines += ["",
                          "## 解析结果",
                          "",
                          "```json",
                          json.dumps(parsed, ensure_ascii=False, indent=2),
                          "```",
                          ]
            lines += [""]
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

    def record_transfer(self, stage, request, response=None, error=None, attempt=1, prefix=""):
        with self._lock:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = {"time": ts, "prefix": prefix, "stage": stage, "attempt": attempt,
                     "request": request, "response": response, "error": error}
            self._append_entries(self.transfer_path, [entry])


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


def init_world(world_id, world_config_name=None, seed=42):
    world_config = load_world_config(world_config_name)
    world_dir = os.path.join(WORLDS_DIR, world_id)
    os.makedirs(world_dir, exist_ok=True)

    districts = []
    for block in world_config["blocks"]:
        postcode = block["postcode"]
        district_dir = os.path.join(world_dir, postcode)
        log_dir = os.path.join(district_dir, "log")
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(district_dir, exist_ok=True)
        district = {
            "postcode": postcode,
            "location": {"city": world_config["world"], "district": postcode,
                         "coordinates": {"lat": -37.916, "lon": 145.123}},
            "economic_level": "Medium",
            "description": block["info"],
        }
        _write_json(os.path.join(district_dir, "district.json"), district)
        districts.append({
            "postcode": postcode,
            "city": world_config["world"],
            "district": postcode,
            "economic_level": "Medium",
        })

    world_meta = {
        "world_id": world_id,
        "world_config": world_config["world"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "districts": districts,
    }
    _write_json(os.path.join(world_dir, "world.json"), world_meta)
    return world_dir, os.path.join(world_dir, districts[0]["postcode"], "log")


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


def list_houses(world_id, postcode=CLAYTON_POSTCODE):
    district_dir = os.path.join(WORLDS_DIR, world_id, postcode)
    if os.path.isdir(district_dir):
        houses = sorted(
            d for d in os.listdir(district_dir)
            if d.startswith("house_") and os.path.isfile(os.path.join(district_dir, d, "household.json"))
        )
        if houses:
            return houses
    if os.path.isfile(os.path.join(WORLDS_DIR, world_id, "household.json")):
        return ["house_0001"]
    return []
