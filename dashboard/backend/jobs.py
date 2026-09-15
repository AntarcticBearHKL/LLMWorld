"""Job runner for the LLMWorld Research Console.

Responsibilities
----------------
* Translate a :class:`backend.models.JobRequest` into the exact ``run.py``
  argv (``run.py:main`` is the authoritative CLI).
* Estimate the number of LLM calls a request will cost - no side effects.
* Execute ONE job at a time in a background daemon thread. The research repo
  has a single writer to ``output/``, so jobs are serialised through a
  module-level queue.
* Persist each job as ``dashboard/jobs/<id>.json`` and stream its combined
  stdout/stderr into ``dashboard/jobs/<id>.log`` (UTF-8, line buffered).

Safety
------
* ``run.py`` costs real API tokens. :func:`create_job` refuses to run unless
  the caller echoes ``confirm=True`` after reviewing an estimate.
* ``.env`` is never read, logged or exposed; the child process simply inherits
  the parent environment (that is how credentials reach ``run.py``).
* Never uses ``shell=True`` - always an argv list.
"""

from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import time
import uuid
from collections import deque
from datetime import datetime
from typing import Deque, Dict, List, Optional, Tuple

from . import paths
from .models import JobCreateResult, JobEstimate, JobInfo, JobRequest

# --------------------------------------------------------------------------
# Paths / constants
# --------------------------------------------------------------------------
JOBS_DIR = paths.JOBS_DIR
os.makedirs(JOBS_DIR, exist_ok=True)

RUN_PY = os.path.join(paths.LLMWORLD_ROOT, "run.py")
WORLDS_DIR = paths.WORLDS_DIR
POSTCODE = "3168"  # Clayton - the only district run.py/generate_world write to

MAX_HOUSEHOLDS = 5  # research rule: count <= 5 per world
RECENT_LINES = 5000  # in-memory tail kept per job
TERMINAL_STATUSES: Tuple[str, ...] = ("done", "failed", "cancelled")
_PERSIST_EVERY_LINES = 25

# --------------------------------------------------------------------------
# In-memory state (guarded by _lock)
# --------------------------------------------------------------------------
_jobs: Dict[str, JobInfo] = {}
_procs: Dict[str, "subprocess.Popen[str]"] = {}
_recent: Dict[str, Deque[str]] = {}
_line_counts: Dict[str, int] = {}
_lock = threading.RLock()

_queue: "queue.Queue[str]" = queue.Queue()
_worker: Optional[threading.Thread] = None
_worker_lock = threading.Lock()


def _now() -> str:
    return datetime.now().isoformat(timespec="milliseconds")


def _job_path(job_id: str) -> str:
    return os.path.join(JOBS_DIR, f"{job_id}.json")


def _log_path(job_id: str) -> str:
    return os.path.join(JOBS_DIR, f"{job_id}.log")


def _persist(job: JobInfo) -> None:
    """Atomically write the JobInfo to ``jobs/<id>.json``. Caller holds _lock."""
    path = _job_path(job.id)
    tmp = f"{path}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(job.model_dump(), fh, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except OSError:
        # Persistence must never take the runner down; the in-memory job stays
        # authoritative for this process.
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass


def _copy(job: JobInfo) -> JobInfo:
    """Return a snapshot with a fresh line count. Caller holds _lock."""
    out = job.model_copy(deep=True)
    out.line_count = _line_counts.get(job.id, out.line_count)
    return out


def _split_lines(lines: List[str]) -> List[str]:
    """Flatten embedded newlines so logical and physical log lines agree."""
    out: List[str] = []
    for line in lines:
        parts = str(line).replace("\r\n", "\n").replace("\r", "\n").split("\n")
        out.extend(parts)
    return out


def _append_log_lines(job_id: str, lines: List[str]) -> None:
    """Append lines to the job log and mirror them into memory."""
    physical = _split_lines(lines)
    if not physical:
        return
    try:
        with open(_log_path(job_id), "a", encoding="utf-8", errors="replace", buffering=1) as fh:
            for line in physical:
                fh.write(line + "\n")
    except OSError:
        return
    with _lock:
        buf = _recent.get(job_id)
        if buf is not None:
            buf.extend(physical)
        _line_counts[job_id] = _line_counts.get(job_id, 0) + len(physical)


def _count_lines(path: str) -> int:
    try:
        with open(path, "rb") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


# --------------------------------------------------------------------------
# argv construction
# --------------------------------------------------------------------------
def _argv_and_warnings(req: JobRequest) -> Tuple[List[str], List[str]]:
    """Build the run.py argv plus any warnings worth recording in the log."""
    warnings: List[str] = []
    argv: List[str] = [paths.VENV_PYTHON, RUN_PY, "--mode", req.kind]

    if req.kind == "world":
        if req.world:
            argv += ["--world", str(req.world)]
        if req.world_config:
            argv += ["--world-config", str(req.world_config)]
        if req.count is not None:
            argv += ["--count", str(int(req.count))]
        if req.seed is not None:
            argv += ["--seed", str(int(req.seed))]
        if req.workers is not None:
            argv += ["--workers", str(int(req.workers))]
        return argv, warnings

    # simulate
    if req.world:
        argv += ["--world", str(req.world)]
    if req.date:
        argv += ["--date", str(req.date)]
    else:
        today = time.strftime("%Y-%m-%d")
        warnings.append(
            f"--date not set; defaulting to {today}. An unset date drifts across "
            "midnight, so pass an explicit date for reproducible runs."
        )
        argv += ["--date", today]
    if req.days is not None:
        argv += ["--days", str(int(req.days))]
    if req.house:
        argv += ["--house", str(req.house)]
    if req.env:
        argv += ["--env", str(req.env)]
    if req.member:
        argv += ["--member", str(req.member)]
    if req.workers is not None:
        argv += ["--workers", str(int(req.workers))]
    if req.policy:
        argv += ["--policy", str(req.policy)]
    for spec in req.policy_schedule:
        argv += ["--policy-schedule", str(spec)]
    if req.s4_only:
        argv += ["--s4-only"]
    for spec in req.event:
        argv += ["--event", str(spec)]
    for spec in req.event_template:
        argv += ["--event-template", str(spec)]
    for spec in req.community_notice:
        argv += ["--community-notice", str(spec)]
    if req.temperature is not None:
        argv += ["--temperature", str(float(req.temperature))]
    if req.no_thinking:
        argv += ["--no-thinking"]
    if req.reasoning_effort:
        argv += ["--reasoning-effort", str(req.reasoning_effort)]
    if req.peer_nudge:
        argv += ["--peer-nudge"]
    if req.natural_ev:
        argv += ["--natural-ev"]
    if req.cost_context:
        argv += ["--cost-context"]
    if req.price_sensitivity:
        argv += ["--price-sensitivity", str(req.price_sensitivity)]
    if req.bill_feedback:
        argv += ["--bill-feedback"]
    argv += ["--cost-context-mode", str(req.cost_context_mode)]
    return argv, warnings


def build_argv(req: JobRequest) -> List[str]:
    """Map every populated JobRequest field to run.py flags.

    Repeatable flags (``--policy-schedule``, ``--event``, ``--event-template``,
    ``--community-notice``) are appended once per list item.
    """
    argv, warnings = _argv_and_warnings(req)
    for warning in warnings:
        print(f"[jobs] warning: {warning}")
    return argv


# --------------------------------------------------------------------------
# Estimation
# --------------------------------------------------------------------------
def _household_paths(world: str, house: str) -> Tuple[str, str]:
    primary = os.path.join(WORLDS_DIR, world, POSTCODE, house, "household.json")
    fallback = os.path.join(WORLDS_DIR, world, "household.json")
    return primary, fallback


def _member_count(world: str, house: str) -> Optional[int]:
    """Read the member count from household.json; None when unknown."""
    for path in _household_paths(world, house):
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return None
        members = data.get("members")
        if isinstance(members, dict):
            return len(members)
        if isinstance(members, list):
            return len(members)
        return None
    return None


def _list_world_houses(world: str) -> List[str]:
    """Mirror generate_world.list_houses without importing it (config loads .env)."""
    district = os.path.join(WORLDS_DIR, world, POSTCODE)
    if os.path.isdir(district):
        houses = sorted(
            d
            for d in os.listdir(district)
            if d.startswith("house_")
            and os.path.isfile(os.path.join(district, d, "household.json"))
        )
        if houses:
            return houses
    if os.path.isfile(os.path.join(WORLDS_DIR, world, "household.json")):
        return ["house_0001"]
    return []


def estimate(req: JobRequest) -> JobEstimate:
    """Predict the number of LLM calls a request will make. No side effects."""
    if req.kind == "world":
        count = int(req.count) if req.count is not None else 1
        calls = 1 + 3 * count
        detail = (
            f"world: s1 household types = 1 call; s2 persona + s3 household + "
            f"s4 assemble = 3 calls per household x {count} = {calls} LLM calls"
        )
        if req.count is None:
            detail += " (count not set; run.py defaults to 1)"
        return JobEstimate(kind=req.kind, estimated_calls=calls, detail=detail)

    days = int(req.days) if req.days is not None else 1
    stages = 1 if req.s4_only else 4
    if req.member:
        members = 1
        members_detail = "1 member (--member selects a single member per house)"
    else:
        world = req.world or req.env
        if not world:
            members = 1
            members_detail = "member count unknown (no world id given); assuming 1"
        else:
            if req.house:
                houses = [h.strip() for h in str(req.house).split(",") if h.strip()]
            else:
                houses = _list_world_houses(str(world))
            if not houses:
                members = 1
                members_detail = (
                    f"member count unknown (no household.json for world '{world}'); assuming 1"
                )
            else:
                total = 0
                unknown: List[str] = []
                for house in houses:
                    count = _member_count(str(world), house)
                    if count is None:
                        unknown.append(house)
                        total += 1
                    else:
                        total += count
                members = total
                members_detail = f"{members} member(s) across {len(houses)} house(s)"
                if unknown:
                    members_detail += (
                        f"; member count unknown for {unknown}, assumed 1 each"
                    )
    calls = members * stages * days
    detail = (
        f"simulate: {members} member(s) x {stages} stage(s) "
        f"({'s4-only' if req.s4_only else 's1-s4'}) x {days} day(s) = {calls} LLM calls "
        f"[{members_detail}]"
    )
    return JobEstimate(kind=req.kind, estimated_calls=calls, detail=detail)


# --------------------------------------------------------------------------
# Job creation
# --------------------------------------------------------------------------
def _new_job_id() -> str:
    return f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"


def create_job(req: JobRequest) -> JobCreateResult:
    """Validate, persist as ``queued`` and enqueue. Refuses unconfirmed runs."""
    if not req.confirm:
        raise ValueError(
            "refusing to start a token-costly run.py job: 'confirm' must be true. "
            "Call POST /jobs/estimate first and echo the confirmed request."
        )
    if req.count is not None and int(req.count) > MAX_HOUSEHOLDS:
        raise ValueError(
            f"count must be <= {MAX_HOUSEHOLDS} (research rule: max "
            f"{MAX_HOUSEHOLDS} households per world); got {req.count}"
        )
    if req.count is not None and int(req.count) < 1:
        raise ValueError(f"count must be >= 1; got {req.count}")

    argv, warnings = _argv_and_warnings(req)
    est = estimate(req)
    job_id = _new_job_id()
    job = JobInfo(
        id=job_id,
        kind=req.kind,
        status="queued",
        created_at=_now(),
        argv=argv,
        world=req.world or req.env,
        log_path=_log_path(job_id),
        line_count=0,
    )

    with _lock:
        _jobs[job_id] = job
        _recent[job_id] = deque(maxlen=RECENT_LINES)
        _line_counts[job_id] = 0
        _persist(job)

    header = [
        f"===== job {job_id} ({req.kind}) queued at {job.created_at} =====",
        f"$ {subprocess.list2cmdline(argv)}",
    ]
    header += [f"[warn] {w}" for w in warnings]
    header.append("")
    _append_log_lines(job_id, header)

    _ensure_worker()
    _queue.put(job_id)
    return JobCreateResult(job=_copy(job), estimate=est)


# --------------------------------------------------------------------------
# Queries
# --------------------------------------------------------------------------
def list_jobs() -> List[JobInfo]:
    """All known jobs, newest first."""
    with _lock:
        jobs = [_copy(job) for job in _jobs.values()]
    jobs.sort(key=lambda j: (j.created_at or "", j.id), reverse=True)
    return jobs


def get_job(job_id: str) -> Optional[JobInfo]:
    with _lock:
        job = _jobs.get(job_id)
        return None if job is None else _copy(job)


def read_log(job_id: str, offset_lines: int = 0) -> Tuple[List[str], int]:
    """Return ``(lines_from_offset, total_line_count)`` for a job log."""
    try:
        offset = max(0, int(offset_lines or 0))
    except (TypeError, ValueError):
        offset = 0

    lines: Optional[List[str]] = None
    try:
        with open(_log_path(job_id), encoding="utf-8", errors="replace") as fh:
            lines = [line.rstrip("\r\n") for line in fh]
    except OSError:
        lines = None

    if lines is None:
        with _lock:
            buf = _recent.get(job_id)
            lines = list(buf) if buf is not None else []
    return lines[offset:], len(lines)


# --------------------------------------------------------------------------
# Cancellation
# --------------------------------------------------------------------------
def cancel_job(job_id: str) -> Optional[JobInfo]:
    """Cancel a queued/running job. Returns the updated JobInfo (None if unknown)."""
    proc: Optional["subprocess.Popen[str]"] = None
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        if job.status in TERMINAL_STATUSES:
            return _copy(job)
        proc = _procs.get(job_id)
        if job.status == "queued" and proc is None:
            job.status = "cancelled"
            job.error = "cancelled before start"
            job.finished_at = _now()
            _persist(job)
            _append_log_lines(job_id, ["[cancel] cancelled before start"])
            return _copy(job)
        # Running: mark intent first so the worker does not overwrite it.
        job.status = "cancelled"
        job.error = "cancelled by user"
        _persist(job)

    _append_log_lines(job_id, ["[cancel] requested by user; terminating process"])

    if proc is not None and proc.poll() is None:
        try:
            proc.terminate()
            try:
                proc.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    proc.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    pass
        except OSError:
            pass

    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        job.finished_at = job.finished_at or _now()
        if proc is not None and proc.returncode is not None:
            job.exit_code = proc.returncode
        _persist(job)
        return _copy(job)


# --------------------------------------------------------------------------
# Worker
# --------------------------------------------------------------------------
def _ensure_worker() -> threading.Thread:
    """Start the single serial worker thread lazily (idempotent)."""
    global _worker
    if _worker is not None and _worker.is_alive():
        return _worker
    with _worker_lock:
        if _worker is None or not _worker.is_alive():
            thread = threading.Thread(target=_worker_loop, name="job-worker", daemon=True)
            _worker = thread
            thread.start()
    return _worker


def _worker_loop() -> None:
    while True:
        job_id = _queue.get()
        try:
            _run_job(job_id)
        except Exception as exc:  # noqa: BLE001 - the queue must never die
            with _lock:
                job = _jobs.get(job_id)
                if job is not None and job.status not in TERMINAL_STATUSES:
                    job.status = "failed"
                    job.error = f"{type(exc).__name__}: {exc}"
                    job.finished_at = _now()
                    _persist(job)
            _append_log_lines(job_id, [f"[error] runner crashed: {type(exc).__name__}: {exc}"])
        finally:
            _queue.task_done()


def _run_job(job_id: str) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is None or job.status != "queued":
            return  # cancelled before it started
        job.status = "running"
        job.started_at = _now()
        _persist(job)
        argv = list(job.argv)

    _append_log_lines(
        job_id,
        [f"[started] {_now()}", f"[argv] {subprocess.list2cmdline(argv)}", ""],
    )

    try:
        proc: "subprocess.Popen[str]" = subprocess.Popen(
            argv,
            cwd=paths.LLMWORLD_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except OSError as exc:
        _append_log_lines(job_id, [f"[error] failed to start process: {exc}"])
        with _lock:
            job = _jobs.get(job_id)
            if job is not None:
                job.status = "failed"
                job.error = f"failed to start: {exc}"
                job.finished_at = _now()
                _persist(job)
        return

    with _lock:
        _procs[job_id] = proc
        current = _jobs.get(job_id)
        cancelled_early = current is not None and current.status == "cancelled"

    if cancelled_early:
        # cancel_job() ran in the window between the status flip and Popen.
        try:
            proc.terminate()
            try:
                proc.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                proc.kill()
        except OSError:
            pass

    try:
        if proc.stdout is not None:
            with open(
                _log_path(job_id), "a", encoding="utf-8", errors="replace", buffering=1
            ) as fh:
                seen = 0
                for raw in proc.stdout:
                    line = raw.rstrip("\r\n")
                    fh.write(line + "\n")
                    with _lock:
                        buf = _recent.get(job_id)
                        if buf is not None:
                            buf.append(line)
                        _line_counts[job_id] = _line_counts.get(job_id, 0) + 1
                    seen += 1
                    if seen % _PERSIST_EVERY_LINES == 0:
                        with _lock:
                            snapshot = _jobs.get(job_id)
                            if snapshot is not None:
                                snapshot.line_count = _line_counts.get(job_id, 0)
                                _persist(snapshot)
        proc.wait()
    finally:
        final_status = "?"
        with _lock:
            _procs.pop(job_id, None)
            job = _jobs.get(job_id)
            if job is not None:
                job.exit_code = proc.returncode
                job.finished_at = job.finished_at or _now()
                if job.status == "running":
                    if proc.returncode == 0:
                        job.status = "done"
                    else:
                        job.status = "failed"
                        job.error = f"run.py exited with code {proc.returncode}"
                job.line_count = _line_counts.get(job_id, job.line_count)
                _persist(job)
                final_status = job.status
        _append_log_lines(
            job_id,
            [f"[exit] code={proc.returncode} status={final_status} at {_now()}"],
        )


# --------------------------------------------------------------------------
# Startup: rehydrate history
# --------------------------------------------------------------------------
def _load_jobs() -> None:
    """Load persisted jobs. Jobs left running/queued by a dead process are failed."""
    if not os.path.isdir(JOBS_DIR):
        return
    for name in sorted(os.listdir(JOBS_DIR)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(JOBS_DIR, name)
        try:
            with open(path, encoding="utf-8") as fh:
                job = JobInfo(**json.load(fh))
        except (OSError, ValueError):
            continue
        if job.status in ("running", "queued"):
            job.status = "failed"
            job.error = "interrupted"
            job.finished_at = job.finished_at or _now()
            _persist(job)
            _append_log_lines(job.id, ["[error] interrupted: server restarted while job was active"])
        _jobs[job.id] = job
        _recent[job.id] = deque(maxlen=RECENT_LINES)
        _line_counts[job.id] = _count_lines(_log_path(job.id))


_load_jobs()


# --------------------------------------------------------------------------
# Self-test: build argv + estimates + rejection guards (no job is launched)
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import pprint

    print("=== build_argv: world ===")
    world_req = JobRequest(
        kind="world",
        world="world_demo",
        world_config="Melbourne",
        count=2,
        seed=42,
        workers=2,
    )
    pprint.pprint(build_argv(world_req))

    print("\n=== build_argv: simulate (every field populated) ===")
    sim_req = JobRequest(
        kind="simulate",
        world="world_143345",
        date="2026-09-14",
        days=2,
        house="house_0001,house_0002",
        env="world_143345",
        member="Member 1",
        workers=3,
        policy="tou",
        policy_schedule=["2026-09-14,2026-09-15,tou"],
        event=["2026-09-14|heatwave|40C"],
        event_template=["2026-09-15|heatwave"],
        community_notice=["2026-09-14|notice|save power"],
        s4_only=True,
        cost_context=True,
        cost_context_mode="soft",
        price_sensitivity="high",
        natural_ev=True,
        peer_nudge=True,
        bill_feedback=True,
        temperature=0.7,
        no_thinking=True,
        reasoning_effort="low",
    )
    pprint.pprint(build_argv(sim_req))

    print("\n=== build_argv: simulate without date (defaults to today + warning) ===")
    pprint.pprint(build_argv(JobRequest(kind="simulate", world="world_143345")))

    print("\n=== estimate: world (count=2) ===")
    print(estimate(world_req).model_dump())

    print("\n=== estimate: simulate (s4_only, 2 days, house_0001+house_0002) ===")
    print(estimate(sim_req).model_dump())

    print("\n=== estimate: simulate (all houses, s1-s4, 1 day) ===")
    print(
        estimate(
            JobRequest(kind="simulate", world="world_143345", date="2026-09-14")
        ).model_dump()
    )

    print("\n=== estimate: simulate (unknown world -> fallback) ===")
    print(
        estimate(
            JobRequest(kind="simulate", world="world_does_not_exist", date="2026-09-14")
        ).model_dump()
    )

    print("\n=== rejection guards (no job must be created) ===")
    guards = (
        ("confirm=False", JobRequest(kind="world", count=1, confirm=False)),
        ("count=9", JobRequest(kind="world", count=9, confirm=True)),
    )
    for label, req in guards:
        try:
            create_job(req)
        except ValueError as exc:
            print(f"REJECTED [{label}]: {exc}")
        else:
            raise SystemExit(f"!!! guard failed, job was created for {label}")

    print("\nself-test complete; no run.py job was launched.")
