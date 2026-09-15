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
IMPORT_WORLD_DIR = os.path.join(paths.LLMWORLD_ROOT, "import", "world")

POSTCODE = "3168"
DEFAULT_SEED = 42
DEFAULT_WORLD_CONFIG = "Melbourne"

STEP_ORDER: Tuple[str, ...] = ("types", "personas", "household", "assemble")
STEP_SCOPE: Dict[str, str] = {
    "types": "world",
    "personas": "house",
    "household": "house",
    "assemble": "house",
}

_WORLD_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
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


def district_dir(world_id: str) -> str:
    return os.path.join(resolve_world_dir(world_id), POSTCODE)


def world_meta_path(world_id: str) -> str:
    return os.path.join(resolve_world_dir(world_id), "world.json")


def types_path(world_id: str) -> str:
    return os.path.join(district_dir(world_id), "household_types.json")


def households_meta_path(world_id: str) -> str:
    return os.path.join(district_dir(world_id), "households.json")


def log_dir(world_id: str) -> str:
    return os.path.join(district_dir(world_id), "log")


def llm_trace_path(world_id: str, job_id: str) -> str:
    """Per-job LLM trace (JSONL) written by the build subprocess.

    Scoping the trace to a single job keeps every call attributable to the
    build step that made it without tagging anything inside ``src/``.
    """
    return os.path.join(log_dir(world_id), "llm_trace_%s.jsonl" % job_id)


def house_dir(world_id: str, house_label_value: str) -> str:
    return os.path.join(district_dir(world_id), house_label_value)


def house_file(world_id: str, house_label_value: str, name: str) -> str:
    return os.path.join(house_dir(world_id, house_label_value), name)


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


def household_type_count(world_id: str) -> int:
    data = read_json(types_path(world_id))
    entries = data.get("household_types") if isinstance(data, dict) else data
    return len(entries) if isinstance(entries, list) else 0


def list_house_labels(world_id: str) -> List[str]:
    labels = set()
    district = district_dir(world_id)
    if os.path.isdir(district):
        try:
            children = os.listdir(district)
        except OSError:
            children = []
        for name in children:
            if _HOUSE_RE.match(name) and os.path.isdir(os.path.join(district, name)):
                labels.add(name)
    for index in range(household_type_count(world_id)):
        labels.add(house_label(index))
    return sorted(labels)


def resolve_house_label(world_id: str, house: Any) -> str:
    """Resolve a house selector ('house_0001', '0' or None) to a house label.

    None selects the first known house, or ``house_0001`` when the world has
    none yet so the step itself fails with a readable reason.
    """
    if house is None or str(house).strip() == "":
        labels = list_house_labels(world_id)
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


def member_count(world_id: str, house_label_value: Optional[str]) -> Optional[int]:
    if not house_label_value:
        return None
    data = read_json(house_file(world_id, house_label_value, "aligned_texts.json"))
    return len(data) if isinstance(data, list) else None


def _world_config_name(world_id: str) -> str:
    meta = read_json(world_meta_path(world_id))
    if isinstance(meta, dict) and meta.get("world_config"):
        return str(meta["world_config"])
    return DEFAULT_WORLD_CONFIG


def _aggregate(
    step: str, houses: List[HouseStepStatus], empty_reason: str
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
        scope="house",
        done=done,
        runnable=runnable,
        blocked_reason=reason,
        houses=houses,
    )


def build_state(world_id: str) -> BuildState:
    wid = normalize_world_id(world_id)
    world_dir = os.path.join(WORLDS_DIR, wid)
    exists = os.path.isdir(world_dir)
    district = os.path.join(world_dir, POSTCODE)

    types_done = _is_file(os.path.join(district, "household_types.json"))
    type_count = household_type_count(wid) if types_done else 0
    labels = list_house_labels(wid) if exists else []

    assembled: set = set()
    meta = read_json(os.path.join(district, "households.json"))
    if isinstance(meta, dict) and isinstance(meta.get("households"), list):
        for entry in meta["households"]:
            if isinstance(entry, dict) and entry.get("house_id"):
                assembled.add(str(entry["house_id"]))

    persona_houses: List[HouseStepStatus] = []
    household_houses: List[HouseStepStatus] = []
    assemble_houses: List[HouseStepStatus] = []
    for label in labels:
        raw_index = house_index_from(label)
        index = 0 if raw_index is None else raw_index

        personas_done = _is_file(house_file(wid, label, "aligned_texts.json"))
        if not types_done:
            personas_runnable = False
            personas_reason = "household_types.json missing (run 'types' first)"
        elif type_count and index >= type_count:
            personas_runnable = False
            personas_reason = "house index %d is out of range (types=%d)" % (index, type_count)
        else:
            personas_runnable = True
            personas_reason = None
        persona_houses.append(
            HouseStepStatus(
                house=label,
                done=personas_done,
                runnable=personas_runnable,
                blocked_reason=personas_reason,
            )
        )

        household_done = _is_file(house_file(wid, label, "household.json"))
        household_houses.append(
            HouseStepStatus(
                house=label,
                done=household_done,
                runnable=personas_done,
                blocked_reason=None if personas_done else "aligned_texts.json missing (run 'personas' first)",
            )
        )

        assemble_done = (
            household_done
            and _is_file(house_file(wid, label, "personas.json"))
            and label in assembled
        )
        assemble_houses.append(
            HouseStepStatus(
                house=label,
                done=assemble_done,
                runnable=household_done,
                blocked_reason=None if household_done else "household.json missing (run 'household' first)",
            )
        )

    steps = [
        BuildStepStatus(
            step="types",
            scope="world",
            done=types_done,
            runnable=exists,
            blocked_reason=None if exists else "world directory is missing",
        ),
        _aggregate("personas", persona_houses, "no households yet; run 'types' first"),
        _aggregate("household", household_houses, "no households yet; run 'personas' first"),
        _aggregate("assemble", assemble_houses, "no households yet; run 'household' first"),
    ]

    return BuildState(
        world_id=wid,
        world_dir=os.path.abspath(world_dir),
        exists=exists,
        houses=labels,
        steps=steps,
    )


def build_preview(world_id: str, step: str, house: Any = None) -> BuildPreview:
    wid = normalize_world_id(world_id)
    step_name = str(step or "").strip()
    if step_name not in STEP_ORDER:
        raise ValueError(
            "unknown step %r: expected one of %s" % (step, ", ".join(STEP_ORDER))
        )
    world_dir = os.path.join(WORLDS_DIR, wid)
    district = os.path.join(world_dir, POSTCODE)
    label = resolve_house_label(wid, house) if step_name != "types" else None

    reads: List[Tuple[str, str]] = []
    writes: List[Tuple[str, str]] = []

    if step_name == "types":
        config = _world_config_name(wid)
        reads = [
            ("input", os.path.join(world_dir, "world.json")),
            ("input", os.path.join(IMPORT_WORLD_DIR, config, POSTCODE, "info.md")),
        ]
        writes = [("output", os.path.join(district, "household_types.json"))]
    elif step_name == "personas":
        reads = [("input", os.path.join(district, "household_types.json"))]
        writes = [
            ("output", house_file(wid, label, "aligned_texts.json")),
            ("output", house_file(wid, label, "persona_provenance.json")),
        ]
    elif step_name == "household":
        reads = [
            ("input", os.path.join(district, "household_types.json")),
            ("input", house_file(wid, label, "aligned_texts.json")),
            ("input", house_file(wid, label, "persona_provenance.json")),
        ]
        writes = [
            ("output", house_file(wid, label, "household.json")),
            ("output", house_file(wid, label, "persona_rows.json")),
        ]
    else:
        reads = [
            ("input", house_file(wid, label, "household.json")),
            ("input", house_file(wid, label, "aligned_texts.json")),
            ("input", house_file(wid, label, "persona_provenance.json")),
            ("input", os.path.join(district, "household_types.json")),
            ("input", os.path.join(district, "households.json")),
        ]
        writes = [
            ("output", house_file(wid, label, "household.json")),
            ("output", house_file(wid, label, "personas.json")),
            ("output", os.path.join(district, "households.json")),
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
        house=label,
        reads=read_refs,
        writes=write_refs,
        overwrites=overwrites,
    )
