import json
import os
import re
import shutil
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
TRASH_DIR = os.path.join(OUTPUT_DIR, "_trash")

CLAYTON_CITY = "Melbourne"
CLAYTON_DISTRICT = "Clayton"
DEFAULT_WORLD_CONFIG = "Melbourne"

# A district is identified by a name; the same rules as a world id apply.
_DISTRICT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_RESERVED_DISTRICT_NAMES = frozenset({"log"})


def load_world_config(world_config_name=None):
    """Load a world configuration: import/world/<name>/<district>/info.md -> list of blocks."""
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
            "name": entry,
            "postcode": entry,
            "world": world_config_name,
            "info": info_text,
        })
    if not blocks:
        raise FileNotFoundError(f"no block configs (info.md) found in world config '{world_config_name}'")
    return {"world": world_config_name, "blocks": blocks}


def load_district_text(district=None, world_config_name=None):
    """Load one district's info.md text by name from the world config.

    Returns "" when the district (or its info.md) is absent; the legacy Clayton
    postcode is no longer forced.
    """
    if not district:
        return ""
    config = load_world_config(world_config_name)
    for block in config["blocks"]:
        if district in (block.get("name"), block.get("postcode")):
            return block["info"]
    return ""


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


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _world_dir(world_id):
    return os.path.join(WORLDS_DIR, world_id)


def _world_meta_path(world_id):
    return os.path.join(_world_dir(world_id), "world.json")


def _district_entry_name(entry):
    if not isinstance(entry, dict):
        return None
    name = entry.get("name") or entry.get("postcode")
    return str(name) if name else None


def _validate_district_name(name):
    token = str(name or "").strip()
    if not token or token in (".", "..") or not _DISTRICT_NAME_RE.match(token):
        raise ValueError(
            "invalid district name %r: use letters, digits, '.', '_' or '-'" % (name,)
        )
    return token


def districts(world_id):
    """District names of a world: world.json's districts[].name, else child dirs."""
    meta = _read_json(_world_meta_path(world_id))
    if isinstance(meta, dict):
        found = [name for name in (_district_entry_name(e) for e in (meta.get("districts") or [])) if name]
        if found:
            return found
    world_dir = _world_dir(world_id)
    try:
        children = sorted(os.listdir(world_dir))
    except OSError:
        return []
    return [
        child for child in children
        if child not in _RESERVED_DISTRICT_NAMES
        and _DISTRICT_NAME_RE.match(child)
        and os.path.isdir(os.path.join(world_dir, child))
    ]


def primary_district(world_id):
    found = districts(world_id)
    return found[0] if found else ""


def district_dir(world_id, district=None):
    """District directory: worlds/<world>/<district or primary district>."""
    return os.path.join(WORLDS_DIR, world_id, district or primary_district(world_id))


def add_district(world_id, name, description=None):
    """Create a district (local, zero LLM) and register it in world.json.

    Idempotent: an existing district is returned untouched with created=False.
    """
    district = _validate_district_name(name)
    world_dir = _world_dir(world_id)
    meta_path = _world_meta_path(world_id)
    meta = _read_json(meta_path)
    if not isinstance(meta, dict):
        meta = {}
    entries = meta.get("districts")
    if not isinstance(entries, list):
        entries = []
    meta["world_id"] = meta.get("world_id") or world_id
    meta["districts"] = entries
    for entry in entries:
        if _district_entry_name(entry) == district:
            return {"world_id": world_id, "district": district,
                    "district_dir": os.path.abspath(os.path.join(world_dir, district)),
                    "created": False}

    district_path = os.path.join(world_dir, district)
    os.makedirs(district_path, exist_ok=True)
    district_meta_path = os.path.join(district_path, "district.json")
    if not os.path.isfile(district_meta_path):
        _write_json(district_meta_path, {
            "name": district,
            "description": description or "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    entries.append({"name": district, "postcode": district})
    _write_json(meta_path, meta)
    return {"world_id": world_id, "district": district,
            "district_dir": os.path.abspath(district_path), "created": True}


def remove_district(world_id, name, permanent=False):
    """Remove a district; default is recoverable (move to output/_trash/)."""
    district = _validate_district_name(name)
    world_dir = _world_dir(world_id)
    district_path = os.path.join(world_dir, district)
    existed = os.path.isdir(district_path)
    moved_to = None
    if existed:
        if permanent:
            shutil.rmtree(district_path)
        else:
            os.makedirs(TRASH_DIR, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = os.path.join(TRASH_DIR, "%s_%s_%s" % (world_id, district, stamp))
            bump = 0
            while os.path.exists(dest):
                bump += 1
                dest = os.path.join(TRASH_DIR, "%s_%s_%s_%d" % (world_id, district, stamp, bump))
            shutil.move(district_path, dest)
            moved_to = os.path.abspath(dest)

    meta_path = _world_meta_path(world_id)
    meta = _read_json(meta_path)
    if isinstance(meta, dict) and isinstance(meta.get("districts"), list):
        meta["districts"] = [
            entry for entry in meta["districts"] if _district_entry_name(entry) != district
        ]
        _write_json(meta_path, meta)
    return {"world_id": world_id, "district": district, "existed": existed,
            "removed": existed, "moved_to": moved_to}


def init_world(world_id, world_config_name=None, seed=42):
    """Create the world scaffolding: world.json (empty districts) + world log/ dir.

    Districts are created explicitly via add_district(); there is no postcode loop.
    """
    world_config = load_world_config(world_config_name)
    world_dir = _world_dir(world_id)
    os.makedirs(world_dir, exist_ok=True)
    log_dir = os.path.join(world_dir, "log")
    os.makedirs(log_dir, exist_ok=True)

    meta_path = _world_meta_path(world_id)
    world_meta = _read_json(meta_path)
    if not isinstance(world_meta, dict):
        world_meta = {}
    world_meta["world_id"] = world_id
    world_meta["world_config"] = world_config["world"]
    world_meta.setdefault("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if not isinstance(world_meta.get("districts"), list):
        world_meta["districts"] = []
    _write_json(meta_path, world_meta)
    return world_dir, log_dir


def update_world_meta(world_id, house_meta, district=None):
    d_dir = district_dir(world_id, district)
    district_meta_path = os.path.join(d_dir, "households.json")
    if os.path.exists(district_meta_path):
        with open(district_meta_path, "r", encoding="utf-8") as f:
            district_meta = json.load(f)
    else:
        district_meta = {"households": []}
    district_meta.setdefault("households", []).append(house_meta)
    _write_json(district_meta_path, district_meta)
    return district_meta


def list_houses(world_id, district=None):
    d_dir = district_dir(world_id, district)
    if os.path.isdir(d_dir):
        houses = sorted(
            d for d in os.listdir(d_dir)
            if d.startswith("house_") and os.path.isfile(os.path.join(d_dir, d, "household.json"))
        )
        if houses:
            return houses
    if os.path.isfile(os.path.join(_world_dir(world_id), "household.json")):
        return ["house_0001"]
    return []
