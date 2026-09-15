"""Replay endpoints: day payloads, point-in-time snapshots and stage logs."""

from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from .. import derive
from ..models import DayReplay, Snapshot, StagePayload
from ..paths import SIMULATION_DIR

from analyze import dataset  # noqa: E402  (paths.py put src/ on sys.path)

router = APIRouter(tags=["replay"])


@router.get("/runs/{run}/days/{date}/houses/{house}", response_model=DayReplay)
def get_day_replay(
    run: str,
    date: str,
    house: str,
    policy: str = "baseline",
) -> DayReplay:
    try:
        return derive.build_day_replay(run, date, house, policy)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/replay", response_model=Snapshot)
def get_snapshot(
    run: str,
    date: str,
    minute: int = 0,
    policy: str = "baseline",
) -> Snapshot:
    try:
        return derive.build_snapshot(run, date, minute, policy)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/runs/{run}/days/{date}/houses/{house}/stages/{member}",
    response_model=StagePayload,
)
def get_stages(run: str, date: str, house: str, member: str) -> StagePayload:
    try:
        return derive.build_stages(run, date, house, member)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/runs/{run}/days/{date}/houses/{house}/policies")
def get_policies(run: str, date: str, house: str) -> Dict[str, Any]:
    house_dir = os.path.join(SIMULATION_DIR, run, date, house)
    if not os.path.isdir(house_dir):
        raise HTTPException(
            status_code=404,
            detail="house dir not found: %s/%s/%s" % (run, date, house),
        )
    return {"policies": dataset.discover_policy_tags(house_dir)}
