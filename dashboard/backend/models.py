"""Shared API contract for the LLMWorld Research Console.

This module is the single source of truth for the JSON shapes exchanged
between the FastAPI backend and the React frontend. Both sides MUST conform.

Time convention: every "minute" is an integer in 0..1440 (minutes since
midnight). Segments use half-open ranges [start, end).
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------
# Index / catalog
# --------------------------------------------------------------------------
class RunInfo(BaseModel):
    """One simulation run = one directory under output/simulation/."""

    run: str = Field(..., description="run/env id, e.g. 'world_838587'")
    dates: List[str] = Field(default_factory=list)
    houses: List[str] = Field(default_factory=list)
    member_count: int = 0
    has_analysis: bool = False
    has_baseline: bool = False
    policies: List[str] = Field(default_factory=list)
    latest_mtime: Optional[float] = None


class RunMeta(BaseModel):
    """Compact metadata for one run (no per-house member scan)."""

    run: str
    dates: List[str] = Field(default_factory=list)
    houses: List[str] = Field(default_factory=list)
    policies: List[str] = Field(default_factory=list)


class WorldInfo(BaseModel):
    world_id: str
    postcode: Optional[str] = None
    houses: List[str] = Field(default_factory=list)
    has_events: bool = False
    latest_mtime: Optional[float] = None


class HomeListEntry(BaseModel):
    """A run that can be replayed, grouped for the picker."""

    run: str
    dates: List[str] = Field(default_factory=list)
    houses: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Household metadata
# --------------------------------------------------------------------------
class ApplianceInfo(BaseModel):
    unique_id: str
    name: str
    type: str = Field(..., description="on_demand | charging | always_on | cycle")
    brand: Optional[str] = None
    room: Optional[str] = Field(default=None, description="location, None for personal devices")
    owner: Optional[str] = Field(default=None, description="member name for personal devices")
    power_watts: float = 0.0
    standby_watts: float = 0.0
    is_exclusive: bool = False
    available_actions: List[str] = Field(default_factory=list)


class MemberInfo(BaseModel):
    id: str = Field(..., description="display id, e.g. 'Member 1'")
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    bedroom: Optional[str] = None
    energy_awareness: Optional[str] = None
    big_five: Dict[str, float] = Field(default_factory=dict)
    persona: str = ""
    is_out: bool = False


class RoomInfo(BaseModel):
    name: str
    size: Optional[float] = None


class HouseholdInfo(BaseModel):
    run: str
    house: str
    household_type: str = "?"
    season: Optional[str] = None
    story: Optional[str] = None
    home_name: Optional[str] = None
    home_type: Optional[str] = None
    home_size: Optional[float] = None
    rooms: List[str] = Field(default_factory=list)
    room_meta: List[RoomInfo] = Field(default_factory=list)
    members: List[MemberInfo] = Field(default_factory=list)
    appliances: List[ApplianceInfo] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Replay payload
# --------------------------------------------------------------------------
class ActivitySegment(BaseModel):
    start: int
    end: int
    time: str
    location: str
    activity: str
    desc: Optional[str] = None


class Operation(BaseModel):
    unique_id: str
    action: str = Field(..., description="use | idle | run | charge_home | charge_external")


class DecisionSegment(BaseModel):
    start: int
    end: int
    time: str
    location: str
    activity: str
    operations: List[Operation] = Field(default_factory=list)


class MemberDay(BaseModel):
    id: str
    info: MemberInfo
    activities: List[ActivitySegment] = Field(default_factory=list)
    decisions: List[DecisionSegment] = Field(default_factory=list)


class ApplianceInterval(BaseModel):
    """A contiguous stretch where the appliance draws ``watts``."""

    start: int
    end: int
    watts: float
    action: Optional[str] = None


class ApplianceDay(BaseModel):
    unique_id: str
    info: ApplianceInfo
    energy_kwh: float = 0.0
    peak_watts: float = 0.0
    on_minutes: int = 0
    intervals: List[ApplianceInterval] = Field(default_factory=list)


class DayMetrics(BaseModel):
    total_kwh: float = 0.0
    peak_watts: float = 0.0
    peak_minute: int = 0
    peak_window_kwh: Optional[float] = None
    evening_kwh: Optional[float] = None
    load_factor: Optional[float] = None


class DayReplay(BaseModel):
    """Everything needed to render one (run, date, house) day."""

    run: str
    date: str
    house: str
    policy: str = "baseline"
    household: HouseholdInfo
    members: List[MemberDay] = Field(default_factory=list)
    appliances: List[ApplianceDay] = Field(default_factory=list)
    total_watts: List[float] = Field(default_factory=list, description="1440 values")
    metrics: DayMetrics = Field(default_factory=DayMetrics)
    warnings: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Time-point snapshot (all houses at one minute)
# --------------------------------------------------------------------------
class SnapshotPerson(BaseModel):
    member: str
    location: str
    activity: str
    powered: List[str] = Field(default_factory=list)


class SnapshotAppliance(BaseModel):
    unique_id: str
    name: str
    room: Optional[str] = None
    owner: Optional[str] = None
    watts: float = 0.0
    action: Optional[str] = None


class SnapshotHouse(BaseModel):
    house: str
    household_type: str = "?"
    total_watts: float = 0.0
    people: List[SnapshotPerson] = Field(default_factory=list)
    powered: List[SnapshotAppliance] = Field(default_factory=list)


class Snapshot(BaseModel):
    run: str
    date: str
    minute: int
    policy: str = "baseline"
    houses: List[SnapshotHouse] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Decision-pipeline walkthrough (s1 -> s4) + LLM logs
# --------------------------------------------------------------------------
class StagePayload(BaseModel):
    member: str
    s1: Optional[Any] = None
    s2: Optional[Any] = None
    s3: Optional[Any] = None
    s4: Optional[Any] = None
    s4_raw: Optional[Any] = None
    report: Optional[Any] = None
    logs: Dict[str, str] = Field(
        default_factory=dict, description="stage -> markdown log excerpt"
    )


# --------------------------------------------------------------------------
# Jobs (world generation / simulation control)
# --------------------------------------------------------------------------
class JobRequest(BaseModel):
    kind: Literal["world", "simulate"]
    # world mode
    world: Optional[str] = None
    count: Optional[int] = None
    world_config: Optional[str] = None
    seed: Optional[int] = None
    # simulate mode
    date: Optional[str] = None
    days: Optional[int] = None
    house: Optional[str] = None
    member: Optional[str] = None
    env: Optional[str] = None
    policy: Optional[str] = None
    policy_schedule: List[str] = Field(default_factory=list)
    event: List[str] = Field(default_factory=list)
    event_template: List[str] = Field(default_factory=list)
    community_notice: List[str] = Field(default_factory=list)
    s4_only: bool = False
    cost_context: bool = False
    cost_context_mode: Literal["strong", "soft"] = "strong"
    price_sensitivity: Optional[Literal["low", "high"]] = None
    natural_ev: bool = False
    peer_nudge: bool = False
    bill_feedback: bool = False
    temperature: Optional[float] = None
    no_thinking: bool = False
    reasoning_effort: Optional[Literal["low", "medium", "high"]] = None
    workers: Optional[int] = None
    # client must echo the confirmed estimate before a token-costly run is allowed
    confirm: bool = False


class JobEstimate(BaseModel):
    kind: str
    estimated_calls: int = 0
    detail: str = ""


class JobInfo(BaseModel):
    id: str
    kind: str
    status: Literal["queued", "running", "done", "failed", "cancelled"]
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    argv: List[str] = Field(default_factory=list)
    world: Optional[str] = None
    exit_code: Optional[int] = None
    log_path: Optional[str] = None
    line_count: int = 0
    error: Optional[str] = None


class JobCreateResult(BaseModel):
    job: JobInfo
    estimate: JobEstimate
