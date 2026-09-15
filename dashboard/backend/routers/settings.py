"""Dashboard settings API.

Paths are defined WITHOUT the ``/api`` prefix - ``main.py`` mounts this router
with ``prefix="/api"``. A change is persisted to ``settings.json`` and injected
into the next job as ``LLMWORLD_*`` env vars, so it takes effect immediately for
newly spawned jobs.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import settings
from ..models import Settings, SettingsUpdate

router = APIRouter(tags=["settings"])


@router.get("/settings", response_model=Settings)
def get_settings() -> Settings:
    """Current model / temperature / token / retry knobs."""
    return settings.describe()


@router.put("/settings", response_model=Settings)
def put_settings(req: SettingsUpdate) -> Settings:
    """Persist the provided knobs; omitted fields keep their current value."""
    try:
        return Settings(**settings.save_settings(req.model_dump(exclude_none=True)))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
