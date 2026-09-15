"""Spacetimes: a simulation run pinned to a world, with its own policy/news/days.

A spacetime is a directory under ``output/simulation/<name>/`` plus a manifest
(``<name>/spacetime.json``) recording what makes it that spacetime: the world it
belongs to, its start date, day count, policy, and news/events. The manifest is
what lets the UI say "this spacetime used policy X and these notices", and its
existence is what freezes a world's households (a world with >=1 spacetime is
read-only at the household level).
"""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import paths
from .models import Spacetime

MANIFEST_NAME = "spacetime.json"
TRASH_DIR = os.path.join(paths.OUTPUT_DIR, "_trash")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def normalize_name(name: str) -> str:
    text = str(name or "").strip()
    if not text or not _NAME_RE.match(text) or text in (".", ".."):
        raise ValueError(
            "invalid spacetime name %r: use letters, digits, '.', '_' or '-'" % (name,)
        )
    return text


def run_dir(name: str) -> str:
    return os.path.join(paths.SIMULATION_DIR, normalize_name(name))


def manifest_path(name: str) -> str:
    return os.path.join(run_dir(name), MANIFEST_NAME)


def exists(name: str) -> bool:
    try:
        return os.path.isdir(run_dir(name))
    except ValueError:
        return False


def _run_dates(dir_path: str) -> List[str]:
    try:
        names = os.listdir(dir_path)
    except OSError:
        return []
    return sorted(
        entry for entry in names
        if _DATE_RE.match(entry) and os.path.isdir(os.path.join(dir_path, entry))
    )


def _house_count(dir_path: str) -> int:
    dates = _run_dates(dir_path)
    if not dates:
        return 0
    day = os.path.join(dir_path, dates[0])
    try:
        return sum(1 for entry in os.listdir(day) if entry.startswith("house_"))
    except OSError:
        return 0


def read(name: str) -> Optional[Spacetime]:
    try:
        run = normalize_name(name)
    except ValueError:
        return None
    dir_path = os.path.join(paths.SIMULATION_DIR, run)
    if not os.path.isdir(dir_path):
        return None
    raw: Dict[str, Any] = {}
    manifest = os.path.join(dir_path, MANIFEST_NAME)
    has_manifest = os.path.isfile(manifest)
    if has_manifest:
        try:
            with open(manifest, encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict):
                raw = loaded
        except (OSError, ValueError):
            raw = {}
    dates = _run_dates(dir_path)
    return Spacetime(
        name=run,
        world=str(raw.get("world") or run),
        start_date=raw.get("start_date") or (dates[0] if dates else None),
        days=int(raw.get("days") or len(dates) or 1),
        policy=raw.get("policy"),
        events=[str(item) for item in raw.get("events") or []],
        notices=[str(item) for item in raw.get("notices") or []],
        seed=raw.get("seed"),
        created_at=raw.get("created_at"),
        status=str(raw.get("status") or "created"),
        has_manifest=has_manifest,
        date_count=len(dates),
        house_count=_house_count(dir_path),
        latest_mtime=os.path.getmtime(dir_path),
    )


def write(name: str, config: Dict[str, Any]) -> Spacetime:
    run = normalize_name(name)
    dir_path = os.path.join(paths.SIMULATION_DIR, run)
    os.makedirs(dir_path, exist_ok=True)
    manifest = os.path.join(dir_path, MANIFEST_NAME)
    existing: Dict[str, Any] = {}
    if os.path.isfile(manifest):
        try:
            with open(manifest, encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict):
                existing = loaded
        except (OSError, ValueError):
            existing = {}
    record = {
        "spacetime_version": 1,
        "name": run,
        "world": str(config.get("world") or existing.get("world") or run),
        "start_date": config.get("start_date") or existing.get("start_date"),
        "days": int(config.get("days") or existing.get("days") or 1),
        "policy": config.get("policy") if "policy" in config else existing.get("policy"),
        "events": list(config.get("events") or existing.get("events") or []),
        "notices": list(config.get("notices") or existing.get("notices") or []),
        "seed": config.get("seed") if "seed" in config else existing.get("seed"),
        "status": str(config.get("status") or existing.get("status") or "created"),
        "created_at": existing.get("created_at") or datetime.now().isoformat(timespec="seconds"),
    }
    with open(manifest, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    result = read(run)
    if result is None:
        raise ValueError("could not create spacetime %r" % (run,))
    return result


def list_for_world(world: str) -> List[Spacetime]:
    """Manifests whose ``world`` is *world*, plus legacy runs named after it."""
    if not os.path.isdir(paths.SIMULATION_DIR):
        return []
    items: List[Spacetime] = []
    try:
        names = sorted(os.listdir(paths.SIMULATION_DIR))
    except OSError:
        return []
    for name in names:
        if not os.path.isdir(os.path.join(paths.SIMULATION_DIR, name)):
            continue
        item = read(name)
        if item is None:
            continue
        if item.world == world or name == world:
            items.append(item)
    items.sort(key=lambda entry: entry.latest_mtime or 0.0, reverse=True)
    return items


def worlds_with_spacetimes() -> Dict[str, List[str]]:
    """``{world: [spacetime names]}`` for every run that declares a world."""
    mapping: Dict[str, List[str]] = {}
    if not os.path.isdir(paths.SIMULATION_DIR):
        return mapping
    try:
        names = sorted(os.listdir(paths.SIMULATION_DIR))
    except OSError:
        return mapping
    for name in names:
        if not os.path.isdir(os.path.join(paths.SIMULATION_DIR, name)):
            continue
        item = read(name)
        if item is None:
            continue
        mapping.setdefault(item.world, []).append(item.name)
    return mapping


def delete(name: str, permanent: bool = False) -> Dict[str, Any]:
    run = normalize_name(name)
    dir_path = os.path.join(paths.SIMULATION_DIR, run)
    if not os.path.isdir(dir_path):
        return {"name": run, "existed": False, "deleted": False, "moved_to": None}
    if permanent:
        shutil.rmtree(dir_path)
        return {"name": run, "existed": True, "deleted": True, "moved_to": None}
    os.makedirs(TRASH_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(TRASH_DIR, "%s_%s" % (run, stamp))
    bump = 0
    while os.path.exists(dest):
        bump += 1
        dest = os.path.join(TRASH_DIR, "%s_%s_%d" % (run, stamp, bump))
    shutil.move(dir_path, dest)
    return {"name": run, "existed": True, "deleted": True, "moved_to": os.path.abspath(dest)}
