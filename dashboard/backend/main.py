"""LLMWorld Research Console - FastAPI application.

Routers are attached defensively so the app can boot while they are being
built in parallel. Run with:

    .venv\\Scripts\\python.exe -m uvicorn backend.main:app --reload --port 8000
        (from the dashboard/ directory)
"""

from __future__ import annotations

import json
import os
import threading
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Callable, Optional

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from .paths import LLMWORLD_ROOT, OUTPUT_DIR, WEB_DIST

# Set when the MCP app mounts below; the lifespan runs its session manager.
_mcp_session_lifespan: Optional[Callable[[], AbstractAsyncContextManager[None]]] = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from . import store

    threading.Thread(target=store.list_run_summaries, daemon=True).start()
    if _mcp_session_lifespan is None:
        yield
    else:
        async with _mcp_session_lifespan():
            yield


app = FastAPI(title="LLMWorld Research Console", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*", "Mcp-Session-Id", "Mcp-Protocol-Version", "Mcp-Trace-Id"],
    expose_headers=["Mcp-Session-Id"],
)


class _McpPathNormalizer:
    """Serve the bare '/mcp' path without Starlette's 307 redirect to '/mcp/'.

    Some MCP clients refuse to follow redirects, so the path is rewritten before
    routing and the mount matches '/mcp' directly.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope.get("path") == "/mcp":
            scope = {**scope, "path": "/mcp/"}
        await self.app(scope, receive, send)


app.add_middleware(_McpPathNormalizer)

ATTACHED: list[str] = []
MISSING: list[str] = []

try:
    from .routers import worlds as _worlds

    app.include_router(_worlds.router, prefix="/api")
    ATTACHED.append("worlds")
except Exception as exc:  # noqa: BLE001 - keep the app bootable during parallel work
    MISSING.append(f"worlds: {exc}")

try:
    from .routers import replay as _replay

    app.include_router(_replay.router, prefix="/api")
    ATTACHED.append("replay")
except Exception as exc:  # noqa: BLE001
    MISSING.append(f"replay: {exc}")

try:
    from .routers import jobs as _jobs

    app.include_router(_jobs.router, prefix="/api")
    ATTACHED.append("jobs")
except Exception as exc:  # noqa: BLE001
    MISSING.append(f"jobs: {exc}")

try:
    from .routers import build as _build

    app.include_router(_build.router, prefix="/api")
    ATTACHED.append("build")
except Exception as exc:  # keep the app bootable during parallel work
    MISSING.append(f"build: {exc}")

try:
    from . import mcp_server as _mcp

    app.mount("/mcp", _mcp.asgi_app)
    _mcp_session_lifespan = _mcp.session_lifespan
    ATTACHED.append("mcp")
except Exception as exc:  # noqa: BLE001 - keep the dashboard bootable if MCP fails
    MISSING.append(f"mcp: {exc}")


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "llmworld_root": LLMWORLD_ROOT,
        "output_dir": OUTPUT_DIR,
        "output_exists": os.path.isdir(OUTPUT_DIR),
        "routers": ATTACHED,
        "missing_routers": MISSING,
        "web_dist": os.path.isdir(WEB_DIST),
    }


@app.get("/config.js", include_in_schema=False)
def runtime_config() -> Response:
    base = os.environ.get("LLMWORLD_API_BASE", "/api")
    return Response(
        content="window.__API_BASE__ = %s;\n" % json.dumps(base),
        media_type="application/javascript",
        headers={"cache-control": "no-store"},
    )


# --- Serve the built SPA (production). In dev, use the Vite server instead. ---
if os.path.isdir(WEB_DIST):
    assets = os.path.join(WEB_DIST, "assets")
    if os.path.isdir(assets):
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        candidate = os.path.join(WEB_DIST, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        index = os.path.join(WEB_DIST, "index.html")
        if os.path.isfile(index):
            return FileResponse(index)
        return JSONResponse({"error": "frontend not built"}, status_code=404)
