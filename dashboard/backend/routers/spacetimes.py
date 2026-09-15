"""Spacetime API: list / create / delete the simulation runs of a world.

Creating a spacetime writes its manifest and queues the matching simulate job;
its configuration (policy / news / days) is fixed at creation, so "changing" a
spacetime means creating another one. Paths are defined WITHOUT the ``/api``
prefix - ``main.py`` mounts this router with ``prefix="/api"``.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from .. import jobs, spacetimes, world_admin
from ..models import JobRequest, Spacetime, SpacetimeCreate, SpacetimeDeleteResult

router = APIRouter(tags=["spacetimes"])


@router.get("/worlds/{world}/spacetimes", response_model=List[Spacetime])
def spacetimes_list(world: str) -> List[Spacetime]:
    """Every spacetime of a world (manifest-backed or a legacy run named after it)."""
    try:
        wid = world_admin.normalize_world_id(world)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return spacetimes.list_for_world(wid)


@router.post("/worlds/{world}/spacetimes", response_model=Spacetime)
def spacetime_create(world: str, req: SpacetimeCreate) -> Spacetime:
    """Create a spacetime: persist its manifest, then queue the simulation job."""
    try:
        wid = world_admin.normalize_world_id(world)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not world_admin.world_exists(wid):
        raise HTTPException(status_code=404, detail="world not found: %s" % wid)
    if spacetimes.exists(req.name):
        raise HTTPException(
            status_code=400, detail="spacetime already exists: %s" % req.name
        )

    try:
        spacetimes.write(req.name, {
            "world": wid,
            "start_date": req.start_date,
            "days": req.days,
            "policy": req.policy,
            "events": req.events,
            "notices": req.notices,
            "seed": req.seed,
            "status": "queued",
        })
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    request = JobRequest(
        kind="simulate",
        world=wid,
        env=req.name,
        date=req.start_date,
        days=req.days,
        policy=req.policy,
        event_template=list(req.events),
        community_notice=list(req.notices),
        seed=req.seed,
        confirm=True,
    )
    try:
        jobs.create_job(request)
    except ValueError as exc:
        spacetimes.write(req.name, {"status": "failed"})
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    created = spacetimes.read(req.name)
    if created is None:
        raise HTTPException(status_code=500, detail="spacetime manifest vanished")
    return created


@router.delete("/spacetimes/{name}", response_model=SpacetimeDeleteResult)
def spacetime_delete(name: str, permanent: bool = False) -> SpacetimeDeleteResult:
    """Delete a spacetime; default moves it to output/_trash/ (recoverable)."""
    try:
        result = spacetimes.delete(name, permanent)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SpacetimeDeleteResult(**result)
