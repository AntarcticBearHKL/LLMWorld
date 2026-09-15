"""Build-step argv construction and pre-run file preparation.

Each world-generation stage runs as its own subprocess through the shared job
queue (:mod:`backend.jobs`), so SSE logs, estimates, cancellation and
persistence are reused unchanged. This module owns:

* the per-step argv, verified against each step module's ``main()`` argparse;
* the s4 pre-run cleanup - ``s4_world_assemble`` APPENDS to ``households.json``
  and is not idempotent, so any existing entry for the target house is stripped
  (after a ``.bak.<timestamp>`` copy) before the subprocess starts.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from . import paths, world_admin
from .models import JobEstimate, JobInfo, JobRequest

STEP_ORDER: Tuple[str, ...] = ("types", "personas", "household", "assemble")
HOUSE_SCOPE: Tuple[str, ...] = ("personas", "household", "assemble")
STEP_MODULE: Dict[str, str] = {
    "types": os.path.join(paths.SRC_DIR, "steps", "world", "s1_household_types.py"),
    "personas": os.path.join(paths.SRC_DIR, "steps", "world", "s2_persona_align.py"),
    "household": os.path.join(paths.SRC_DIR, "steps", "world", "s3_household_build.py"),
    "assemble": os.path.join(paths.SRC_DIR, "steps", "world", "s4_world_assemble.py"),
}
DEFAULT_SEED = 42
BACKUP_SUFFIX = ".bak."


def require_step(req: JobRequest) -> str:
    step = str(req.step or "").strip()
    if step not in STEP_MODULE:
        raise ValueError(
            "build job needs a valid 'step' (one of %s); got %r"
            % (", ".join(STEP_ORDER), req.step)
        )
    return step


def build_step_argv(req: JobRequest) -> Tuple[List[str], List[str]]:
    step = require_step(req)
    world_id = world_admin.normalize_world_id(req.world or "")
    warnings: List[str] = []
    argv: List[str] = [paths.VENV_PYTHON, STEP_MODULE[step], "--world", world_id]
    seed = DEFAULT_SEED if req.seed is None else int(req.seed)

    if step == "types":
        if req.count is None:
            warnings.append("--count not set; defaulting to 1 household type.")
        count = 1 if req.count is None else int(req.count)
        argv += ["--count", str(count), "--seed", str(seed)]
        return argv, warnings

    label = world_admin.resolve_house_label(world_id, req.house)
    index = world_admin.house_index_from(label)
    if index is None:
        raise ValueError("could not resolve house %r to a 0-based index" % (label,))
    if req.house is None or str(req.house).strip() == "":
        warnings.append("--house not set; defaulting to %s." % label)
    argv += ["--house", str(index), "--seed", str(seed)]
    return argv, warnings


def estimate_build(req: JobRequest) -> JobEstimate:
    step = require_step(req)
    world_id = world_admin.normalize_world_id(req.world or "")
    if step == "types":
        count = 1 if req.count is None else int(req.count)
        return JobEstimate(
            kind="build",
            estimated_calls=1,
            detail="build: s1 household types = 1 LLM call (count=%d)" % count,
        )
    if step == "assemble":
        return JobEstimate(
            kind="build",
            estimated_calls=0,
            detail="build: s4 assemble merges existing artifacts (no LLM calls)",
        )
    label = world_admin.resolve_house_label(world_id, req.house)
    if step == "personas":
        return JobEstimate(
            kind="build",
            estimated_calls=1,
            detail="build: s2 persona align for %s = 1 LLM call (retries may add calls)"
            % label,
        )
    members = world_admin.member_count(world_id, label)
    if members:
        calls = 1 + members
        member_detail = "%d member(s)" % members
    else:
        calls = 2
        member_detail = "member count unknown; assuming 1"
    return JobEstimate(
        kind="build",
        estimated_calls=calls,
        detail="build: s3 household build for %s = 1 home call + member calls (%s) = %d"
        % (label, member_detail, calls),
    )


def prepare_step_run(job: JobInfo) -> List[str]:
    """Run pre-flight file hygiene for a build job; returns log lines."""
    if job.kind != "build" or not job.step:
        return []
    world_id = world_admin.normalize_world_id(job.world or "")
    lines: List[str] = []
    if job.step == "assemble":
        label = job.house or world_admin.resolve_house_label(world_id, None)
        lines += _dedup_households_meta(world_id, label)
        lines += _backup_if_exists(world_admin.house_file(world_id, label, "household.json"))
        lines += _backup_if_exists(world_admin.house_file(world_id, label, "personas.json"))
    return lines


def build_env(job: JobInfo) -> Optional[Dict[str, str]]:
    """Environment for a build subprocess, or ``None`` to inherit the parent's.

    Points ``LLM_TRACE_FILE`` at a per-job JSONL so ``src/engine/subagent.py``
    records every prompt / response / duration / http_status for this step.
    Nothing inside ``src/`` is modified - the trace hook is already env-driven.
    """
    if job.kind != "build" or not job.world or not job.id:
        return None
    try:
        world_id = world_admin.normalize_world_id(job.world)
    except ValueError:
        return None
    env = dict(os.environ)
    env["LLM_TRACE_FILE"] = world_admin.llm_trace_path(world_id, job.id)
    return env


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _backup_file(path: str) -> str:
    backup = "%s%s%s" % (path, BACKUP_SUFFIX, _stamp())
    bump = 0
    while os.path.exists(backup):
        bump += 1
        backup = "%s%s%s_%d" % (path, BACKUP_SUFFIX, _stamp(), bump)
    shutil.copy2(path, backup)
    return backup


def _backup_if_exists(path: str) -> List[str]:
    if not os.path.isfile(path):
        return []
    backup = _backup_file(path)
    return [
        "[build] backed up %s -> %s" % (os.path.basename(path), os.path.basename(backup))
    ]


def _dedup_households_meta(world_id: str, house_label_value: Optional[str]) -> List[str]:
    if not house_label_value:
        return []
    path = world_admin.households_meta_path(world_id)
    if not os.path.isfile(path):
        return ["[build] %s not found; the assemble step will create it" % path]

    backup = _backup_file(path)
    data = world_admin.read_json(path)
    entries = data.get("households") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        entries = []
    kept = [
        entry
        for entry in entries
        if not (isinstance(entry, dict) and str(entry.get("house_id")) == house_label_value)
    ]
    removed = len(entries) - len(kept)

    cleaned: Dict[str, Any] = dict(data) if isinstance(data, dict) else {}
    cleaned["households"] = kept
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(cleaned, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    return [
        "[build] %s: removed %d stale entry(ies) for %s (backup: %s)"
        % (path, removed, house_label_value, os.path.basename(backup))
    ]
