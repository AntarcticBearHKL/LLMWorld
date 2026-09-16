"""World lifecycle service for the LLMWorld Research Console.

Owns the filesystem side of a world: creating an EMPTY world (scaffolding only,
zero LLM calls), resolving and deleting world directories, and reporting per-step
build progress for the four world-generation stages. Nothing here calls the LLM
or run.py - build jobs are still executed by :mod:`backend.jobs`.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from . import paths
from .models import (
    ArtifactRef,
    BuildPreview,
    BuildState,
    BuildStepStatus,
    HouseStepStatus,
)

WORLDS_DIR = paths.WORLDS_DIR
OUTPUT_DIR = paths.OUTPUT_DIR
TRASH_DIR = os.path.join(OUTPUT_DIR, "_trash")

DEFAULT_POSTCODE = "3168"
DEFAULT_SEED = 42
DEFAULT_WORLD_CONFIG = "Melbourne"

STEP_ORDER: Tuple[str, ...] = ("district", "household", "home")
STEP_SCOPE: Dict[str, str] = {
    "district": "district",
    "household": "district",
    "home": "house",
}

_WORLD_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_DISTRICT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_RESERVED_DISTRICT_NAMES = frozenset({"log"})
_HOUSE_RE = re.compile(r"^house_(\d+)$")


def _gw() -> Any:
    import generate_world

    return generate_world


def read_json(path: str) -> Any:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _is_file(path: str) -> bool:
    return os.path.isfile(path)


def _district_entry_name(entry: Any) -> Optional[str]:
    if not isinstance(entry, dict):
        return None
    name = entry.get("name") or entry.get("postcode")
    return str(name) if name else None


def districts(world_id: str) -> List[str]:
    """District names of a world: world.json's districts, else child dirs."""
    meta = read_json(world_meta_path(world_id))
    if isinstance(meta, dict):
        found = [
            name
            for name in (_district_entry_name(entry) for entry in (meta.get("districts") or []))
            if name
        ]
        if found:
            return found
    world_dir = resolve_world_dir(world_id)
    try:
        children = sorted(os.listdir(world_dir))
    except OSError:
        return []
    return [
        child for child in children
        if child not in _RESERVED_DISTRICT_NAMES
        and _DISTRICT_RE.match(child)
        and os.path.isdir(os.path.join(world_dir, child))
    ]


def primary_district(world_id: str) -> str:
    found = districts(world_id)
    return found[0] if found else DEFAULT_POSTCODE


def normalize_district(name: Any) -> str:
    token = str(name or "").strip()
    if not token or token in (".", "..") or not _DISTRICT_RE.match(token):
        raise ValueError(
            "invalid district name %r: use letters, digits, '.', '_' or '-'" % (name,)
        )
    return token


def resolve_district(world_id: str, district: Any = None) -> str:
    """Resolve a district selector (None -> the world's primary district)."""
    token = str(district or "").strip()
    if not token:
        return primary_district(world_id)
    return normalize_district(token)


def create_district(
    world_id: str, name: str, description: Optional[str] = None
) -> Dict[str, Any]:
    """Create a district locally (zero LLM); idempotent, ``created=False`` if present."""
    wid = normalize_world_id(world_id)
    if not os.path.isdir(os.path.join(WORLDS_DIR, wid)):
        raise ValueError("world not found: %s" % wid)
    result = _gw().add_district(wid, name, description)
    district = str(result.get("district") or normalize_district(name))
    meta = read_json(os.path.join(district_dir(wid, district), "district.json"))
    stored = meta.get("description") if isinstance(meta, dict) else None
    return {
        "world_id": wid,
        "name": district,
        "description": stored if isinstance(stored, str) else description,
        "district_dir": result.get("district_dir")
        or os.path.abspath(district_dir(wid, district)),
        "created": bool(result.get("created")),
    }


def delete_district(
    world_id: str, name: str, permanent: bool = False
) -> Dict[str, Any]:
    """Remove a district; default is recoverable (move to output/_trash/)."""
    wid = normalize_world_id(world_id)
    if not os.path.isdir(os.path.join(WORLDS_DIR, wid)):
        raise ValueError("world not found: %s" % wid)
    result = _gw().remove_district(wid, name, permanent)
    return {
        "name": str(result.get("district") or name),
        "existed": bool(result.get("existed")),
        "deleted": bool(result.get("removed")),
        "moved_to": result.get("moved_to"),
    }


def normalize_world_id(world_id: str) -> str:
    wid = str(world_id or "").strip()
    if not wid or not _WORLD_ID_RE.match(wid) or wid in (".", ".."):
        raise ValueError(
            "invalid world id %r: use letters, digits, '.', '_' or '-'" % (world_id,)
        )
    return wid


def resolve_world_dir(world_id: str) -> str:
    return os.path.join(WORLDS_DIR, normalize_world_id(world_id))


def world_exists(world_id: str) -> bool:
    return os.path.isdir(resolve_world_dir(world_id))


def create_world(
    world_id: str,
    world_config: Optional[str] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Create an EMPTY world (scaffolding only, zero LLM calls).

    Idempotent: an existing world is returned untouched with ``created=False``.
    """
    wid = normalize_world_id(world_id)
    world_dir = os.path.join(WORLDS_DIR, wid)
    if os.path.isdir(world_dir):
        return {
            "world_id": wid,
            "world_dir": os.path.abspath(world_dir),
            "created": False,
        }

    config_name = world_config or DEFAULT_WORLD_CONFIG
    seed_value = DEFAULT_SEED if seed is None else int(seed)
    try:
        created_dir, _log_dir = _gw().init_world(wid, config_name, seed_value)
    except FileNotFoundError as exc:
        raise ValueError(str(exc)) from exc
    return {
        "world_id": wid,
        "world_dir": os.path.abspath(created_dir),
        "created": True,
    }


def delete_world(world_id: str, permanent: bool = False) -> Dict[str, Any]:
    """Remove a world directory; default is recoverable (move to output/_trash/)."""
    wid = normalize_world_id(world_id)
    world_dir = os.path.join(WORLDS_DIR, wid)
    if not os.path.isdir(world_dir):
        return {
            "world_id": wid,
            "existed": False,
            "deleted": False,
            "moved_to": None,
        }
    if permanent:
        shutil.rmtree(world_dir)
        return {
            "world_id": wid,
            "existed": True,
            "deleted": True,
            "moved_to": None,
        }

    os.makedirs(TRASH_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(TRASH_DIR, "%s_%s" % (wid, stamp))
    bump = 0
    while os.path.exists(dest):
        bump += 1
        dest = os.path.join(TRASH_DIR, "%s_%s_%d" % (wid, stamp, bump))
    shutil.move(world_dir, dest)
    return {
        "world_id": wid,
        "existed": True,
        "deleted": True,
        "moved_to": os.path.abspath(dest),
    }


def clone_world(world_id: str, new_id: str) -> Dict[str, Any]:
    """Deep-copy a world (households included) to a new id.

    Spacetimes are deliberately NOT copied: a clone is a fresh draft you edit.
    """
    src = normalize_world_id(world_id)
    dst = normalize_world_id(new_id)
    if src == dst:
        raise ValueError("clone target must differ from the source world")
    src_dir = os.path.join(WORLDS_DIR, src)
    if not os.path.isdir(src_dir):
        raise ValueError("world not found: %s" % src)
    dst_dir = os.path.join(WORLDS_DIR, dst)
    if os.path.exists(dst_dir):
        raise ValueError("target world already exists: %s" % dst)

    shutil.copytree(src_dir, dst_dir)
    meta = read_json(world_meta_path(dst))
    if isinstance(meta, dict):
        meta["world_id"] = dst
        meta["cloned_from"] = src
        with open(world_meta_path(dst), "w", encoding="utf-8") as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    return {
        "world_id": dst,
        "cloned_from": src,
        "world_dir": os.path.abspath(dst_dir),
    }


def district_dir(world_id: str, district: Optional[str] = None) -> str:
    return os.path.join(resolve_world_dir(world_id), district or primary_district(world_id))


def world_meta_path(world_id: str) -> str:
    return os.path.join(resolve_world_dir(world_id), "world.json")


def types_path(world_id: str, district: Optional[str] = None) -> str:
    return os.path.join(district_dir(world_id, district), "household_types.json")


def households_meta_path(world_id: str, district: Optional[str] = None) -> str:
    return os.path.join(district_dir(world_id, district), "households.json")


def log_dir(world_id: str, district: Optional[str] = None) -> str:
    return os.path.join(district_dir(world_id, district), "log")


def llm_trace_path(world_id: str, job_id: str, district: Optional[str] = None) -> str:
    """Per-job LLM trace (JSONL) written by the build subprocess.

    Scoping the trace to a single job keeps every call attributable to the
    build step that made it without tagging anything inside ``src/``.
    """
    return os.path.join(log_dir(world_id, district), "llm_trace_%s.jsonl" % job_id)


def house_dir(world_id: str, house_label_value: str, district: Optional[str] = None) -> str:
    return os.path.join(district_dir(world_id, district), house_label_value)


def house_file(
    world_id: str, house_label_value: str, name: str, district: Optional[str] = None
) -> str:
    return os.path.join(house_dir(world_id, house_label_value, district), name)


def house_label(index: int) -> str:
    return "house_%04d" % (int(index) + 1)


def house_index_from(house_label_or_index: Any) -> Optional[int]:
    text = str(house_label_or_index or "").strip()
    match = _HOUSE_RE.match(text)
    if match:
        return int(match.group(1)) - 1
    if text.lstrip("-").isdigit():
        return int(text)
    return None


def count_houses(world_id: str, district: Optional[str] = None) -> int:
    """Number of ``house_XXXX`` directories present in a district."""
    base = district_dir(world_id, district)
    try:
        children = os.listdir(base)
    except OSError:
        return 0
    return sum(
        1 for name in children
        if _HOUSE_RE.match(name) and os.path.isdir(os.path.join(base, name))
    )


def household_type_count(world_id: str, district: Optional[str] = None) -> int:
    data = read_json(types_path(world_id, district))
    entries = data.get("household_types") if isinstance(data, dict) else data
    return len(entries) if isinstance(entries, list) else 0


def list_house_labels(world_id: str, district: Optional[str] = None) -> List[str]:
    labels = set()
    district_path = district_dir(world_id, district)
    if os.path.isdir(district_path):
        try:
            children = os.listdir(district_path)
        except OSError:
            children = []
        for name in children:
            if _HOUSE_RE.match(name) and os.path.isdir(os.path.join(district_path, name)):
                labels.add(name)
    for index in range(household_type_count(world_id, district)):
        labels.add(house_label(index))
    return sorted(labels)


def resolve_house_label(world_id: str, house: Any, district: Optional[str] = None) -> str:
    """Resolve a house selector ('house_0001', '0' or None) to a house label.

    None selects the first known house, or ``house_0001`` when the world has
    none yet so the step itself fails with a readable reason.
    """
    if house is None or str(house).strip() == "":
        labels = list_house_labels(world_id, district)
        return labels[0] if labels else house_label(0)
    index = house_index_from(house)
    if index is None:
        raise ValueError(
            "unknown house %r: use a house id like 'house_0001' or a 0-based index"
            % (house,)
        )
    if index < 0:
        raise ValueError("house index must be >= 0; got %d" % index)
    return house_label(index)


def member_count(
    world_id: str, house_label_value: Optional[str], district: Optional[str] = None
) -> Optional[int]:
    if not house_label_value:
        return None
    data = read_json(house_file(world_id, house_label_value, "aligned_texts.json", district))
    return len(data) if isinstance(data, list) else None


def _aggregate(
    step: str, scope: str, houses: List[HouseStepStatus], empty_reason: str
) -> BuildStepStatus:
    done = bool(houses) and all(item.done for item in houses)
    runnable = any(item.runnable for item in houses)
    reason: Optional[str] = None
    if not houses:
        reason = empty_reason
    elif not runnable:
        reason = next((item.blocked_reason for item in houses if item.blocked_reason), "blocked")
    return BuildStepStatus(
        step=step,
        scope=scope,
        done=done,
        runnable=runnable,
        blocked_reason=reason,
        houses=houses,
    )


def _house_has_home(path: str) -> bool:
    data = read_json(path)
    return isinstance(data, dict) and isinstance(data.get("home"), dict) and bool(data["home"])


def build_state(world_id: str, district: Optional[str] = None) -> BuildState:
    wid = normalize_world_id(world_id)
    world_dir = os.path.join(WORLDS_DIR, wid)
    exists = os.path.isdir(world_dir)
    district_name = resolve_district(wid, district)
    district_path = district_dir(wid, district_name)

    description_done = _is_file(os.path.join(district_path, "description.md"))
    labels = list_house_labels(wid, district_name) if exists else []

    household_houses: List[HouseStepStatus] = []
    home_houses: List[HouseStepStatus] = []
    for label in labels:
        household_path = house_file(wid, label, "household.json", district_name)
        household_done = _is_file(household_path)
        household_houses.append(
            HouseStepStatus(
                house=label,
                done=household_done,
                runnable=description_done,
                blocked_reason=None
                if description_done
                else "district description missing (run 'district' first)",
            )
        )

        home_done = household_done and _house_has_home(household_path)
        home_houses.append(
            HouseStepStatus(
                house=label,
                done=home_done,
                runnable=household_done,
                blocked_reason=None
                if household_done
                else "household.json missing (run 'household' first)",
            )
        )

    steps = [
        BuildStepStatus(
            step="district",
            scope="district",
            done=description_done,
            runnable=exists,
            blocked_reason=None if exists else "world directory is missing",
        ),
        _aggregate("household", "district", household_houses, "no households yet; run 'household' first"),
        _aggregate("home", "house", home_houses, "no households yet; run 'household' first"),
    ]

    return BuildState(
        world_id=wid,
        world_dir=os.path.abspath(world_dir),
        exists=exists,
        district=district_name,
        houses=labels,
        steps=steps,
    )


def _next_house_label(world_id: str, district: str) -> str:
    highest = -1
    for label in list_house_labels(world_id, district):
        index = house_index_from(label)
        if index is not None and index > highest:
            highest = index
    return house_label(highest + 1)


def _preview_house_label(world_id: str, district: str, step: str, house: Any) -> str:
    if house is not None and str(house).strip():
        return resolve_house_label(world_id, house, district)
    if step == "household":
        return _next_house_label(world_id, district)
    return resolve_house_label(world_id, None, district)


def build_preview(
    world_id: str, step: str, house: Any = None, district: Optional[str] = None
) -> BuildPreview:
    wid = normalize_world_id(world_id)
    step_name = str(step or "").strip()
    if step_name not in STEP_ORDER:
        raise ValueError(
            "unknown step %r: expected one of %s" % (step, ", ".join(STEP_ORDER))
        )
    world_dir = os.path.join(WORLDS_DIR, wid)
    district_name = resolve_district(wid, district)
    district_path = district_dir(wid, district_name)
    label: Optional[str] = None
    if step_name == "household" or STEP_SCOPE[step_name] == "house":
        label = _preview_house_label(wid, district_name, step_name, house)

    reads: List[Tuple[str, str]] = []
    writes: List[Tuple[str, str]] = []

    if step_name == "district":
        reads = [
            ("input", os.path.join(world_dir, "world.json")),
            ("input", os.path.join(district_path, "district.json")),
        ]
        writes = [
            ("output", os.path.join(district_path, "description.md")),
            ("output", os.path.join(district_path, "district.json")),
        ]
    elif step_name == "household":
        reads = [
            ("input", os.path.join(district_path, "district.json")),
            ("input", households_meta_path(wid, district_name)),
        ]
        writes = [
            ("output", house_file(wid, label, "household.json", district_name)),
            ("output", house_file(wid, label, "aligned_texts.json", district_name)),
            ("output", house_file(wid, label, "persona_provenance.json", district_name)),
            ("output", households_meta_path(wid, district_name)),
        ]
    else:  # home
        household_path = house_file(wid, label, "household.json", district_name)
        reads = [
            ("input", os.path.join(district_path, "district.json")),
            ("input", household_path),
        ]
        writes = [
            ("output", household_path),
            ("output", household_path + ".bak.<timestamp>"),
        ]

    read_refs = [
        ArtifactRef(path=os.path.abspath(path), exists=_is_file(path), role=role)
        for role, path in reads
    ]
    write_refs = [
        ArtifactRef(path=os.path.abspath(path), exists=_is_file(path), role=role)
        for role, path in writes
    ]
    overwrites = [ref.path for ref in write_refs if ref.exists]
    return BuildPreview(
        world_id=wid,
        step=step_name,
        district=district_name,
        house=label,
        reads=read_refs,
        writes=write_refs,
        overwrites=overwrites,
    )
