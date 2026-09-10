"""Time-of-use (TOU) pricing policy renderer.

Generates the natural-language tariff text that is injected into the s4
appliance-decision prompt via the {policy_context} placeholder. All pricing
interventions follow the guide in intervention_experiment_guide.md: policies are
"told to the AI residents" as text, and effects are emergent agent behaviour.
"""

TOU_DEFAULT = {
    "peak_window": ("16:00", "21:00"),
    "valley_window": ("22:00", "07:00"),
    "peak_rate": 0.60,
    "valley_rate": 0.18,
    "shoulder_rate": 0.35,
}


def _tou_config(peak_rate, valley_rate, shoulder_rate):
    cfg = dict(TOU_DEFAULT)
    if peak_rate is not None:
        cfg["peak_rate"] = peak_rate
    if valley_rate is not None:
        cfg["valley_rate"] = valley_rate
    if shoulder_rate is not None:
        cfg["shoulder_rate"] = shoulder_rate
    return cfg


def _tou_tariff_sentence(cfg):
    peak_from, peak_to = cfg["peak_window"]
    valley_from, valley_to = cfg["valley_window"]
    return (
        "Today your household is on a time-of-use (TOU) electricity tariff: "
        f"peak period {peak_from}-{peak_to} at {cfg['peak_rate']:.2f} AUD/kWh; "
        f"valley period {valley_from}-{valley_to} at {cfg['valley_rate']:.2f} AUD/kWh; "
        f"shoulder period (all other times) at {cfg['shoulder_rate']:.2f} AUD/kWh."
    )


def render_tou_policy(peak_rate=None, valley_rate=None, shoulder_rate=None):
    cfg = _tou_config(peak_rate, valley_rate, shoulder_rate)
    return _tou_tariff_sentence(cfg) + (
        " To reduce your bill, shift flexible appliances (electric vehicle charging, "
        "washing machine, dishwasher-free routines like hot water use) into the valley "
        "period, and avoid running high-power appliances during the peak period unless "
        "necessary."
    )


def render_tou_policy_soft(peak_rate=None, valley_rate=None, shoulder_rate=None):
    """Tariff facts only, with no 'shift/avoid' directive (prompt-bias control)."""
    return _tou_tariff_sentence(_tou_config(peak_rate, valley_rate, shoulder_rate))


def render_nudge_policy(neighbor_kwh=18.0):
    """Social-norm comparison with a fixed neighbour average (guide §3.1)."""
    return (f"Your neighbours use about {neighbor_kwh:.0f} kWh of electricity per day on average. "
            "Most households in your area try to keep their usage near or below this level.")


def render_nudge_loss_policy(rebate=30.0):
    """Loss-framed social norm (guide §3.2): lose a rebate if flagged high-usage."""
    return (f"Households that do not reduce their electricity use will be flagged as high-usage "
            f"and lose the {rebate:.0f} AUD energy-saving rebate.")


def parse_policy_arg(spec):
    """Parse a --policy CLI value into (policy_text, tag).

    Supported: "tou" or "tou:<peak_rate>,<valley_rate>" (AUD/kWh, optional shoulder via third value).
    Returns ("", None) when spec is empty/None.
    """
    if not spec:
        return "", None
    name = spec.strip().lower().split(":", 1)[0]
    if name in ("tou", "tou_soft"):
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        peak = valley = shoulder = None
        if rest:
            nums = [float(v) for v in rest.split(",")]
            if len(nums) >= 2:
                peak, valley = nums[0], nums[1]
            if len(nums) >= 3:
                shoulder = nums[2]
        render = render_tou_policy if name == "tou" else render_tou_policy_soft
        return render(peak, valley, shoulder), name
    if name == "nudge":
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        return (render_nudge_policy(float(rest)) if rest else render_nudge_policy()), "nudge"
    if name == "nudge_loss":
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        return (render_nudge_loss_policy(float(rest)) if rest else render_nudge_loss_policy()), "nudge_loss"
    raise ValueError(
        f"Unknown policy '{spec}'. Supported: tou, tou_soft, tou:<peak>,<valley>[,<shoulder>], nudge[:<kwh>], nudge_loss[:<aud>]"
    )


def parse_policy_schedule(specs):
    """Parse 'start,end,policy' entries into a schedule (end may be empty = open).

    Only simple policy names are allowed inside a schedule (no comma-bearing
    rate arguments), so entries stay comma-free.
    """
    schedule = []
    for spec in specs or []:
        if not spec:
            continue
        parts = [part.strip() for part in str(spec).split(",")]
        if len(parts) < 3 or not parts[0] or not parts[2]:
            raise ValueError(
                f"Bad policy-schedule '{spec}'; expected 'start,end,policy' (end may be empty)")
        schedule.append({"start": parts[0], "end": parts[1] or None, "policy": parts[2].lower()})
    return schedule


def active_policy_spec(schedule, date):
    """Policy name active on *date* (last matching entry wins), else None."""
    active = None
    for entry in schedule or []:
        start = entry.get("start")
        end = entry.get("end")
        if start and date >= start and (end is None or date <= end):
            active = entry.get("policy")
    return active
