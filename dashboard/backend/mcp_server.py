"""LLMWorld MCP server (milestone M6) - drive the dashboard without a browser.

:mod:`backend.main` mounts this module's ASGI app at ``/mcp`` on the SAME port
as the REST API (``http://127.0.0.1:8000/mcp``). Every tool is hand-written and
delegates to the existing backend services (:mod:`backend.store`,
:mod:`backend.world_admin`, :mod:`backend.jobs`, :mod:`backend.build`,
:mod:`backend.artifacts`, :mod:`backend.llm_trace`, :mod:`backend.derive`); no
business logic is duplicated here and nothing under ``src/`` is touched.

Client configuration
--------------------
Claude Code / Cursor (both use the ``mcpServers`` root key)::

    { "mcpServers": { "llmworld": { "type": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": { "Authorization": "Bearer ${MCP_TOKEN}" } } } }

VS Code - the root key is ``servers``, NOT ``mcpServers`` (the most common
paste error)::

    { "servers": { "llmworld": { "type": "http",
      "url": "http://127.0.0.1:8000/mcp" } } }

Auth & transport
----------------
* Localhost only: the transport rejects a non-localhost ``Host`` header with
  421 (this is the library default for ``streamable_http_app``).
* If ``MCP_TOKEN`` is set in the environment, every ``/mcp`` request must carry
  ``Authorization: Bearer <MCP_TOKEN>`` or it is rejected with 401. The token is
  never logged or echoed.
* The MCP app is mounted with internal path ``/`` so the public path is exactly
  ``/mcp`` (mounting with internal path ``/mcp`` would expose ``/mcp/mcp``).
* :mod:`backend.main` starts ``server.session_manager`` from the parent
  lifespan: Starlette never runs a mounted sub-app's own lifespan.

Token cost
----------
``run_build_step`` and ``run_simulation`` queue real ``run.py`` jobs that spend
API tokens, so both take ``confirm: bool = False`` and refuse unless it is
``True`` - the same gate the REST API applies through ``JobRequest.confirm``.
"""

from __future__ import annotations

import hmac
import os
import site
import sys
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, Optional


def _restore_pywin32_path() -> None:
    """Load pywin32's ``.pth`` entries when site-packages arrived via sys.path.

    The dev server adds the venv site-packages through ``sys.path`` instead of
    ``site.addsitedir``, so ``pywin32.pth`` never runs and ``import mcp`` fails on
    its unconditional ``import pywintypes`` (via ``mcp.server.stdio``). Running
    the same ``.pth`` processing that site would have performed fixes that; a
    sound interpreter already imports pywintypes and returns immediately.
    """
    try:
        import pywintypes  # noqa: F401
        return
    except ImportError:
        pass
    for entry in list(sys.path):
        if entry.endswith("site-packages") and os.path.isdir(entry):
            site.addsitedir(entry)


_restore_pywin32_path()

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from starlette.types import ASGIApp, Receive, Scope, Send

from . import artifacts, build, derive, jobs, llm_trace, store, world_admin
from .models import JobRequest

VERSION = "0.1.0"
LIST_WORLDS_NOTE = "One entry per directory under output/worlds/ (newest first)."


def _token() -> Optional[str]:
    """The configured bearer token, or ``None`` when auth is disabled.

    Read from the environment on every access so a reload picks up a change and
    so nothing is captured at import time. The value is never logged.
    """
    value = os.environ.get("MCP_TOKEN")
    return value if value else None


class BearerTokenGate:
    """Minimal ASGI wrapper that enforces ``Authorization: Bearer <token>``.

    Runs in front of the mounted MCP app. A request without the exact bearer
    token is answered with 401 before it reaches MCP; when no token is
    configured the wrapper is transparent.
    """

    def __init__(
        self,
        app: ASGIApp,
        token_getter: Optional[Callable[[], Optional[str]]] = None,
    ) -> None:
        self.app = app
        self._token_getter = token_getter or _token

    @staticmethod
    def _presented(scope: Scope) -> str:
        for key, value in scope.get("headers") or []:
            if key == b"authorization":
                return value.decode("latin-1")
        return ""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        token = self._token_getter()
        if scope["type"] != "http" or token is None:
            await self.app(scope, receive, send)
            return
        # Constant-time compare: both sides are bytes-like ASCII.
        if not hmac.compare_digest(
            self._presented(scope).encode("latin-1"),
            f"Bearer {token}".encode("latin-1"),
        ):
            body = b'{"error":"unauthorized"}'
            await send(
                {
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"www-authenticate", b"Bearer"),
                        (b"content-length", str(len(body)).encode("latin-1")),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return
        await self.app(scope, receive, send)


server = MCPServer(
    name="llmworld",
    title="LLMWorld Research Console",
    instructions=(
        "Tools over the LLMWorld energy-simulation repository. Worlds are built "
        "in four stages (types -> personas -> household -> assemble); "
        "run_build_step and run_simulation spend real API tokens and require "
        "confirm=True. list_worlds/create_world/delete_world/get_build_state are "
        "zero-LLM."
    ),
    version=VERSION,
)

# Internal path "/" so the public URL is /mcp (not /mcp/mcp).
_mcp_http_app = server.streamable_http_app(streamable_http_path="/")

# Public ASGI app mounted by main.py: bearer gate -> MCP streamable HTTP.
asgi_app: ASGIApp = BearerTokenGate(_mcp_http_app)


@asynccontextmanager
async def session_lifespan() -> AsyncIterator[None]:
    """Run the MCP session manager for the lifetime of the parent FastAPI app.

    Starlette does not execute a mounted sub-app's lifespan, so main.py must
    enter this context manager to start (and stop) the streamable-HTTP session
    manager.
    """
    async with server.session_manager.run():
        yield


# --------------------------------------------------------------------------
# Catalog / worlds
# --------------------------------------------------------------------------
@server.tool(description="List worlds under output/worlds/ (newest first). " + LIST_WORLDS_NOTE)
def list_worlds() -> dict[str, Any]:
    return {"worlds": [info.model_dump(mode="json") for info in store.list_worlds()]}


@server.tool(
    description=(
        "Create an EMPTY world (scaffolding only, zero LLM calls). Idempotent: "
        "an existing world is returned with created=false."
    )
)
def create_world(
    world_id: str,
    world_config: Optional[str] = None,
    seed: Optional[int] = None,
) -> dict[str, Any]:
    try:
        return world_admin.create_world(world_id, world_config, seed)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


@server.tool(
    description=(
        "Delete a world. Default is recoverable (move to output/_trash/); pass "
        "permanent=true for an irreversible removal."
    )
)
def delete_world(world_id: str, permanent: bool = False) -> dict[str, Any]:
    try:
        return world_admin.delete_world(world_id, permanent)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


@server.tool(
    description=(
        "Per-step build progress for a world: which of the four steps "
        "(types/personas/household/assemble) are done, runnable, or blocked, "
        "plus the house-level breakdown."
    )
)
def get_build_state(world_id: str) -> dict[str, Any]:
    try:
        return world_admin.build_state(world_id).model_dump(mode="json")
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


@server.tool(
    description=(
        "Preview the reads, writes and overwrites for one build step without "
        "running it. step is one of types, personas, household, assemble."
    )
)
def get_build_preview(
    world_id: str,
    step: str,
    house: Optional[str] = None,
) -> dict[str, Any]:
    try:
        return world_admin.build_preview(world_id, step, house).model_dump(mode="json")
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


@server.tool(
    description=(
        "Queue ONE world-build step as a run.py job (same path as POST /api/jobs "
        "with kind=build). TOKEN-COSTLY: requires confirm=True. Get the estimate "
        "and the file preview first via get_build_preview."
    )
)
def run_build_step(
    world_id: str,
    step: str,
    house: Optional[str] = None,
    count: Optional[int] = None,
    seed: Optional[int] = None,
    confirm: bool = False,
) -> dict[str, Any]:
    if not confirm:
        raise ToolError(
            "refusing to run a token-costly build step: pass confirm=True. "
            "Inspect get_build_preview first; this mirrors the POST /api/jobs gate."
        )
    if step not in build.STEP_ORDER:
        raise ToolError(
            "unknown step %r: expected one of %s" % (step, ", ".join(build.STEP_ORDER))
        )
    request = JobRequest(
        kind="build",
        world=world_id,
        step=step,
        house=house,
        count=count,
        seed=seed,
        confirm=True,
    )
    try:
        result = jobs.create_job(request)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    return {
        "job": result.job.model_dump(mode="json"),
        "estimate": result.estimate.model_dump(mode="json"),
    }


# --------------------------------------------------------------------------
# Jobs / LLM trace
# --------------------------------------------------------------------------
@server.tool(description="List all known run.py jobs, newest first.")
def list_jobs() -> dict[str, Any]:
    return {"jobs": [job.model_dump(mode="json") for job in jobs.list_jobs()]}


@server.tool(description="Full status of one job by id.")
def get_job(job_id: str) -> dict[str, Any]:
    job = jobs.get_job(job_id)
    if job is None:
        raise ToolError("unknown job '%s'" % job_id)
    return job.model_dump(mode="json")


@server.tool(
    description=(
        "Cancel a queued/running job. A queued job is dropped before it starts; "
        "a running one is terminated."
    )
)
def cancel_job(job_id: str) -> dict[str, Any]:
    job = jobs.cancel_job(job_id)
    if job is None:
        raise ToolError("unknown job '%s'" % job_id)
    return job.model_dump(mode="json")


@server.tool(
    description=(
        "List the LLM calls a build job recorded (prompt size, duration, HTTP "
        "status, success)."
    )
)
def list_llm_calls(job_id: str, offset: int = 0, limit: int = 500) -> dict[str, Any]:
    job = jobs.get_job(job_id)
    if job is None:
        raise ToolError("unknown job '%s'" % job_id)
    return llm_trace.list_calls(job, offset, limit).model_dump(mode="json")


@server.tool(
    description="Full prompt / request / response for one traced LLM call of a job."
)
def get_llm_call(job_id: str, call_id: str) -> dict[str, Any]:
    job = jobs.get_job(job_id)
    if job is None:
        raise ToolError("unknown job '%s'" % job_id)
    detail = llm_trace.get_call(job, call_id)
    if detail is None:
        raise ToolError("no LLM call '%s' in job '%s'" % (call_id, job_id))
    return detail.model_dump(mode="json")


# --------------------------------------------------------------------------
# Artifacts (hand edit with backup + diff, path confined to the world dir)
# --------------------------------------------------------------------------
@server.tool(
    description=(
        "Read a world artifact by its path relative to the world directory "
        "(e.g. 'house_0001/household.json'). JSON is parsed into data."
    )
)
def get_artifact(world: str, path: str) -> dict[str, Any]:
    try:
        return artifacts.read_artifact(world, path).model_dump(mode="json")
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


@server.tool(
    description=(
        "Write a world artifact by relative path. JSON is validated before it is "
        "persisted, the previous file is backed up to <name>.bak.<timestamp>, and "
        "a unified diff is returned."
    )
)
def put_artifact(world: str, path: str, content: str) -> dict[str, Any]:
    try:
        return artifacts.write_artifact(world, path, content).model_dump(mode="json")
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


# --------------------------------------------------------------------------
# Simulation catalog / replay
# --------------------------------------------------------------------------
@server.tool(description="One entry per simulation run under output/simulation/.")
def list_runs() -> dict[str, Any]:
    return {"runs": [info.model_dump(mode="json") for info in store.list_runs()]}


@server.tool(description="Dates, houses and policy tags for one simulation run.")
def get_run_meta(run: str) -> dict[str, Any]:
    meta = store.run_meta(run)
    if meta is None:
        raise ToolError("run not found: %s" % run)
    return meta


@server.tool(
    description=(
        "Queue a simulation as a run.py job (same path as POST /api/jobs with "
        "kind=simulate). TOKEN-COSTLY: requires confirm=True."
    )
)
def run_simulation(
    world: str,
    date: Optional[str] = None,
    days: Optional[int] = None,
    house: Optional[str] = None,
    env: Optional[str] = None,
    member: Optional[str] = None,
    policy: Optional[str] = None,
    policy_schedule: Optional[list[str]] = None,
    s4_only: bool = False,
    workers: Optional[int] = None,
    confirm: bool = False,
) -> dict[str, Any]:
    if not confirm:
        raise ToolError(
            "refusing to run a token-costly simulation: pass confirm=True. "
            "This mirrors the POST /api/jobs gate."
        )
    request = JobRequest(
        kind="simulate",
        world=world,
        date=date,
        days=days,
        house=house,
        env=env,
        member=member,
        policy=policy,
        policy_schedule=list(policy_schedule or []),
        s4_only=s4_only,
        workers=workers,
        confirm=True,
    )
    try:
        result = jobs.create_job(request)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    return {
        "job": result.job.model_dump(mode="json"),
        "estimate": result.estimate.model_dump(mode="json"),
    }


@server.tool(
    description=(
        "Everything needed to render one (run, date, house) day: household, "
        "member activities/decisions, per-appliance series and metrics."
    )
)
def get_day_replay(
    run: str,
    date: str,
    house: str,
    policy: str = "baseline",
) -> dict[str, Any]:
    try:
        return derive.build_day_replay(run, date, house, policy).model_dump(mode="json")
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


@server.tool(
    description=(
        "All houses of one run at a single minute of a day (minute is 0..1439, "
        "minutes since midnight)."
    )
)
def get_snapshot(
    run: str,
    date: str,
    minute: int = 0,
    policy: str = "baseline",
) -> dict[str, Any]:
    try:
        return derive.build_snapshot(run, date, minute, policy).model_dump(mode="json")
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
