"""District presets and the district listing used by the build API.

Presets come from ``src/prompts/district_presets.json`` (owned by the research
repo). Only ``id`` / ``title`` / ``description`` are exposed - the long ``prompt``
text is deliberately never returned to the client. Listing reuses
:mod:`backend.world_admin` for names and paths so there is one source of truth.
"""

from __future__ import annotations

import json
import os
from typing import Any, List

from . import paths, world_admin
from .models import DistrictInfo, DistrictPreset

PRESETS_PATH = os.path.join(paths.SRC_DIR, "prompts", "district_presets.json")


def _read_json(path: str) -> Any:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def list_presets() -> List[DistrictPreset]:
    data = _read_json(PRESETS_PATH)
    if not isinstance(data, list):
        return []
    presets: List[DistrictPreset] = []
    for entry in data:
        if not isinstance(entry, dict) or not entry.get("id"):
            continue
        presets.append(
            DistrictPreset(
                id=str(entry["id"]),
                title=str(entry.get("title") or ""),
                description=str(entry.get("description") or ""),
            )
        )
    return presets


def _description(world_id: str, name: str) -> str:
    meta = world_admin.read_json(
        os.path.join(world_admin.district_dir(world_id, name), "district.json")
    )
    if isinstance(meta, dict) and isinstance(meta.get("description"), str):
        return meta["description"].strip()
    return ""


def list_districts(world_id: str) -> List[DistrictInfo]:
    infos: List[DistrictInfo] = []
    for name in world_admin.districts(world_id):
        description = _description(world_id, name)
        has_md = os.path.isfile(
            os.path.join(world_admin.district_dir(world_id, name), "description.md")
        )
        infos.append(
            DistrictInfo(
                name=name,
                description=description,
                house_count=world_admin.count_houses(world_id, name),
                has_description=bool(description) or has_md,
            )
        )
    return infos
