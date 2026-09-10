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


def render_tou_policy(peak_rate=None, valley_rate=None, shoulder_rate=None):
    cfg = dict(TOU_DEFAULT)
    if peak_rate is not None:
        cfg["peak_rate"] = peak_rate
    if valley_rate is not None:
        cfg["valley_rate"] = valley_rate
    if shoulder_rate is not None:
        cfg["shoulder_rate"] = shoulder_rate

    peak_from, peak_to = cfg["peak_window"]
    valley_from, valley_to = cfg["valley_window"]
    return (
        "Today your household is on a time-of-use (TOU) electricity tariff: "
        f"peak period {peak_from}-{peak_to} at {cfg['peak_rate']:.2f} AUD/kWh; "
        f"valley period {valley_from}-{valley_to} at {cfg['valley_rate']:.2f} AUD/kWh; "
        f"shoulder period (all other times) at {cfg['shoulder_rate']:.2f} AUD/kWh. "
        "To reduce your bill, shift flexible appliances (electric vehicle charging, "
        "washing machine, dishwasher-free routines like hot water use) into the valley "
        "period, and avoid running high-power appliances during the peak period unless "
        "necessary."
    )


def parse_policy_arg(spec):
    """Parse a --policy CLI value into (policy_text, tag).

    Supported: "tou" or "tou:<peak_rate>,<valley_rate>" (AUD/kWh, optional shoulder via third value).
    Returns ("", None) when spec is empty/None.
    """
    if not spec:
        return "", None
    name = spec.strip().lower().split(":", 1)[0]
    if name == "tou":
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        peak = valley = shoulder = None
        if rest:
            nums = [float(v) for v in rest.split(",")]
            if len(nums) >= 2:
                peak, valley = nums[0], nums[1]
            if len(nums) >= 3:
                shoulder = nums[2]
        return render_tou_policy(peak, valley, shoulder), "tou"
    raise ValueError(
        f"Unknown policy '{spec}'. Supported: tou, tou:<peak>,<valley>[,<shoulder>]"
    )
