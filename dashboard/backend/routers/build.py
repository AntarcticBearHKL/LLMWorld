"""World lifecycle + stepwise build API.

Paths are defined WITHOUT the ``/api`` prefix - ``main.py`` mounts this router
with ``prefix="/api"``. The build *job* endpoint stays in ``routers/jobs.py``
(``kind="build"``); this module only creates/deletes worlds and inspects the
per-step build state so the UI can warn before re-running a stage.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from .. import artifacts, blocks, districts, store, world_admin
from ..models import (
    ArtifactRead,
    ArtifactWriteRequest,
    ArtifactWriteResult,
    BuildPreview,
    BuildState,
    DistrictCopyRequest,
    DistrictCreateRequest,
    DistrictCreateResult,
    DistrictDeleteResult,
    DistrictInfo,
    DistrictPatchRequest,
    DistrictPreset,
    WorldCloneRequest,
    WorldCloneResult,
    WorldCreateRequest,
    WorldCreateResult,
    WorldDayBlocks,
    WorldDeleteResult,
)

router = APIRouter(tags=["build"])


def _ensure_world(world: str) -> None:
    try:
        exists = world_admin.world_exists(world)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not exists:
        raise HTTPException(status_code=404, detail="world not found: %s" % world)


def _district_info(world: str, name: str) -> DistrictInfo:
    return DistrictInfo(**world_admin.district_record(world, name))


@router.post("/worlds", response_model=WorldCreateResult)
def worlds_create(req: WorldCreateRequest) -> WorldCreateResult:
    """Create an EMPTY world (scaffolding only, zero LLM calls)."""
    try:
        result = world_admin.create_world(req.world_id, req.world_config, req.seed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.invalidate_catalog()
    return WorldCreateResult(**result)


@router.delete("/worlds/{world}", response_model=WorldDeleteResult)
def worlds_delete(world: str, permanent: bool = False) -> WorldDeleteResult:
    """Delete a world; default moves it to output/_trash/ (recoverable)."""
    try:
        result = world_admin.delete_world(world, permanent)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.invalidate_catalog()
    return WorldDeleteResult(**result)


@router.get("/district-presets", response_model=List[DistrictPreset])
def district_presets() -> List[DistrictPreset]:
    """Wizard presets for the district-description step (never the prompt text)."""
    return districts.list_presets()


@router.get("/worlds/{world}/districts", response_model=List[DistrictInfo])
def world_districts_list(world: str) -> List[DistrictInfo]:
    """Districts of a world with description presence and household counts."""
    _ensure_world(world)
    try:
        return districts.list_districts(world)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/worlds/{world}/districts", response_model=DistrictCreateResult)
def world_districts_create(world: str, req: DistrictCreateRequest) -> DistrictCreateResult:
    """Create a district locally (zero LLM); idempotent like POST /worlds."""
    _ensure_world(world)
    try:
        result = world_admin.create_district(world, req.name, req.description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.invalidate_catalog()
    info = _district_info(world, result["name"])
    return DistrictCreateResult(**info.model_dump(), created=bool(result.get("created")))


@router.delete(
    "/worlds/{world}/districts/{district}", response_model=DistrictDeleteResult
)
def world_districts_delete(
    world: str, district: str, permanent: bool = False
) -> DistrictDeleteResult:
    """Delete a district; default moves it to output/_trash/ (recoverable)."""
    _ensure_world(world)
    try:
        result = world_admin.delete_district(world, district, permanent)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.invalidate_catalog()
    return DistrictDeleteResult(**result)


@router.patch("/worlds/{world}/districts/{district}", response_model=DistrictInfo)
def world_districts_patch(
    world: str, district: str, req: DistrictPatchRequest
) -> DistrictInfo:
    """Edit an unlocked district: rename it and/or replace its description."""
    _ensure_world(world)
    try:
        record = world_admin.edit_district(world, district, req.name, req.description)
    except (world_admin.DistrictLockedError, world_admin.DistrictConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.invalidate_catalog()
    return DistrictInfo(**record)


@router.post("/worlds/{world}/districts/{district}/lock", response_model=DistrictInfo)
def world_districts_lock(world: str, district: str) -> DistrictInfo:
    """Lock a district (one-way, idempotent). There is no unlock endpoint."""
    _ensure_world(world)
    try:
        record = world_admin.lock_district(world, district)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.invalidate_catalog()
    return DistrictInfo(**record)


@router.post("/worlds/{world}/districts/{district}/copy", response_model=DistrictInfo)
def world_districts_copy(
    world: str, district: str, req: Optional[DistrictCopyRequest] = None
) -> DistrictInfo:
    """Copy a district's brief into a NEW (initialized, unlocked) district."""
    _ensure_world(world)
    requested = req.name if req is not None else None
    try:
        record = world_admin.copy_district(world, district, requested)
    except (world_admin.DistrictLockedError, world_admin.DistrictConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.invalidate_catalog()
    return DistrictInfo(**record)


@router.get("/worlds/{world}/build", response_model=BuildState)
def world_build_state(world: str, district: Optional[str] = None) -> BuildState:
    """Per-step done/runnable/blocked status for one district's households."""
    try:
        state = world_admin.build_state(world, district)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not state.exists:
        raise HTTPException(status_code=404, detail="world not found: %s" % world)
    return state


@router.get("/worlds/{world}/build/steps/{step}/preview", response_model=BuildPreview)
def world_build_preview(
    world: str,
    step: str,
    house: Optional[str] = None,
    district: Optional[str] = None,
) -> BuildPreview:
    """What a step reads and writes (paths + existence) before it is run."""
    try:
        return world_admin.build_preview(world, step, house, district)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/worlds/{world}/artifact", response_model=ArtifactRead)
def world_artifact_get(world: str, path: str = Query(..., min_length=1)) -> ArtifactRead:
    """Read a world artifact; JSON files are parsed into ``data``."""
    try:
        return artifacts.read_artifact(world, path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/worlds/{world}/artifact", response_model=ArtifactWriteResult)
def world_artifact_put(world: str, req: ArtifactWriteRequest) -> ArtifactWriteResult:
    """Overwrite a world artifact after a ``.bak.<ts>`` copy; JSON is validated."""
    try:
        return artifacts.write_artifact(world, req.path, req.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/worlds/{world}/clone", response_model=WorldCloneResult)
def world_clone(world: str, req: WorldCloneRequest) -> WorldCloneResult:
    """Deep-copy a world (households included) into a new draft world."""
    try:
        result = world_admin.clone_world(world, req.new_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.invalidate_catalog()
    return WorldCloneResult(**result)


@router.get("/worlds/{world}/runs/{run}/days/{date}/blocks", response_model=WorldDayBlocks)
def world_day_blocks(
    world: str,
    run: str,
    date: str,
    policy: str = "baseline",
) -> WorldDayBlocks:
    """One day of a spacetime aggregated into the world's blocks."""
    try:
        return blocks.build_day_blocks(world, run, date, policy)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
