"""World lifecycle service for the LLMWorld Research Console.

Owns the filesystem side of a world: creating an EMPTY world (scaffolding only,
zero LLM calls), resolving and deleting world directories, the district
lifecycle (uninitialized -> initialized -> locked, DESIGN.md §18) and reporting
per-step build progress for the world-generation stages. Nothing here calls the
LLM or run.py - build jobs are still executed by :mod:`backend.jobs`.

District lifecycle invariants
-----------------------------
* ``status`` is always DERIVED from files on disk - it is never persisted:
  no description -> ``uninitialized``; description but no lock marker ->
  ``initialized``; lock marker present -> ``locked``.
* The lock is a marker file OUTSIDE ``district.json`` (so a pipeline rewrite of
  the brief can never clear it). It travels with the directory on rename.
* The lock is one-way: there is no unlock path anywhere in this module.
* The ``household`` and ``home`` build steps are gated on the lock; both
  :func:`build_state` and :mod:`backend.build` use :data:`LOCK_REQUIRED_REASON`
  so the Steps sheet and the job HTTP API refuse with the same wording.
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
    DistrictStatus,
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

#: Steps refused until the district is locked (DESIGN.md §18.3).
LOCKED_STEPS: Tuple[str, ...] = ("household", "home")
#: The one and only wording for the gate: the state reporter and the build-job
#: argv builder must refuse with identical text (DESIGN.md §18.3).
LOCK_REQUIRED_REASON = (
    "Lock the district first — households can only be generated for a locked district."
)

#: ``<district>/.locked`` - the persisted, one-way lock marker; always read and
#: written through the helpers below so every caller agrees.
LOCK_MARKER_NAME = ".locked"
#: district.json keys a copy carries over (the brief, never the households).
COPY_KEYS: Tuple[str, ...] = ("location", "economic_level", "postcode")

_WORLD_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_DISTRICT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_RESERVED_DISTRICT_NAMES = frozenset({"log"})
_HOUSE_RE = re.compile(r"^house_(\d+)$")


class DistrictConflictError(ValueError):
    pass


class DistrictLockedError(ValueError):
    pass


def district_status(has_description: bool, locked: bool) -> DistrictStatus:
    if locked:
        return "locked"
    return "initialized" if has_description else "uninitialized"


def _gw() -> Any:
    import generate_world

    return generate_world


def read_json(path: str) -> Any:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        raise ValueError("%s exists but is not readable JSON: %s" % (path, exc)) from exc


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def _read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


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


def district_meta_path(world_id: str, district: Optional[str] = None) -> str:
    return os.path.join(district_dir(world_id, district), "district.json")


def description_md_path(world_id: str, district: Optional[str] = None) -> str:
    return os.path.join(district_dir(world_id, district), "description.md")


def lock_marker_path(world_id: str, district: Optional[str] = None) -> str:
    return os.path.join(district_dir(world_id, district), LOCK_MARKER_NAME)


def read_lock(world_id: str, district: Optional[str] = None) -> Optional[str]:
    """The lock timestamp, or ``None`` when the district is not locked."""
    try:
        with open(lock_marker_path(world_id, district), encoding="utf-8") as fh:
            stamp = fh.read().strip()
    except OSError:
        return None
    return stamp or None


def is_locked(world_id: str, district: Optional[str] = None) -> bool:
    return _is_file(lock_marker_path(world_id, district))


def write_lock(world_id: str, district: Optional[str] = None) -> str:
    """Write the lock marker; idempotent, an existing timestamp is preserved."""
    if is_locked(world_id, district):
        return read_lock(world_id, district) or ""
    stamp = datetime.now().isoformat(timespec="seconds")
    path = lock_marker_path(world_id, district)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(stamp + "\n")
    return stamp


def district_description(world_id: str, district: Optional[str] = None) -> str:
    meta = read_json(district_meta_path(world_id, district))
    if isinstance(meta, dict) and isinstance(meta.get("description"), str):
        return meta["description"].strip()
    return ""


def district_has_description(world_id: str, district: Optional[str] = None) -> bool:
    """Existing meaning, unchanged: brief text present, or ``description.md``."""
    if district_description(world_id, district):
        return True
    return _is_file(description_md_path(world_id, district))


def district_record(world_id: str, district: str) -> Dict[str, Any]:
    """The one place a DistrictInfo payload is assembled (list + every mutation)."""
    wid = normalize_world_id(world_id)
    name = normalize_district(district)
    has_description = district_has_description(wid, name)
    locked = is_locked(wid, name)
    return {
        "name": name,
        "description": district_description(wid, name),
        "house_count": count_houses(wid, name),
        "has_description": has_description,
        "status": district_status(has_description, locked),
        "locked_at": read_lock(wid, name),
    }


def lock_district(world_id: str, name: str) -> Dict[str, Any]:
    """Lock a district (one-way, idempotent) and return its record."""
    wid = normalize_world_id(world_id)
    district = normalize_district(name)
    if not os.path.isdir(os.path.join(WORLDS_DIR, wid)):
        raise ValueError("world not found: %s" % wid)
    if not os.path.isdir(district_dir(wid, district)):
        raise ValueError("district not found: %s" % district)
    write_lock(wid, district)
    return district_record(wid, district)


def _district_taken(world_id: str, name: str) -> bool:
    return name in districts(world_id) or os.path.exists(
        os.path.join(resolve_world_dir(world_id), name)
    )


def _copy_name(world_id: str, source: str, requested: Optional[str]) -> str:
    if requested is not None and str(requested).strip():
        candidate = normalize_district(requested)
        if _district_taken(world_id, candidate):
            raise DistrictConflictError("district already exists: %s" % candidate)
        return candidate
    candidate = "%s_copy" % source
    suffix = 1
    while _district_taken(world_id, candidate):
        suffix += 1
        candidate = "%s_copy%d" % (source, suffix)
    return candidate


def copy_district(
    world_id: str, source: str, name: Optional[str] = None
) -> Dict[str, Any]:
    """Copy a district's BRIEF into a NEW district - zero household data.

    The copy carries the source's description, location, economic level and
    postcode, is ``initialized`` (it has a description) and is never locked.
    """
    wid = normalize_world_id(world_id)
    src = normalize_district(source)
    if not os.path.isdir(os.path.join(WORLDS_DIR, wid)):
        raise ValueError("world not found: %s" % wid)
    src_dir = district_dir(wid, src)
    if not os.path.isdir(src_dir):
        raise ValueError("district not found: %s" % src)

    target = _copy_name(wid, src, name)
    description = district_description(wid, src)
    if not description:
        description = _read_text(description_md_path(wid, src)).strip()

    create_district(wid, target, description or None)

    source_meta = read_json(district_meta_path(wid, src))
    new_meta: Dict[str, Any] = {
        "name": target,
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "copied_from": src,
    }
    if isinstance(source_meta, dict):
        for key in COPY_KEYS:
            if key in source_meta:
                new_meta[key] = source_meta[key]
    _write_json(district_meta_path(wid, target), new_meta)

    if description:
        _write_text(description_md_path(wid, target), description + "\n")
    return district_record(wid, target)


def rename_district(world_id: str, name: str, new_name: str) -> Dict[str, Any]:
    """Move the district directory and keep world.json + district.json in step."""
    wid = normalize_world_id(world_id)
    old = normalize_district(name)
    new = normalize_district(new_name)
    if old == new:
        return district_record(wid, old)
    if is_locked(wid, old):
        raise DistrictLockedError(
            "district %s is locked; it can no longer be renamed" % old
        )
    world_dir = resolve_world_dir(wid)
    old_dir = os.path.join(world_dir, old)
    new_dir = os.path.join(world_dir, new)
    if not os.path.isdir(old_dir):
        raise ValueError("district not found: %s" % old)
    if os.path.exists(new_dir):
        raise DistrictConflictError("district already exists: %s" % new)

    try:
        shutil.move(old_dir, new_dir)
    except OSError as exc:
        raise ValueError(
            "could not rename district %s -> %s: %s" % (old, new, exc)
        ) from exc

    _sync_district_meta(wid, new)
    _rename_in_world_meta(wid, old, new)
    return district_record(wid, new)


def _sync_district_meta(world_id: str, name: str) -> None:
    path = district_meta_path(world_id, name)
    meta = read_json(path)
    if not isinstance(meta, dict):
        return
    meta["name"] = name
    meta["postcode"] = name
    location = meta.get("location")
    if isinstance(location, dict):
        location["district"] = name
    _write_json(path, meta)


def _rename_in_world_meta(world_id: str, old: str, new: str) -> None:
    path = world_meta_path(world_id)
    meta = read_json(path)
    if not isinstance(meta, dict) or not isinstance(meta.get("districts"), list):
        return
    changed = False
    for index, entry in enumerate(meta["districts"]):
        if isinstance(entry, str):
            if entry == old:
                meta["districts"][index] = {"name": new, "postcode": new}
                changed = True
            continue
        if not isinstance(entry, dict) or _district_entry_name(entry) != old:
            continue
        entry["name"] = new
        if "postcode" in entry:
            entry["postcode"] = new
        changed = True
    if changed:
        _write_json(path, meta)


def _write_description(world_id: str, name: str, text: str) -> None:
    value = text.strip()
    meta = read_json(district_meta_path(world_id, name))
    if not isinstance(meta, dict):
        meta = {"name": name}
    meta["name"] = name
    meta["description"] = value
    meta["description_updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _write_json(district_meta_path(world_id, name), meta)

    md_path = description_md_path(world_id, name)
    if value:
        _write_text(md_path, value + "\n")
    elif os.path.isfile(md_path):
        os.remove(md_path)


def edit_district(
    world_id: str,
    name: str,
    new_name: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """PATCH an unlocked district: rename it and/or replace its description."""
    wid = normalize_world_id(world_id)
    current = normalize_district(name)
    if not os.path.isdir(district_dir(wid, current)):
        raise ValueError("district not found: %s" % current)
    if is_locked(wid, current):
        raise DistrictLockedError(
            "district %s is locked; its name and description can no longer be edited"
            % current
        )

    target = current
    if new_name is not None and str(new_name).strip():
        target = normalize_district(new_name)
        if target != current:
            rename_district(wid, current, target)
    if description is not None:
        _write_description(wid, target, str(description))
    return district_record(wid, target)


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
    step: str,
    scope: str,
    houses: List[HouseStepStatus],
    empty_reason: str,
    runnable_when_empty: bool = False,
) -> BuildStepStatus:
    """Zero houses is an entry point for ``household`` and a dead end for ``home`` (§18.3)."""
    done = bool(houses) and all(item.done for item in houses)
    runnable = any(item.runnable for item in houses)
    reason: Optional[str] = None
    if not houses:
        runnable = runnable_when_empty
        reason = None if runnable_when_empty else empty_reason
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


def _household_status(path: str) -> Tuple[bool, str]:
    """(done, stage): a household is done only once its ``members`` list is non-empty."""
    data = read_json(path)
    if not isinstance(data, dict):
        return False, "missing"
    members = data.get("members")
    if isinstance(members, list) and members:
        return True, "composed"
    return False, "described"


def build_state(world_id: str, district: Optional[str] = None) -> BuildState:
    wid = normalize_world_id(world_id)
    world_dir = os.path.join(WORLDS_DIR, wid)
    exists = os.path.isdir(world_dir)
    district_name = resolve_district(wid, district)
    district_path = district_dir(wid, district_name)

    description_done = _is_file(os.path.join(district_path, "description.md"))
    labels = list_house_labels(wid, district_name) if exists else []
    gate_reason = None if is_locked(wid, district_name) else LOCK_REQUIRED_REASON

    household_houses: List[HouseStepStatus] = []
    home_houses: List[HouseStepStatus] = []
    for label in labels:
        household_path = house_file(wid, label, "household.json", district_name)
        household_exists = _is_file(household_path)
        household_done, household_stage = _household_status(household_path)
        household_houses.append(
            HouseStepStatus(
                house=label,
                done=household_done,
                stage=household_stage,
                runnable=description_done and gate_reason is None,
                blocked_reason=gate_reason
                or (
                    None
                    if description_done
                    else "district description missing (run 'district' first)"
                ),
            )
        )

        home_done = household_exists and _house_has_home(household_path)
        home_houses.append(
            HouseStepStatus(
                house=label,
                done=home_done,
                runnable=household_exists and gate_reason is None,
                blocked_reason=gate_reason
                or (
                    None
                    if household_exists
                    else "household.json missing (run 'household' first)"
                ),
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
        _aggregate(
            "household",
            "district",
            household_houses,
            gate_reason or "no households yet; run 'household' first",
            runnable_when_empty=description_done and gate_reason is None,
        ),
        _aggregate(
            "home",
            "house",
            home_houses,
            gate_reason or "no households yet; run 'household' first",
        ),
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
