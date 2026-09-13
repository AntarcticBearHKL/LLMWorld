"""Concrete cost/tariff context for the s4 appliance-decision prompt.

Given a structured tariff (peak/valley rates + windows) and the household's
flexible appliances, render a money table (cost now vs off-peak) that is injected
into the decision prompt. This supplies the explicit economic trade-off the agents
otherwise lack; the decision itself remains emergent (no hardcoded behaviour).
"""


_SENSITIVITY_NOTES = {
    "high": "You are highly cost-conscious and will accept some inconvenience to cut your electricity bill.",
    "low": "You are not very price-sensitive; comfort and convenience matter more than the bill.",
}


def _in_window(minute, window):
    start = int(window[0][:2]) * 60 + int(window[0][3:])
    end = int(window[1][:2]) * 60 + int(window[1][3:])
    if start <= end:
        return start <= minute < end
    return minute >= start or minute < end


def rate_for_minute(minute, tariff):
    """Tariff rate (AUD/kWh) applying at a given minute of the day."""
    if _in_window(minute, tariff.get("peak_window", ("16:00", "21:00"))):
        return float(tariff["peak_rate"])
    if _in_window(minute, tariff.get("valley_window", ("22:00", "07:00"))):
        return float(tariff["valley_rate"])
    return float(tariff.get("shoulder_rate", tariff["valley_rate"]))


def cost_from_profile(profile_watts, tariff):
    """(total_cost, peak_cost) in AUD for a per-minute watts profile; None if unusable."""
    if not tariff or not profile_watts:
        return None
    peak_window = tariff.get("peak_window", ("16:00", "21:00"))
    total = peak = 0.0
    for minute, watts in enumerate(profile_watts):
        cost = (watts / 60.0 / 1000.0) * rate_for_minute(minute, tariff)
        total += cost
        if _in_window(minute, peak_window):
            peak += cost
    return total, peak


def render_bill_feedback(total_cost, peak_cost):
    """Yesterday's-bill feedback sentence ('' when the cost is unavailable)."""
    if total_cost is None:
        return ""
    return (
        f"Yesterday your household electricity cost about {total_cost:.2f} AUD, of which "
        f"{peak_cost:.2f} AUD was during the peak window. Use this to decide when to run "
        "flexible appliances today."
    )


def sensitivity_note(sensitivity):
    """Preference sentence for a price-sensitivity level ('' when unknown/none)."""
    return _SENSITIVITY_NOTES.get(str(sensitivity or "").lower(), "")


def _unit_energy_kwh(appliance):
    """Energy of one representative unit of use: cycle kWh, else per-hour kWh."""
    cycle = appliance.get("energy_per_cycle_kwh")
    if cycle:
        return float(cycle), "per cycle"
    power = appliance.get("power_watts")
    if power:
        return float(power) / 1000.0, "per hour"
    return None, None


def render_cost_context(home_details, tariff):
    """Render the flexible-appliance cost table ('' when nothing applies)."""
    if not tariff:
        return ""
    peak_rate = float(tariff.get("peak_rate") or 0.0)
    valley_rate = float(tariff.get("valley_rate") or 0.0)
    rows = []
    for section in (home_details or {}).values():
        for appliance in section.get("appliances", []):
            if not appliance.get("flexible") or appliance.get("type") == "always_on":
                continue
            kwh, unit = _unit_energy_kwh(appliance)
            if not kwh:
                continue
            cost_peak = kwh * peak_rate
            cost_valley = kwh * valley_rate
            rows.append(
                f"- {appliance.get('unique_id')}: {cost_peak:.2f} AUD now (peak) vs "
                f"{cost_valley:.2f} AUD off-peak — save {cost_peak - cost_valley:.2f} {unit}"
            )
    if not rows:
        return ""
    window_p = tariff.get("peak_window", ("16:00", "21:00"))
    window_v = tariff.get("valley_window", ("22:00", "07:00"))
    header = (
        f"Flexible-appliance costs under today's tariff "
        f"(peak {window_p[0]}-{window_p[1]} @{peak_rate:.2f} AUD/kWh; "
        f"off-peak {window_v[0]}-{window_v[1]} @{valley_rate:.2f} AUD/kWh):"
    )
    trailer = (
        "To minimise cost: if a flexible appliance would otherwise run in the peak window, you MAY "
        "move it to an off-peak segment earlier or later the same day (for example run the dishwasher "
        "overnight, or shower before 16:00) — the activity still happens, only its time changes. Keep "
        "it in the peak window only if the activity genuinely cannot move."
    )
    return "\n".join([header] + rows + [trailer])
