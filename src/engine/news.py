"""Preset news/event templates and natural-language injection helpers.

Events are told to the AI residents as text; the behavioural effect must emerge
from the agents (intervention_experiment_guide.md §5). The rendered block is
passed to the s1/s4 prompts via the ``world_news`` placeholder. Persisted events
are written to ``<world_dir>/events.json`` so
``src/analyze/analyze_event_response.py`` can align behaviour shifts to dates.
"""

import json
import os

NEWS_TEMPLATES = {
    "heatwave": {
        "title": "Heatwave warning",
        "content": "A severe heatwave is forecast, with daytime temperatures above 38C for the next three days.",
    },
    "cold_snap": {
        "title": "Cold snap",
        "content": "A cold snap is forecast, with overnight temperatures dropping close to 2C this week.",
    },
    "storm": {
        "title": "Severe storm",
        "content": "A severe storm is expected this evening, with possible local power outages.",
    },
    "price_hike": {
        "title": "Electricity price rise",
        "content": "Electricity prices are announced to rise by 8% from tomorrow.",
    },
    "energy_crisis": {
        "title": "Supply margin warning",
        "content": "The grid operator has warned of a tight electricity supply margin this week.",
    },
    "ac_tax": {
        "title": "Air-conditioner peak tax",
        "content": "A 10% tax on air-conditioner use during the evening peak takes effect today.",
    },
    "rebate": {
        "title": "Energy-saving rebate",
        "content": "A rebate is available to households that lower their use during peak hours this month.",
    },
    "blackout_risk": {
        "title": "Rolling blackout warning",
        "content": "The grid operator warns of possible rolling blackouts during the evening peak.",
    },
    "solar_incentive": {
        "title": "Rooftop solar subsidy",
        "content": "A new subsidy for rooftop solar panels has been announced for this suburb.",
    },
    "lockdown": {
        "title": "Public-health lockdown",
        "content": "A public-health lockdown begins today; residents are asked to stay at home.",
    },
    "holiday": {
        "title": "Public holiday",
        "content": "Today is a public holiday; most workplaces and schools are closed and people are staying at home.",
    },
    "wfh": {
        "title": "Work-from-home day",
        "content": "Today is a work-from-home day; many residents are working from home instead of commuting to the office.",
    },
}


# Preset events also shift the environment so the text and the structured
# weather fields agree; otherwise agents may ignore the news (see R014 finding).
EVENT_WEATHER_EFFECTS = {
    "heatwave": {"weather": "Heatwave", "temperature_delta": 12},
    "cold_snap": {"weather": "ColdSnap", "temperature_delta": -10},
}


def list_templates():
    return sorted(NEWS_TEMPLATES)


def _event(date, title, content):
    return {"date": str(date).strip(), "title": str(title).strip(), "content": str(content).strip()}


def weather_override_for(active_events):
    """Merged weather override implied by active preset events (None if none)."""
    weather = None
    delta = 0
    found = False
    for event in active_events or []:
        effect = EVENT_WEATHER_EFFECTS.get((event or {}).get("template"))
        if not effect:
            continue
        found = True
        weather = effect["weather"]
        delta += effect["temperature_delta"]
    if not found:
        return None
    return {"weather": weather, "temperature_delta": delta}


def parse_event_spec(spec):
    """Parse a God-injected event ``"date|title|content"`` into an event dict."""
    if not spec:
        return None
    parts = str(spec).split("|", 2)
    if len(parts) < 3 or not parts[0].strip() or not parts[1].strip():
        raise ValueError(f"Bad event spec '{spec}'; expected 'date|title|content'")
    return _event(parts[0], parts[1], parts[2])


def parse_event_template_spec(spec):
    """Parse a preset event ``"date|template"`` into an event dict."""
    if not spec:
        return None
    parts = str(spec).split("|", 1)
    if len(parts) < 2 or not parts[0].strip():
        raise ValueError(f"Bad event-template spec '{spec}'; expected 'date|template'")
    name = parts[1].strip().lower()
    template = NEWS_TEMPLATES.get(name)
    if template is None:
        raise ValueError(f"Unknown event template '{name}'. Known: {', '.join(list_templates())}")
    event = _event(parts[0], template["title"], template["content"])
    event["template"] = name
    return event


def parse_events(event_specs=None, template_specs=None):
    events = []
    for spec in event_specs or []:
        parsed = parse_event_spec(spec)
        if parsed:
            events.append(parsed)
    for spec in template_specs or []:
        parsed = parse_event_template_spec(spec)
        if parsed:
            events.append(parsed)
    return events


def events_for_date(events, date, keep=5):
    """Most recent ``keep`` events dated on or before *date*, oldest first."""
    window = [e for e in events or [] if isinstance(e, dict) and e.get("date") and e["date"] <= date]
    window.sort(key=lambda e: e["date"])
    if keep and keep > 0:
        window = window[-keep:]
    return window


def render_world_news(active_events):
    if not active_events:
        return ""
    lines = ["Recent news and events in your area:"]
    for event in active_events:
        lines.append(f"- ({event.get('date')}) {event.get('title')}: {event.get('content')}")
    return "\n".join(lines)


def write_events_json(world_dir, events):
    os.makedirs(world_dir, exist_ok=True)
    path = os.path.join(world_dir, "events.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"events": list(events or [])}, f, ensure_ascii=False, indent=2)
    return path


def load_events_json(world_dir):
    path = os.path.join(world_dir, "events.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    events = data.get("events") if isinstance(data, dict) else data
    return events if isinstance(events, list) else []
