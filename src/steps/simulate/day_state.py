"""Day-boundary carry-over state for the simulate pipeline.

Each simulated day is generated independently, so without carry-over a member
can end day N "Out" at 24:00 and start day N+1 asleep at home at 00:00.
This module persists the end-of-day state of a member's s1 macro plan and
reconciles the opening segment of the next day when the member was still out.
"""

import json
import os

OUT_LOCATION = "Out"
COMMUTE_HOME_ACTIVITY = "Commuting home from work"
COMMUTE_HOME_MINUTES = 45


def _is_out(location):
    text = str(location or "").strip().lower()
    return text == "out" or text.startswith("out ") or text.startswith("out(")


def _parse_range(time_str):
    """Parse 'HH:MM-HH:MM' into (start_minutes, end_minutes); None if invalid."""
    text = str(time_str or "").strip()
    if "-" not in text:
        return None
    start_text, _, end_text = text.partition("-")
    try:
        start_h, start_m = [int(p) for p in start_text.strip().split(":")]
        end_h, end_m = [int(p) for p in end_text.strip().split(":")]
    except ValueError:
        return None
    start = start_h * 60 + start_m
    end = end_h * 60 + end_m
    if end <= start:
        return None
    return start, end


def _fmt(minutes):
    minutes = max(0, min(1440, int(minutes)))
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def end_state(activities):
    """Summarise the last (24:00-covering) segment of a day's activity list."""
    if not activities or not isinstance(activities[-1], dict):
        return None
    last = activities[-1]
    location = last.get("location", "")
    return {
        "end_time": last.get("time", ""),
        "end_location": location,
        "end_activity": last.get("activity", ""),
        "ends_out": _is_out(location),
    }


def _state_path(house_dir, member):
    return os.path.join(house_dir, f"day_state_{member}.json")


def load_day_state(house_dir, member=None):
    """Read day_state_<Member>.json from house_dir; None when absent.

    With no member given, fall back to a single day_state_*.json in the dir
    (returns None when there are zero or several, so no wrong member leaks).
    """
    if not house_dir or not os.path.isdir(house_dir):
        return None
    if member is None:
        names = [n for n in os.listdir(house_dir)
                 if n.startswith("day_state_") and n.endswith(".json")]
        if len(names) != 1:
            return None
        path = os.path.join(house_dir, names[0])
    else:
        path = _state_path(house_dir, member)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError):
        return None
    return state if isinstance(state, dict) else None


def save_day_state(house_dir, member, state):
    if state is None:
        return None
    os.makedirs(house_dir, exist_ok=True)
    path = _state_path(house_dir, member)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    return path


def carry_over_text(prev_state, member):
    """Short instruction injected into the s1 prompt; '' when no previous day."""
    if not prev_state:
        return ""
    location = prev_state.get("end_location") or "unknown"
    activity = prev_state.get("end_activity") or "unknown"
    return (
        f"The previous day ended at 24:00 with {member} at {location} doing '{activity}'. "
        "If they were still out at work, the new day must begin with commuting home (Out) "
        "before any at-home activity; if asleep, remain asleep until their normal wake time."
    )


def reconcile_boundary(activities, prev_state):
    """Make the new day start where the previous day ended.

    Rule: when the previous day ended Out and the new day opens with a home
    room, the opening segment is split into a deterministic commute-home
    segment (Out, 00:00 to +COMMUTE_HOME_MINUTES, capped at the segment end),
    followed by the remainder of the original segment. Every other segment is
    copied through untouched, so the day still covers 00:00-24:00 with no gap
    or overlap. If the opening segment is fully consumed by the commute it is
    replaced outright. Returns the same list when nothing needs rewriting.
    """
    if not prev_state or not prev_state.get("ends_out"):
        return activities
    if not activities or not isinstance(activities[0], dict):
        return activities
    first = activities[0]
    if _is_out(first.get("location")):
        return activities
    span = _parse_range(first.get("time"))
    if span is None:
        return activities
    first_start, first_end = span
    if first_start > 0:
        # Non-standard opening: cover the gap 00:00-first_start with the commute.
        commute = {"time": f"00:00-{_fmt(first_start)}", "location": OUT_LOCATION,
                   "activity": COMMUTE_HOME_ACTIVITY}
        return [commute] + [dict(a) if isinstance(a, dict) else a for a in activities]
    commute_end = min(first_start + COMMUTE_HOME_MINUTES, first_end)
    rewritten = [{"time": f"00:00-{_fmt(commute_end)}", "location": OUT_LOCATION,
                  "activity": COMMUTE_HOME_ACTIVITY}]
    if commute_end < first_end:
        tail = dict(first)
        tail["time"] = f"{_fmt(commute_end)}-{_fmt(first_end)}"
        rewritten.append(tail)
    rewritten.extend(dict(a) if isinstance(a, dict) else a for a in activities[1:])
    return rewritten
