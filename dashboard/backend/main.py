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
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .paths import LLMWORLD_ROOT, OUTPUT_DIR, WEB_DIST


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from . import store

    threading.Thread(target=store.list_run_summaries, daemon=True).start()
    yield


app = FastAPI(title="LLMWorld Research Console", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
