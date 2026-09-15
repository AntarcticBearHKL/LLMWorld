"""Read-only index + metadata store for the LLMWorld research console.

Everything here reads the existing simulation output (never writes) and
returns Pydantic models from :mod:`backend.models`.  Catalog scans are
cached with a short TTL (~20s) so browsing the UI does not re-stat
thousands of directories; the expensive appliance registry is cached
permanently per (world_id, house_id) because it is pure.
"""

from __future__ import annotations

import contextlib
import io
import os
import re
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from .models import (
    ApplianceInfo,
    HouseholdInfo,
    MemberInfo,
    RoomInfo,
    RunInfo,
    RunSummary,
    WorldInfo,
)
from .paths import SIMULATION_DIR, WORLDS_DIR

from analyze import dataset  # noqa: E402  (paths.py put src/ on sys.path)

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TTL_SECONDS = 20.0

_CATALOG_CACHE: Dict[str, Tuple[float, Any]] = {}
_CATALOG_LOCK = threading.Lock()

_REGISTRY_CACHE: Dict[Tuple[str, str], Dict[str, Any]] = {}


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
def _cached(key: str, builder: Callable[[], Any]) -> Any:
    now = time.time()
    with _CATALOG_LOCK:
        hit = _CATALOG_CACHE.get(key)
        if hit is not None and (now - hit[0]) < _TTL_SECONDS:
            return hit[1]
    value = builder()
    with _CATALOG_LOCK:
        _CATALOG_CACHE[key] = (time.time(), value)
    return value


def _run_dates(run_dir: str) -> List[str]:
    try:
        names = os.listdir(run_dir)
    except OSError:
        return []
    return sorted(
        name for name in names
        if _DATE_RE.match(name) and os.path.isdir(os.path.join(run_dir, name))
    )


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_optional_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------
# Catalog: runs / worlds
# --------------------------------------------------------------------------
def list_runs() -> List[RunInfo]:
    """One entry per directory under output/simulation/ (newest first)."""
    return _cached("runs", _build_runs)


def _member_names_from_household_or_stages(run: str, date: str, house: str) -> List[str]:
    names = dataset.read_member_names(run, house)
    if names:
        return names
    return dataset._member_names_from_dir(os.path.join(SIMULATION_DIR, run, date, house))


def _has_baseline_decisions(house_dir: str, members: List[str]) -> bool:
    return any(
        os.path.isfile(os.path.join(house_dir, "s4_decisions_%s.json" % member))
        for member in members
    )


def _build_runs() -> List[RunInfo]:
    runs: List[RunInfo] = []
    if not os.path.isdir(SIMULATION_DIR):
        return runs
    try:
        names = sorted(os.listdir(SIMULATION_DIR))
    except OSError:
        return runs

    for name in names:
        if name == "analysis":
            continue
        run_dir = os.path.join(SIMULATION_DIR, name)
        if not os.path.isdir(run_dir):
            continue

        dates = _run_dates(run_dir)
        houses: List[str] = []
        members = set()
        policies = set()
        has_baseline = False
        for date in dates:
            for house in dataset.list_houses(name, name, date):
                house_dir = os.path.join(SIMULATION_DIR, name, date, house)
                house_members = _member_names_from_household_or_stages(name, date, house)
                policies.update(dataset.discover_policy_tags(house_dir))
                if _has_baseline_decisions(house_dir, house_members):
                    has_baseline = True
                if house in houses:
                    continue
                houses.append(house)
                members.update(house_members)

        runs.append(RunInfo(
            run=name,
            dates=dates,
            houses=houses,
            member_count=len(members),
            has_analysis=os.path.isdir(os.path.join(run_dir, "analysis")),
            has_baseline=has_baseline,
            policies=sorted(policies),
            latest_mtime=_as_optional_float(os.path.getmtime(run_dir)),
        ))

    runs.sort(key=lambda info: info.latest_mtime or 0.0, reverse=True)
    return runs


def list_run_summaries() -> List[RunSummary]:
    """Cheap catalog projection: directory counts only, no per-house file reads."""
    return _cached("run-summaries", _build_run_summaries)


def _build_run_summaries() -> List[RunSummary]:
    summaries: List[RunSummary] = []
    if not os.path.isdir(SIMULATION_DIR):
        return summaries
    try:
        names = sorted(os.listdir(SIMULATION_DIR))
    except OSError:
        return summaries
    for name in names:
        if name == "analysis":
            continue
        run_dir = os.path.join(SIMULATION_DIR, name)
        if not os.path.isdir(run_dir):
            continue
        dates = _run_dates(run_dir)
        houses: set[str] = set()
        stems: set[str] = set()
        has_baseline = False
        for date in dates:
            try:
                entries = os.scandir(os.path.join(run_dir, date))
            except OSError:
                continue
            with entries:
                for entry in entries:
                    if not entry.is_dir() or not entry.name.startswith("house_"):
                        continue
                    houses.add(entry.name)
                    try:
                        files = os.listdir(entry.path)
                    except OSError:
                        continue
                    enrich: set[str] = set()
                    for filename in files:
                        if filename.startswith("s3_enrich_") and filename.endswith(".json"):
                            enrich.add(filename[len("s3_enrich_"):-len(".json")])
                    if not enrich:
                        continue
                    stems |= enrich
                    if not has_baseline:
                        for stem in enrich:
                            if os.path.isfile(os.path.join(entry.path, "s4_decisions_%s.json" % stem)):
                                has_baseline = True
                                break
        summaries.append(RunSummary(
            run=name,
            date_count=len(dates),
            house_count=len(houses),
            member_count=len(stems),
            has_baseline=has_baseline,
            has_analysis=os.path.isdir(os.path.join(run_dir, "analysis")),
            latest_mtime=_as_optional_float(os.path.getmtime(run_dir)),
        ))
    summaries.sort(key=lambda item: item.latest_mtime or 0.0, reverse=True)
    return summaries


def query_run_summaries(
    keyword: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[RunSummary]:
    items = list_run_summaries()
    if keyword:
        needle = keyword.strip().lower()
        if needle:
            items = [item for item in items if needle in item.run.lower()]
    if limit is not None and limit > 0:
        items = items[:limit]
    return items


def _playable(item: RunSummary) -> bool:
    return item.has_baseline and item.date_count > 0 and item.house_count > 0


def default_run() -> Optional[RunSummary]:
    """Best run to open when the URL carries no selection."""
    items = list_run_summaries()
    candidates = [item for item in items if _playable(item)]
    if not candidates:
        candidates = [item for item in items if item.date_count > 0 and item.house_count > 0]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda item: (
            int(item.has_analysis),
            item.member_count,
            item.house_count,
            item.date_count,
        ),
    )


def run_meta(run: str) -> Optional[Dict[str, Any]]:
    """Dates / houses / policy tags for one run, or None when it is unknown."""
    return _cached("run-meta:%s" % run, lambda: _build_run_meta(run))


def _build_run_meta(run: str) -> Optional[Dict[str, Any]]:
    run_dir = os.path.join(SIMULATION_DIR, run)
    if not os.path.isdir(run_dir):
        return None
    dates = _run_dates(run_dir)
    houses: List[str] = []
    policies = set()
    for date in dates:
        for house in dataset.list_houses(run, run, date):
            if house not in houses:
                houses.append(house)
            policies.update(dataset.discover_policy_tags(os.path.join(run_dir, date, house)))
    return {
        "run": run,
        "dates": dates,
        "houses": houses,
        "policies": sorted(policies),
    }


def list_worlds() -> List[WorldInfo]:
    """One entry per directory under output/worlds/ (newest first)."""
    return _cached("worlds", _build_worlds)


def _build_worlds() -> List[WorldInfo]:
    worlds: List[WorldInfo] = []
    if not os.path.isdir(WORLDS_DIR):
        return worlds
    try:
        names = sorted(os.listdir(WORLDS_DIR))
    except OSError:
        return worlds

    for name in names:
        world_dir = os.path.join(WORLDS_DIR, name)
        if not os.path.isdir(world_dir):
            continue

        postcode = None
        try:
            children = sorted(os.listdir(world_dir))
        except OSError:
            children = []
        for child in children:
            if os.path.isdir(os.path.join(world_dir, child)):
                postcode = child
                break

        houses: List[str] = []
        if postcode:
            base = os.path.join(world_dir, postcode)
            try:
                houses = sorted(
                    child for child in os.listdir(base)
                    if child.startswith("house_") and os.path.isdir(os.path.join(base, child))
                )
            except OSError:
                houses = []

        worlds.append(WorldInfo(
            world_id=name,
            postcode=postcode,
            houses=houses,
            has_events=os.path.isfile(os.path.join(world_dir, "events.json")),
            latest_mtime=_as_optional_float(os.path.getmtime(world_dir)),
        ))

    worlds.sort(key=lambda info: info.latest_mtime or 0.0, reverse=True)
    return worlds


def world_info(world_id: str) -> Optional[WorldInfo]:
    """Single world entry, or None when the world directory is missing."""
    for info in list_worlds():
        if info.world_id == world_id:
            return info
    return None


# --------------------------------------------------------------------------
# Appliance registry (expensive, pure -> cached forever per house)
# --------------------------------------------------------------------------
def registry(world_id: str, house_id: str) -> Dict[str, Any]:
    """``{unique_id: Appliance}`` built from household.json (stdout muted)."""
    key = (world_id, house_id)
    cached = _REGISTRY_CACHE.get(key)
    if cached is not None:
        return cached

    household = dataset.read_household(world_id, house_id)
    if not isinstance(household, dict):
        raise ValueError("household not found for %s/%s" % (world_id, house_id))

    built = registry_from_household(household)
    _REGISTRY_CACHE[key] = built
    return built


def registry_from_household(household: Dict[str, Any]) -> Dict[str, Any]:
    """Build (and cache) the appliance registry for a household dict."""
    home = household.get("home") if isinstance(household.get("home"), dict) else {}
    member_names = tuple(
        str(member.get("name"))
        for member in (household.get("members") or [])
        if isinstance(member, dict) and member.get("name")
    )
    key = ("household", str(home.get("name")), member_names)
    cached = _REGISTRY_CACHE.get(key)
    if cached is not None:
        return cached

    # create_home_from_household prints dozens of [Dedup] lines - keep logs clean.
    from simulate import create_home_from_household

    with contextlib.redirect_stdout(io.StringIO()):
        built = dict(create_home_from_household(household).appliance_registry)
    _REGISTRY_CACHE[key] = built
    return built


def appliance_info(appliance: Any) -> ApplianceInfo:
    """Adapt a runtime Appliance object to the API contract."""
    try:
        actions = list(appliance.get_available_actions() or [])
    except Exception:  # noqa: BLE001 - an unknown appliance must not break the page
        actions = []
    return ApplianceInfo(
        unique_id=str(getattr(appliance, "unique_id", "")),
        name=str(getattr(appliance, "name", "") or ""),
        type=str(getattr(appliance, "appliance_type", "") or ""),
        brand=getattr(appliance, "brand", None),
        room=getattr(appliance, "location", None),
        owner=getattr(appliance, "owner", None),
        power_watts=_as_float(getattr(appliance, "power_watts", 0.0)),
        standby_watts=_as_float(getattr(appliance, "standby_watts", 0.0)),
        is_exclusive=bool(getattr(appliance, "is_exclusive", False)),
        available_actions=[str(action) for action in actions],
    )


# --------------------------------------------------------------------------
# Household metadata
# --------------------------------------------------------------------------
def world_household(world_id: str, house_id: str) -> HouseholdInfo:
    """Household metadata without building the appliance registry."""
    household = dataset.read_household(world_id, house_id)
    if not isinstance(household, dict):
        raise ValueError("household not found for %s/%s" % (world_id, house_id))
    return _household_info(world_id, house_id, household, with_appliances=False)


def household_info(world_id: str, house_id: str) -> HouseholdInfo:
    """Household metadata + the appliance registry."""
    household = dataset.read_household(world_id, house_id)
    if not isinstance(household, dict):
        raise ValueError("household not found for %s/%s" % (world_id, house_id))
    return _household_info(world_id, house_id, household, with_appliances=True)


def _household_info(
    world_id: str,
    house_id: str,
    household: Dict[str, Any],
    with_appliances: bool,
) -> HouseholdInfo:
    home = household.get("home") if isinstance(household.get("home"), dict) else {}
    rooms = [
        str(room.get("name"))
        for room in (home.get("rooms") or [])
        if isinstance(room, dict) and room.get("name")
    ]
    room_meta = [
        RoomInfo(name=str(room.get("name")), size=_as_optional_float(room.get("size")))
        for room in (home.get("rooms") or [])
        if isinstance(room, dict) and room.get("name")
    ]
    members = [
        _member_info(member)
        for member in (household.get("members") or [])
        if isinstance(member, dict) and member.get("name")
    ]

    appliances: List[ApplianceInfo] = []
    if with_appliances:
        for appliance in registry(world_id, house_id).values():
            appliances.append(appliance_info(appliance))

    return HouseholdInfo(
        run=world_id,
        house=house_id,
        household_type=str(household.get("type") or "?"),
        season=household.get("season"),
        story=household.get("story"),
        home_name=home.get("name"),
        home_type=home.get("type"),
        home_size=_as_optional_float(home.get("size")),
        rooms=rooms,
        room_meta=room_meta,
        members=members,
        appliances=appliances,
    )


def _member_info(member: Dict[str, Any]) -> MemberInfo:
    personality = member.get("personality")
    if not isinstance(personality, dict):
        personality = {}

    big_five: Dict[str, float] = {}
    raw_big_five = personality.get("big_five")
    if isinstance(raw_big_five, dict):
        for trait, value in raw_big_five.items():
            number = _as_optional_float(value)
            if number is not None:
                big_five[str(trait)] = number

    awareness = personality.get("energy_awareness")
    return MemberInfo(
        id=str(member.get("name")),
        age=_as_int(member.get("age")),
        gender=member.get("gender"),
        occupation=member.get("occupation"),
        bedroom=member.get("bedroom"),
        energy_awareness=str(awareness) if awareness is not None else None,
        big_five=big_five,
        persona=_persona(member),
    )


def _persona(member: Dict[str, Any]) -> str:
    """A short readable summary of personality / habits for the UI."""
    personality = member.get("personality")
    if not isinstance(personality, dict):
        personality = {}
    habits = member.get("habits")
    if not isinstance(habits, dict):
        habits = {}

    parts: List[str] = []
    if personality.get("mbti"):
        parts.append(str(personality["mbti"]))

    traits = personality.get("traits")
    if isinstance(traits, (list, tuple)):
        traits = ", ".join(str(trait) for trait in list(traits)[:4])
    if traits:
        parts.append(str(traits))

    if personality.get("behavior_text"):
        parts.append(str(personality["behavior_text"]))

    if not parts:
        scalars = [
            "%s: %s" % (key, value)
            for key, value in personality.items()
            if key not in ("big_five", "energy_awareness", "traits", "mbti")
            and isinstance(value, (str, int, float))
        ][:3]
        parts.extend(scalars)

    if not parts:
        raw_big_five = personality.get("big_five")
        if isinstance(raw_big_five, dict) and raw_big_five:
            summary = ", ".join(
                "%s %.2f" % (key, value)
                for key, value in raw_big_five.items()
                if isinstance(value, (int, float))
            )
            if summary:
                parts.append("Big five: " + summary)

    habit_bits = [
        "%s: %s" % (key, value)
        for key, value in habits.items()
        if isinstance(value, (str, int, float))
    ][:2]
    if habit_bits:
        parts.append("Habits - " + "; ".join(habit_bits))

    text = ". ".join(part.strip() for part in parts if part and part.strip())
    return text[:400]
