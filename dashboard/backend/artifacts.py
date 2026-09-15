"""Read and hand-edit a world's build artifacts.

Every write goes through the same safety contract as the build steps:
the previous file is copied to ``<name>.bak.<timestamp>`` first, JSON files are
validated before they are persisted, and a unified diff is returned so the UI
can show exactly what changed. Paths are confined to the world directory.
"""

from __future__ import annotations

import difflib
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from . import world_admin
from .models import ArtifactRead, ArtifactWriteResult

MAX_DIFF_CHARS = 8000
MAX_READ_BYTES = 2_000_000


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _relative_parts(rel_path: str) -> List[str]:
    rel = str(rel_path or "").strip().replace("\\", "/")
    if not rel:
        raise ValueError("artifact path is required")
    if rel.startswith("/") or rel.startswith("~"):
        raise ValueError("artifact path must be relative to the world directory")
    parts = [part for part in rel.split("/") if part not in ("", ".")]
    if not parts or any(part == ".." for part in parts):
        raise ValueError("artifact path must not escape the world directory")
    return parts


def resolve(world_id: str, rel_path: str) -> Tuple[str, str]:
    wid = world_admin.normalize_world_id(world_id)
    world_dir = os.path.realpath(world_admin.resolve_world_dir(wid))
    if not os.path.isdir(world_dir):
        raise ValueError("world not found: %s" % wid)
    parts = _relative_parts(rel_path)
    target = os.path.realpath(os.path.join(world_dir, *parts))
    if os.path.commonpath([world_dir, target]) != world_dir:
        raise ValueError("artifact path must stay inside the world directory")
    return target, "/".join(parts)


def _read_text(path: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        return None, str(exc)
    if size > MAX_READ_BYTES:
        return None, "file is too large to edit (%d bytes)" % size
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read(), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, str(exc)


def _diff(before: str, after: str) -> str:
    lines = list(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile="before",
            tofile="after",
            lineterm="",
            n=2,
        )
    )
    text = "\n".join(lines)
    if len(text) > MAX_DIFF_CHARS:
        text = text[:MAX_DIFF_CHARS] + "\n… (diff truncated)"
    return text


def read_artifact(world_id: str, rel_path: str) -> ArtifactRead:
    path, rel = resolve(world_id, rel_path)
    exists = os.path.isfile(path)
    kind = "json" if rel.lower().endswith(".json") else "text"
    if not exists:
        return ArtifactRead(
            world=world_id, path=path, rel_path=rel, exists=False, size=None,
            modified_at=None, kind=kind, data=None, text=None, parse_error=None,
        )

    text, error = _read_text(path)
    modified_at = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
    size = os.path.getsize(path)
    if text is None:
        return ArtifactRead(
            world=world_id, path=path, rel_path=rel, exists=True, size=size,
            modified_at=modified_at, kind=kind, data=None, text=None, parse_error=error,
        )

    parsed: Optional[Any] = None
    parse_error: Optional[str] = None
    if kind == "json":
        try:
            parsed = json.loads(text)
        except ValueError as exc:
            parse_error = str(exc)
    return ArtifactRead(
        world=world_id, path=path, rel_path=rel, exists=True, size=size,
        modified_at=modified_at, kind=kind, data=parsed, text=text, parse_error=parse_error,
    )


def write_artifact(world_id: str, rel_path: str, content: str) -> ArtifactWriteResult:
    path, rel = resolve(world_id, rel_path)
    parent = os.path.dirname(path)
    if not os.path.isdir(parent):
        raise ValueError(
            "parent directory does not exist: %s (run the prerequisite step first)"
            % os.path.basename(parent)
        )

    kind = "json" if rel.lower().endswith(".json") else "text"
    warnings: List[str] = []
    parsed: Optional[Any] = None
    if kind == "json":
        try:
            parsed = json.loads(content)
        except ValueError as exc:
            raise ValueError("refusing to write invalid JSON: %s" % exc) from exc

    existed = os.path.isfile(path)
    before_text: Optional[str] = None
    if existed:
        before_text, _ = _read_text(path)
        if kind == "json" and before_text is not None:
            try:
                previous = json.loads(before_text)
            except ValueError:
                previous = None
            if previous is not None and parsed is not None:
                if type(previous) is not type(parsed):
                    warnings.append(
                        "top-level JSON type changed from %s to %s"
                        % (type(previous).__name__, type(parsed).__name__)
                    )

    changed = (not existed) or before_text != content
    backup: Optional[str] = None
    if existed and changed:
        backup = "%s.bak.%s" % (path, _stamp())
        bump = 0
        while os.path.exists(backup):
            bump += 1
            backup = "%s.bak.%s_%d" % (path, _stamp(), bump)
        try:
            with open(path, encoding="utf-8") as src, open(backup, "w", encoding="utf-8") as dst:
                dst.write(src.read())
        except (OSError, UnicodeDecodeError) as exc:
            raise ValueError("could not back up %s: %s" % (rel, exc)) from exc

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)

    return ArtifactWriteResult(
        world=world_id,
        path=path,
        rel_path=rel,
        written=True,
        created=not existed,
        backup=backup,
        changed=changed,
        diff=_diff(before_text or "", content),
        json_valid=True,
        warnings=warnings,
    )
