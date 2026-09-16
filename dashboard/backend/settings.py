"""Dashboard runtime settings: the model + LLM knobs, persisted to settings.json.

Values are injected into every spawned job as ``LLMWORLD_*`` environment
variables, which ``src/config.py`` reads, so a change applies to the NEXT job
without editing research code. ``dashboard/settings.json`` is gitignored and
never holds a secret.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Tuple

from . import paths, world_admin
from .models import JobInfo, Settings

SETTINGS_PATH = os.path.join(paths.DASHBOARD_DIR, "settings.json")

_FIELDS: Dict[str, Tuple[str, Any, Any]] = {
    "model": ("LLMWORLD_MODEL", str, "deepseek-v4-flash"),
    "temperature": ("LLMWORLD_TEMPERATURE", float, 1.0),
    "max_tokens": ("LLMWORLD_MAX_TOKENS", int, 64000),
    "request_timeout_seconds": ("LLMWORLD_REQUEST_TIMEOUT", int, 600),
    "max_retries": ("LLMWORLD_MAX_RETRIES", int, 3),
    "retry_backoff_seconds": ("LLMWORLD_RETRY_BACKOFF", float, 2.0),
}


def defaults() -> Dict[str, Any]:
    return {name: default for name, (_var, _caster, default) in _FIELDS.items()}


def _coerce(name: str, value: Any) -> Any:
    caster = _FIELDS[name][1]
    if value is None:
        return _FIELDS[name][2]
    try:
        if caster is str:
            text = str(value).strip()
            return text or _FIELDS[name][2]
        return caster(value)
    except (TypeError, ValueError):
        raise ValueError("invalid value for %s: %r" % (name, value))


def load_settings() -> Dict[str, Any]:
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, ValueError):
        raw = {}
    stored = raw if isinstance(raw, dict) else {}
    return {name: _coerce(name, stored.get(name)) for name in _FIELDS}


def save_settings(updates: Dict[str, Any]) -> Dict[str, Any]:
    unknown = sorted(set(updates) - set(_FIELDS))
    if unknown:
        raise ValueError("unknown setting(s): %s" % ", ".join(unknown))
    current = load_settings()
    for name, value in updates.items():
        current[name] = _coerce(name, value)
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as fh:
        json.dump(current, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return current


def env_overrides() -> Dict[str, str]:
    values = load_settings()
    return {_FIELDS[name][0]: str(values[name]) for name in _FIELDS}


def job_env(job: JobInfo) -> Dict[str, str]:
    """Parent env plus the settings overrides, plus the per-job LLM trace path."""
    env = dict(os.environ)
    env.update(env_overrides())
    if job.kind == "build" and job.world and job.id:
        try:
            world_id = world_admin.normalize_world_id(job.world)
        except ValueError:
            world_id = ""
        if world_id:
            env["LLM_TRACE_FILE"] = world_admin.llm_trace_path(
                world_id, job.id, job.district
            )
    return env


def describe() -> Settings:
    return Settings(**load_settings())
