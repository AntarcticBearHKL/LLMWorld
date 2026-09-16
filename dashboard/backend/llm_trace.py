"""Read the per-job LLM call trace written by a build subprocess.

The trace is a JSONL file produced by ``src/engine/subagent.py`` whenever the
``LLM_TRACE_FILE`` env var points at a path; :func:`backend.build.build_env`
points it at :func:`backend.world_admin.llm_trace_path`. This module only reads
that file - it never writes it and never touches ``src/``.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterator, List, Optional

from . import world_admin
from .models import JobInfo, LLMCallDetail, LLMCallList, LLMCallSummary


def trace_path_for(job: JobInfo) -> Optional[str]:
    if not job.world:
        return None
    try:
        world_id = world_admin.normalize_world_id(job.world)
    except ValueError:
        return None
    return world_admin.llm_trace_path(world_id, job.id, job.district)


def _iter_records(path: str) -> Iterator[Dict[str, Any]]:
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if isinstance(record, dict):
                    yield record
    except OSError:
        return


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _summary(record: Dict[str, Any]) -> LLMCallSummary:
    response = record.get("response")
    return LLMCallSummary(
        logical_call_id=str(record.get("logical_call_id") or ""),
        request_index=_as_int(record.get("request_index"), 1),
        request_count=_as_int(record.get("request_count"), 1),
        http_status=record.get("http_status"),
        duration_seconds=record.get("duration_seconds"),
        started_at=record.get("started_at"),
        prompt_chars=_as_int(record.get("prompt_chars"), 0),
        ok=record.get("http_status") == 200 and not record.get("error"),
        error=record.get("error"),
        has_response=response is not None,
    )


def list_calls(job: JobInfo, offset: int = 0, limit: int = 500) -> LLMCallList:
    path = trace_path_for(job)
    exists = bool(path) and os.path.isfile(path)
    records: List[Dict[str, Any]] = list(_iter_records(path)) if path and exists else []
    window = records[offset : offset + limit]
    return LLMCallList(
        job_id=job.id,
        world=job.world,
        step=job.step,
        exists=exists,
        total=len(records),
        calls=[_summary(record) for record in window],
    )


def get_call(job: JobInfo, logical_call_id: str) -> Optional[LLMCallDetail]:
    path = trace_path_for(job)
    if not path:
        return None
    for record in _iter_records(path):
        if str(record.get("logical_call_id") or "") != logical_call_id:
            continue
        return LLMCallDetail(
            logical_call_id=logical_call_id,
            request_index=_as_int(record.get("request_index"), 1),
            request_count=_as_int(record.get("request_count"), 1),
            http_status=record.get("http_status"),
            duration_seconds=record.get("duration_seconds"),
            started_at=record.get("started_at"),
            prompt_chars=_as_int(record.get("prompt_chars"), 0),
            error=record.get("error"),
            request=record.get("request"),
            response=record.get("response"),
        )
    return None
