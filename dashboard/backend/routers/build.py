"""World lifecycle + stepwise build API.

Paths are defined WITHOUT the ``/api`` prefix - ``main.py`` mounts this router
with ``prefix="/api"``. The build *job* endpoint stays in ``routers/jobs.py``
(``kind="build"``); this module only creates/deletes worlds and inspects the
per-step build state so the UI can warn before re-running a stage.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from .. import artifacts, blocks, store, world_admin
from ..models import (
    ArtifactRead,
    ArtifactWriteRequest,
    ArtifactWriteResult,
    BuildPreview,
    BuildState,
    WorldCloneRequest,
    WorldCloneResult,
    WorldCreateRequest,
    WorldCreateResult,
    WorldDayBlocks,
    WorldDeleteResult,
)

router = APIRouter(tags=["build"])


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


@router.get("/worlds/{world}/build", response_model=BuildState)
def world_build_state(world: str) -> BuildState:
    """Per-step done/runnable/blocked status plus per-house completion."""
    try:
        state = world_admin.build_state(world)
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
) -> BuildPreview:
    """What a step reads and writes (paths + existence) before it is run."""
    try:
        return world_admin.build_preview(world, step, house)
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
