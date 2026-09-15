"""Turn stored s4 decisions into replay payloads (read-only).

The heavy lifting already lives in ``analyze.dataset`` and
``analyze.load_model``; this module only reshapes their output into the
Pydantic contract in :mod:`backend.models`, adding per-minute appliance
series, interval compression and point-in-time snapshots.
"""

from __future__ import annotations

import contextlib
import io
import os
from typing import Any, Dict, List, Optional, Tuple

from . import store
from .models import (
    ActivitySegment,
    ApplianceDay,
    ApplianceInterval,
    DayMetrics,
    DayReplay,
    DecisionSegment,
    MemberDay,
    MemberInfo,
    Operation,
    Snapshot,
    SnapshotAppliance,
    SnapshotHouse,
    SnapshotPerson,
    StagePayload,
)
from .paths import SIMULATION_DIR

from analyze import dataset  # noqa: E402  (paths.py put src/ on sys.path)
from analyze.load_model import _accumulate  # noqa: E402
from appliances.base import AlwaysOnAppliance, ChargingAppliance  # noqa: E402
from engine.utils import parse_time_range  # noqa: E402

MINUTES_PER_DAY = 1440
_EPS = 1e-9
_RUN_EPS = 1e-6
_STAGE_TOKENS = ("s1", "s2", "s3", "s4")

_DAY_CACHE: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
_DAY_CACHE_MAX = 256


# --------------------------------------------------------------------------
# Per-appliance minute series
# --------------------------------------------------------------------------
def _series_and_actions(
    household: Dict[str, Any],
    decisions_by_member: Dict[str, List[Dict[str, Any]]],
    registry: Dict[str, Any],
) -> Tuple[Dict[str, List[float]], Dict[Tuple[str, int], Tuple[float, str]]]:
    """Replicate ``build_load_profile``'s per-appliance adjustments.

    ``_accumulate`` handles operations, daily caps and battery clamping;
    this adds the always-on baseload and the standby fill so that the sum
    of the returned arrays equals the household profile exactly.
    """
    contrib, referenced, best_action = _accumulate(registry, decisions_by_member)
    series: Dict[str, List[float]] = {}

    for unique_id, appliance in registry.items():
        minutes = contrib[unique_id]
        if isinstance(appliance, AlwaysOnAppliance):
            baseload = (getattr(appliance, "daily_energy_kwh", 0.0) or 0.0) / 24.0 * 1000.0
            minutes = [baseload] * MINUTES_PER_DAY
        elif isinstance(appliance, ChargingAppliance):
            pass  # charging appliances keep their accumulated series as-is
        else:
            standby = appliance.standby_watts or 0.0
            if standby:
                for minute in range(MINUTES_PER_DAY):
                    if not referenced[unique_id][minute]:
                        minutes[minute] = standby
        series[unique_id] = minutes

    return series, best_action


def appliance_series(
    household: Dict[str, Any],
    decisions_by_member: Dict[str, List[Dict[str, Any]]],
    registry: Optional[Dict[str, Any]] = None,
) -> Dict[str, List[float]]:
    """``{unique_id: [watts per minute]}`` for one household-day."""
    if registry is None:
        registry = store.registry_from_household(household)
    series, _best = _series_and_actions(household, decisions_by_member, registry)
    return series


# --------------------------------------------------------------------------
# Interval compression
# --------------------------------------------------------------------------
def to_intervals(
    minutes: List[float],
    best_action: Dict[Tuple[str, int], Tuple[float, str]],
    unique_id: str,
) -> List[ApplianceInterval]:
    """Compress consecutive equal-watt runs into ``[start, end)`` intervals."""
    intervals: List[ApplianceInterval] = []
    total = len(minutes)
    index = 0

    while index < total:
        watts = minutes[index]
        end = index + 1
        while end < total and abs(minutes[end] - watts) <= _RUN_EPS:
            end += 1

        if abs(watts) > _EPS:
            actions = set()
            complete = True
            for minute in range(index, end):
                entry = best_action.get((unique_id, minute))
                if entry is None:
                    complete = False
                    break
                actions.add(entry[1])
            action = next(iter(actions)) if (complete and len(actions) == 1) else None
            intervals.append(ApplianceInterval(
                start=index, end=end, watts=float(watts), action=action,
            ))

        index = end

    return intervals


# --------------------------------------------------------------------------
# Day derivation (cached - a snapshot needs every house of a day)
# --------------------------------------------------------------------------
def _derive_day(run: str, date: str, house: str, policy: str = "baseline") -> Dict[str, Any]:
    key = (run, date, house, policy)
    cached = _DAY_CACHE.get(key)
    if cached is not None:
        return cached

    record = None
    # The library builds the appliance registry (and prints [Dedup]/[Warn] lines)
    # lazily on the first next(); mute it so API logs stay clean.
    with contextlib.redirect_stdout(io.StringIO()):
        for candidate in dataset.iter_house_days(run, date=date, policy=policy, houses=[house]):
            record = candidate
            break
    if record is None:
        raise ValueError(
            "no decisions for run=%s date=%s house=%s policy=%s" % (run, date, house, policy)
        )

    registry = store.registry(run, house)
    series, best_action = _series_and_actions(
        record["household"], record["decisions"], registry,
    )
    data = {
        "record": record,
        "registry": registry,
        "series": series,
        "best_action": best_action,
        "info": store.household_info(run, house),
    }
    if len(_DAY_CACHE) >= _DAY_CACHE_MAX:
        _DAY_CACHE.pop(next(iter(_DAY_CACHE)))
    _DAY_CACHE[key] = data
    return data


def _segment_bounds(segment: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
    start = segment.get("start_minutes")
    end = segment.get("end_minutes")
    if start is None or end is None:
        try:
            start, end = parse_time_range(segment.get("time") or "")
        except Exception:  # noqa: BLE001 - malformed timestamps are skipped
            return None, None
    if start is None or end is None:
        return None, None
    return int(start), int(end)


def _metrics(profile: List[float], total_kwh: float) -> DayMetrics:
    if not profile:
        return DayMetrics(total_kwh=total_kwh)
    peak_watts = max(profile)
    peak_minute = profile.index(peak_watts)
    mean_watts = sum(profile) / len(profile)
    load_factor = (mean_watts / peak_watts) if peak_watts > 0 else None
    return DayMetrics(
        total_kwh=float(total_kwh),
        peak_watts=float(peak_watts),
        peak_minute=int(peak_minute),
        peak_window_kwh=sum(profile[1020:1200]) / 60.0 / 1000.0,
        evening_kwh=sum(profile[1080:1380]) / 60.0 / 1000.0,
        load_factor=load_factor,
    )


def build_day_replay(run: str, date: str, house: str, policy: str = "baseline") -> DayReplay:
    """Everything needed to render one (run, date, house) day."""
    data = _derive_day(run, date, house, policy)
    record = data["record"]
    registry = data["registry"]
    series = data["series"]
    best_action = data["best_action"]
    info = data["info"]
    house_dir = record["house_dir"]
    household = record["household"]
    decisions = record.get("decisions") or {}
    activities = record.get("activities") or {}

    warnings: List[str] = []
    members: List[MemberDay] = []
    known = {member.id: member for member in info.members}

    for member in dataset._household_member_names(household):
        segments = decisions.get(member)
        if not segments:
            warnings.append("%s: no decisions for policy '%s'" % (member, policy))

        raw_activities = activities.get(member)
        if raw_activities is None:
            raw_activities = dataset.read_activities(house_dir, member)

        member_activities: List[ActivitySegment] = []
        for item in raw_activities or []:
            if not isinstance(item, dict):
                continue
            start, end = _segment_bounds(item)
            if start is None:
                continue
            member_activities.append(ActivitySegment(
                start=start,
                end=end,
                time=str(item.get("time") or ""),
                location=str(item.get("location") or ""),
                activity=str(item.get("activity") or ""),
                desc=item.get("desc"),
            ))

        member_decisions: List[DecisionSegment] = []
        for item in segments or []:
            if not isinstance(item, dict):
                continue
            start, end = _segment_bounds(item)
            if start is None:
                continue
            operations = [
                Operation(
                    unique_id=str(operation.get("unique_id") or ""),
                    action=str(operation.get("action") or ""),
                )
                for operation in (item.get("operations") or [])
                if isinstance(operation, dict)
            ]
            member_decisions.append(DecisionSegment(
                start=start,
                end=end,
                time=str(item.get("time") or ""),
                location=str(item.get("location") or ""),
                activity=str(item.get("activity") or ""),
                operations=operations,
            ))

        members.append(MemberDay(
            id=member,
            info=known.get(member, MemberInfo(id=member)),
            activities=member_activities,
            decisions=member_decisions,
        ))

    per_appliance_kwh = record.get("per_appliance_kwh") or {}
    appliances: List[ApplianceDay] = []
    for unique_id, appliance in registry.items():
        minutes = series.get(unique_id) or [0.0] * MINUTES_PER_DAY
        appliances.append(ApplianceDay(
            unique_id=unique_id,
            info=store.appliance_info(appliance),
            energy_kwh=float(per_appliance_kwh.get(unique_id, 0.0) or 0.0),
            peak_watts=float(max(minutes)) if minutes else 0.0,
            on_minutes=sum(1 for watts in minutes if watts > _EPS),
            intervals=to_intervals(minutes, best_action, unique_id),
        ))

    profile = [float(watts) for watts in record["load_profile_watts"]]
    return DayReplay(
        run=run,
        date=date,
        house=house,
        policy=policy,
        household=info,
        members=members,
        appliances=appliances,
        total_watts=profile,
        metrics=_metrics(profile, float(record.get("total_energy_kwh") or 0.0)),
        warnings=warnings,
    )


# --------------------------------------------------------------------------
# Snapshot: every house at one minute
# --------------------------------------------------------------------------
def build_snapshot(run: str, date: str, minute: int, policy: str = "baseline") -> Snapshot:
    index = max(0, min(MINUTES_PER_DAY - 1, int(minute)))
    houses: List[SnapshotHouse] = []

    for house in dataset.list_houses(run, run, date):
        try:
            data = _derive_day(run, date, house, policy)
        except ValueError:
            continue

        record = data["record"]
        registry = data["registry"]
        series = data["series"]
        best_action = data["best_action"]
        household = record["household"]
        decisions = record.get("decisions") or {}

        people: List[SnapshotPerson] = []
        for member in household.get("members") or []:
            if not isinstance(member, dict) or not member.get("name"):
                continue
            name = member["name"]
            location, activity = "Out", "Out"
            powered: List[str] = []
            for segment in decisions.get(name) or []:
                if not isinstance(segment, dict):
                    continue
                start, end = _segment_bounds(segment)
                if start is None or not (start <= index < end):
                    continue
                location = str(segment.get("location") or "Out")
                activity = str(segment.get("activity") or "Out")
                for operation in segment.get("operations") or []:
                    if not isinstance(operation, dict):
                        continue
                    unique_id = operation.get("unique_id")
                    if (
                        unique_id in series
                        and series[unique_id][index] > 0
                        and unique_id not in powered
                    ):
                        powered.append(unique_id)
                break
            people.append(SnapshotPerson(
                member=name, location=location, activity=activity, powered=powered,
            ))

        powered_appliances: List[SnapshotAppliance] = []
        total_watts = 0.0
        for unique_id, appliance in registry.items():
            watts = series[unique_id][index]
            total_watts += watts
            if watts > 0:
                entry = best_action.get((unique_id, index))
                powered_appliances.append(SnapshotAppliance(
                    unique_id=unique_id,
                    name=appliance.name,
                    room=appliance.location,
                    owner=appliance.owner,
                    watts=float(watts),
                    action=(entry[1] if entry else None),
                ))

        houses.append(SnapshotHouse(
            house=house,
            household_type=str(household.get("type") or "?"),
            total_watts=total_watts,
            people=people,
            powered=powered_appliances,
        ))

    return Snapshot(run=run, date=date, minute=int(minute), policy=policy, houses=houses)


# --------------------------------------------------------------------------
# Decision-pipeline stages + LLM logs
# --------------------------------------------------------------------------
def _read_json(path: str) -> Any:
    if not os.path.isfile(path):
        return None
    try:
        import json

        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _pick_log(log_dir: str, token: str, member: str) -> Optional[str]:
    try:
        names = sorted(os.listdir(log_dir))
    except OSError:
        return None

    candidates = [
        name for name in names
        if name.endswith(".md") and ("_%s_" % token) in name
    ]
    if not candidates:
        candidates = [name for name in names if name.endswith(".md") and token in name]
    if not candidates:
        return None

    member_tokens = {
        member,
        member.replace(" ", "_"),
        member.lower(),
        member.lower().replace(" ", "_"),
    }
    member_tokens.discard("")
    preferred = [name for name in candidates if any(tok in name for tok in member_tokens)]
    return (preferred or candidates)[0]


def build_stages(run: str, date: str, house: str, member: str) -> StagePayload:
    """s1..s4 JSON payloads plus the matching markdown log excerpts."""
    house_dir = os.path.join(SIMULATION_DIR, run, date, house)
    if not os.path.isdir(house_dir):
        raise ValueError("house dir not found: %s/%s/%s" % (run, date, house))

    payload = StagePayload(
        member=member,
        s1=_read_json(os.path.join(house_dir, "s1_macro_%s.json" % member)),
        s2=_read_json(os.path.join(house_dir, "s2_coord_%s.json" % member)),
        s3=_read_json(os.path.join(house_dir, "s3_enrich_%s.json" % member)),
        s4=_read_json(os.path.join(house_dir, "s4_decisions_%s.json" % member)),
        s4_raw=_read_json(os.path.join(house_dir, "s4_decisions_raw_%s.json" % member)),
        report=_read_json(os.path.join(house_dir, "s4_decision_report_%s.json" % member)),
    )

    log_dir = os.path.join(house_dir, "log")
    logs: Dict[str, str] = {}
    for token in _STAGE_TOKENS:
        name = _pick_log(log_dir, token, member)
        excerpt = ""
        if name:
            try:
                with open(os.path.join(log_dir, name), "r", encoding="utf-8", errors="replace") as handle:
                    excerpt = handle.read(6000)
            except OSError:
                excerpt = ""
        logs[token] = excerpt
    payload.logs = logs
    return payload


# --------------------------------------------------------------------------
# Self-test on real data
# --------------------------------------------------------------------------
if __name__ == "__main__":
    RUN, DATE, HOUSE = "world_838587", "2026-09-11", "house_0001"

    with contextlib.redirect_stdout(io.StringIO()):
        records = list(dataset.iter_house_days(RUN, date=DATE, houses=[HOUSE]))
    print("records:", len(records))
    assert records, "no records found for %s/%s/%s" % (RUN, DATE, HOUSE)

    record = records[0]
    registry = store.registry(RUN, HOUSE)
    series, best_action = _series_and_actions(
        record["household"], record["decisions"], registry,
    )

    profile = record["load_profile_watts"]
    series_total = sum(sum(minutes) for minutes in series.values())
    profile_total = sum(profile)
    print("total_kwh:", record["total_energy_kwh"])
    print("sum(series) - sum(profile):", abs(series_total - profile_total))
    assert abs(series_total - profile_total) < 1e-6, "appliance series do not sum to the profile"

    kwh_sum = sum(record["per_appliance_kwh"].values())
    print("sum(per_appliance_kwh) - total_kwh:", abs(kwh_sum - record["total_energy_kwh"]))

    uid = "kitchen_inductioncooker"
    intervals = to_intervals(series[uid], best_action, uid)
    print("intervals for %s:" % uid, len(intervals))
    for interval in intervals[:5]:
        print(" ", interval.model_dump())

    print("day replay metrics:", build_day_replay(RUN, DATE, HOUSE).metrics.model_dump())
