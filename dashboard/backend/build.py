"""Build-step argv construction for the district -> household -> home pipeline.

Each world-generation stage runs as its own subprocess through the shared job
queue (:mod:`backend.jobs`), so SSE logs, estimates, cancellation and
persistence are reused unchanged. This module owns the per-step argv, verified
against each step module's ``main()`` argparse.

The home step backs up and rewrites ``household.json`` itself, so no pre-run
file hygiene is required before a step runs.
"""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from . import paths, world_admin
from .models import JobEstimate, JobInfo, JobRequest

STEP_ORDER: Tuple[str, ...] = ("district", "household", "home")
DISTRICT_SCOPE: Tuple[str, ...] = ("district", "household")
HOUSE_SCOPE: Tuple[str, ...] = ("home",)
STEP_MODULE: Dict[str, str] = {
    "district": os.path.join(paths.SRC_DIR, "steps", "world", "s1_district_description.py"),
    "household": os.path.join(paths.SRC_DIR, "steps", "world", "s2_household_compose.py"),
    "home": os.path.join(paths.SRC_DIR, "steps", "world", "s3_home.py"),
}
DEFAULT_SEED = 42


def require_step(req: JobRequest) -> str:
    step = str(req.step or "").strip()
    if step not in STEP_MODULE:
        raise ValueError(
            "build job needs a valid 'step' (one of %s); got %r"
            % (", ".join(STEP_ORDER), req.step)
        )
    return step


def require_district_lock(step: str, world_id: str, district: str) -> None:
    """Refuse the household/home steps until the district is locked (§18.3).

    Called on the job path, so a direct ``POST /api/jobs`` is refused with the
    same wording the Steps sheet shows via ``BuildStepStatus.blocked_reason``.
    """
    if step in world_admin.LOCKED_STEPS and not world_admin.is_locked(world_id, district):
        raise ValueError(world_admin.LOCK_REQUIRED_REASON)


def build_step_argv(req: JobRequest) -> Tuple[List[str], List[str]]:
    step = require_step(req)
    world_id = world_admin.normalize_world_id(req.world or "")
    district = world_admin.resolve_district(world_id, req.district)
    require_district_lock(step, world_id, district)
    warnings: List[str] = []
    argv: List[str] = [
        paths.VENV_PYTHON,
        STEP_MODULE[step],
        "--world",
        world_id,
        "--district",
        district,
    ]
    seed = DEFAULT_SEED if req.seed is None else int(req.seed)

    if step == "district":
        preset = str(req.preset or "").strip()
        prompt = str(req.prompt or "").strip()
        if preset:
            argv += ["--preset", preset]
        elif prompt:
            argv += ["--prompt", prompt]
        else:
            raise ValueError(
                "no preset or prompt given for district %s: refusing to fall back "
                "to the first preset" % district
            )
        argv += ["--seed", str(seed)]
        return argv, warnings

    if step == "household":
        if req.house is None or str(req.house).strip() == "":
            warnings.append(
                "--house not set; a new household will be appended to district %s." % district
            )
        else:
            argv += ["--house", world_admin.resolve_house_label(world_id, req.house, district)]
        if req.count is not None:
            argv += ["--count", str(int(req.count))]
        argv += ["--seed", str(seed)]
        return argv, warnings

    # home (house-scoped): passes the house label, not the 0-based index.
    label = world_admin.resolve_house_label(world_id, req.house, district)
    if req.house is None or str(req.house).strip() == "":
        warnings.append("--house not set; defaulting to %s." % label)
    argv += ["--house", label, "--seed", str(seed)]
    return argv, warnings


def estimate_build(req: JobRequest) -> JobEstimate:
    step = require_step(req)
    world_id = world_admin.normalize_world_id(req.world or "")
    if step == "district":
        return JobEstimate(
            kind="build",
            estimated_calls=1,
            detail="build: s1 district description = 1 LLM call (retries may add calls)",
        )
    if step == "household":
        if req.count is not None:
            return JobEstimate(
                kind="build",
                estimated_calls=1,
                detail="build: s2 household batch = 1 LLM call for %d descriptions "
                "(no members; retries may add calls)" % int(req.count),
            )
        return JobEstimate(
            kind="build",
            estimated_calls=2,
            detail="build: s2 household compose = 2 LLM calls (compose + adapt; "
            "retries may add calls)",
        )
    district = world_admin.resolve_district(world_id, req.district)
    label = world_admin.resolve_house_label(world_id, req.house, district)
    return JobEstimate(
        kind="build",
        estimated_calls=1,
        detail="build: s3 home for %s = 1 LLM call (retries may add calls)" % label,
    )


def prepare_step_run(job: JobInfo) -> List[str]:
    """No pre-run file hygiene is needed; the steps own their own backups."""
    return []
