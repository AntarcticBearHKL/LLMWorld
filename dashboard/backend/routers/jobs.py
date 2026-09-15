"""Job API router: estimates, creation, status, logs and SSE streaming.

Paths are defined WITHOUT the ``/api`` prefix - ``main.py`` mounts this router
with ``prefix="/api"``.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, AsyncIterator, Dict, List

from fastapi import APIRouter, HTTPException, Query
from sse_starlette.sse import EventSourceResponse

from ..jobs import (
    TERMINAL_STATUSES,
    cancel_job,
    create_job,
    estimate,
    get_job,
    list_jobs,
    read_log,
)
from ..models import JobCreateResult, JobEstimate, JobInfo, JobRequest

router = APIRouter()

POLL_INTERVAL = 0.5  # seconds between log-file polls while streaming
PING_INTERVAL = 15.0  # seconds between explicit ``event: ping`` keepalives


@router.post("/jobs/estimate", response_model=JobEstimate)
def jobs_estimate(req: JobRequest) -> JobEstimate:
    """Preview the LLM call cost of a request. Never touches the queue."""
    return estimate(req)


@router.post("/jobs", response_model=JobCreateResult)
def jobs_create(req: JobRequest) -> JobCreateResult:
    """Queue a run.py job. Requires ``confirm=true``; refuses ``count > 5``."""
    try:
        return create_job(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/jobs", response_model=List[JobInfo])
def jobs_list() -> List[JobInfo]:
    return list_jobs()


@router.get("/jobs/{job_id}", response_model=JobInfo)
def jobs_get(job_id: str) -> JobInfo:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"unknown job '{job_id}'")
    return job


@router.get("/jobs/{job_id}/logs")
def jobs_logs(job_id: str, offset: int = Query(0, ge=0)) -> Dict[str, Any]:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"unknown job '{job_id}'")
    lines, total = read_log(job_id, offset)
    return {
        "job_id": job_id,
        "status": job.status,
        "lines": lines,
        "line_count": total,
    }


@router.get("/jobs/{job_id}/stream")
async def jobs_stream(job_id: str) -> EventSourceResponse:
    """SSE: one ``log`` event per new line, periodic ``ping``, final ``done``."""
    if get_job(job_id) is None:
        raise HTTPException(status_code=404, detail=f"unknown job '{job_id}'")

    async def event_source() -> AsyncIterator[Dict[str, str]]:
        offset = 0
        last_ping = time.monotonic()
        while True:
            job = get_job(job_id)
            if job is None:
                return

            lines, _total = read_log(job_id, offset)
            if lines:
                offset += len(lines)
                last_ping = time.monotonic()
                for line in lines:
                    yield {"event": "log", "data": json.dumps(line, ensure_ascii=False)}

            job = get_job(job_id)  # refresh after draining the tail
            if job is None:
                return
            if job.status in TERMINAL_STATUSES:
                yield {"event": "done", "data": job.model_dump_json()}
                return

            if time.monotonic() - last_ping >= PING_INTERVAL:
                last_ping = time.monotonic()
                yield {
                    "event": "ping",
                    "data": json.dumps({"job_id": job_id, "status": job.status}),
                }

            await asyncio.sleep(POLL_INTERVAL)

    return EventSourceResponse(event_source(), ping=60)


@router.post("/jobs/{job_id}/cancel", response_model=JobInfo)
def jobs_cancel(job_id: str) -> JobInfo:
    job = cancel_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"unknown job '{job_id}'")
    return job
