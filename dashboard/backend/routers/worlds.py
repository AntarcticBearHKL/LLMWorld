"""Catalog endpoints: runs, run metadata, worlds and household metadata."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException

from .. import store
from ..models import HouseholdInfo, RunInfo, RunMeta, RunSummary, WorldInfo

router = APIRouter(tags=["worlds"])


@router.get("/runs", response_model=List[RunInfo])
def get_runs() -> List[RunInfo]:
    return store.list_runs()


@router.get("/runs/summary", response_model=List[RunSummary])
def get_run_summaries(
    q: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[RunSummary]:
    return store.query_run_summaries(q, limit)


@router.get("/runs/default", response_model=RunSummary)
def get_default_run() -> RunSummary:
    item = store.default_run()
    if item is None:
        raise HTTPException(status_code=404, detail="no playable run found")
    return item


@router.get("/runs/{run}/meta", response_model=RunMeta)
def get_run_meta(run: str) -> RunMeta:
    meta = store.run_meta(run)
    if meta is None:
        raise HTTPException(status_code=404, detail="run not found: %s" % run)
    return RunMeta(**meta)


@router.get("/worlds", response_model=List[WorldInfo])
def get_worlds() -> List[WorldInfo]:
    return store.list_worlds()


@router.get("/worlds/{world}", response_model=WorldInfo)
def get_world(world: str) -> WorldInfo:
    info = store.world_info(world)
    if info is None:
        raise HTTPException(status_code=404, detail="world not found: %s" % world)
    return info


@router.get("/worlds/{world}/houses/{house}", response_model=HouseholdInfo)
def get_world_house(world: str, house: str) -> HouseholdInfo:
    if store.world_info(world) is None:
        raise HTTPException(status_code=404, detail="world not found: %s" % world)
    try:
        return store.household_info(world, house)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/worlds/{world}/districts/{district}/houses/{house}", response_model=HouseholdInfo)
def get_world_district_house(world: str, district: str, house: str) -> HouseholdInfo:
    """Household resolved inside one district (house ids repeat across districts)."""
    if store.world_info(world) is None:
        raise HTTPException(status_code=404, detail="world not found: %s" % world)
    try:
        return store.household_info(world, house, district)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
