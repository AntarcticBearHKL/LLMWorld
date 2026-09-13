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


CPP_DEFAULT = {
    "window": ("17:00", "20:00"),
    "peak_rate": 0.90,
}


def _cpp_sentence(peak_rate=None):
    """Facts-only critical-peak sentence (no behavioural directive)."""
    rate = CPP_DEFAULT["peak_rate"] if peak_rate is None else peak_rate
    start, end = CPP_DEFAULT["window"]
    return (
        f"Today is a critical peak pricing (CPP) event: electricity used during the critical "
        f"peak window {start}-{end} is charged at {rate:.2f} AUD/kWh, several times the normal rate."
    )


def render_cpp_policy(peak_rate=None):
    """Critical-peak-pricing event with an explicit shift directive (guide §2.1).

    Faruqui & Sergici (2010) benchmark: critical-peak pricing cuts peak load 13-20%,
    far more than plain TOU (3-6%). This renderer injects a narrow, very-high-price
    critical-peak window as natural language, mirroring the ``ac_tax`` event but
    belonging to the *pricing* capability family rather than the news templates.
    """
    return _cpp_sentence(peak_rate) + (
        " To avoid the high critical-peak price, shift flexible high-power use outside "
        "17:00-20:00 where possible."
    )


def render_cpp_soft_policy(peak_rate=None):
    """Critical-peak facts only, with no 'shift/avoid' directive (prompt-bias control)."""
    return _cpp_sentence(peak_rate)


UNIFORM_TAX_DEFAULT = 0.10


def render_uniform_tax_policy(rate=None):
    """Uniform electricity tax on all consumption, incl. self-generation (Gunkel et al. 2023).

    Gunkel et al. (2023) study taxing all residential consumption uniformly (removing the
    self-consumption exemption), which redistributes cost across household sizes. At the
    behavioural level the taxable base is total consumption, so the renderer asks agents to
    reduce total use to lower the tax.
    """
    r = UNIFORM_TAX_DEFAULT if rate is None else rate
    return (
        f"A uniform electricity tax of {r:.2f} AUD/kWh now applies to ALL the electricity your "
        "household consumes, no matter where it comes from (including any self-generated solar). "
        "To lower the tax you pay, reduce your total electricity consumption."
    )


def render_uniform_tax_policy_soft(rate=None):
    """Factual uniform-tax statement only, no 'reduce' directive (prompt-bias control)."""
    r = UNIFORM_TAX_DEFAULT if rate is None else rate
    return (
        f"A uniform electricity tax of {r:.2f} AUD/kWh applies to all the electricity your "
        "household consumes, regardless of where it comes from."
    )


def render_nudge_policy(neighbor_kwh=18.0):
    """Social-norm comparison with a fixed neighbour average (guide §3.1)."""
    return (f"Your neighbours use about {neighbor_kwh:.0f} kWh of electricity per day on average. "
            "Most households in your area try to keep their usage near or below this level.")


def render_nudge_soft_policy(neighbor_kwh=18.0):
    """Factual neighbour average only, no normative pressure (prompt-bias control)."""
    return f"Your neighbours use about {neighbor_kwh:.0f} kWh of electricity per day on average."


def render_nudge_loss_policy(rebate=30.0):
    """Loss-framed social norm (guide §3.2): lose a rebate if flagged high-usage."""
    return (f"Households that do not reduce their electricity use will be flagged as high-usage "
            f"and lose the {rebate:.0f} AUD energy-saving rebate.")


def render_subsidy_policy(rate=0.18):
    """Off-peak EV charging subsidy (guide §2.2)."""
    return (f"An off-peak charging subsidy is available: charging your electric vehicle between "
            f"22:00 and 07:00 earns a rebate of {rate:.2f} AUD/kWh.")


def render_peak_demand_policy(rate=12.0):
    """Demand charge on the daily peak hour (guide §2.3)."""
    return (f"Your household is on a demand charge: the highest 60 minutes of electricity use each "
            f"day is billed at {rate:.0f} AUD/kW, so spreading high-power appliances apart lowers it.")


def render_ev_delay_policy(step=0.02):
    """EV charging-delay incentive (guide §2.4)."""
    return (f"Delaying electric-vehicle charging earns a discount: the charging price drops "
            f"{step:.2f} AUD/kWh for each hour of delay, up to 8 hours.")


def render_night_setback_policy():
    """Night setback recommendation (guide §4.1)."""
    return ("Recommendation for tonight: set heating/cooling back while you sleep (for example "
            "2-3C lower heating or higher cooling) to reduce overnight energy use.")


def render_in_home_display_policy():
    """Real-time in-home-display feedback (guide §4.2)."""
    return ("Your home has a smart meter with an in-home display showing real-time electricity use "
            "and price, so you can see how much you are using right now.")


_POLICY_NAMES = frozenset({
    "tou", "tou_soft", "cpp", "cpp_soft", "tax_uniform", "tax_uniform_soft",
    "nudge", "nudge_soft", "nudge_loss",
    "subsidy", "peak_demand", "ev_delay", "night_setback", "in_home_display",
})


def _policy_head(spec):
    return spec.strip().lower().split(":", 1)[0]


def _parse_single_policy(spec):
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
    if name in ("cpp", "cpp_soft"):
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        rate = float(rest) if rest else None
        render = render_cpp_policy if name == "cpp" else render_cpp_soft_policy
        return render(rate), name
    if name in ("tax_uniform", "tax_uniform_soft"):
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        rate = float(rest) if rest else None
        render = render_uniform_tax_policy if name == "tax_uniform" else render_uniform_tax_policy_soft
        return render(rate), name
    if name == "nudge":
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        return (render_nudge_policy(float(rest)) if rest else render_nudge_policy()), "nudge"
    if name == "nudge_soft":
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        return (render_nudge_soft_policy(float(rest)) if rest else render_nudge_soft_policy()), "nudge_soft"
    if name == "nudge_loss":
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        return (render_nudge_loss_policy(float(rest)) if rest else render_nudge_loss_policy()), "nudge_loss"
    if name == "subsidy":
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        return (render_subsidy_policy(float(rest)) if rest else render_subsidy_policy()), "subsidy"
    if name == "peak_demand":
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        return (render_peak_demand_policy(float(rest)) if rest else render_peak_demand_policy()), "peak_demand"
    if name == "ev_delay":
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        return (render_ev_delay_policy(float(rest)) if rest else render_ev_delay_policy()), "ev_delay"
    if name == "night_setback":
        return render_night_setback_policy(), "night_setback"
    if name == "in_home_display":
        return render_in_home_display_policy(), "in_home_display"
    raise ValueError(
        "Unknown policy '%s'. Supported: tou, tou_soft, tou:<peak>,<valley>[,<shoulder>], "
        "cpp[:<peak_rate>], cpp_soft[:<peak_rate>], tax_uniform[:<rate>], tax_uniform_soft[:<rate>], "
        "nudge[:<kwh>], nudge_soft[:<kwh>], "
        "nudge_loss[:<aud>], subsidy[:<rate>], peak_demand[:<rate>], "
        "ev_delay[:<step>], night_setback, in_home_display; combine with commas e.g. 'tou,nudge'." % spec
    )


def parse_policy_arg(spec):
    """Parse a --policy CLI value into (policy_text, tag).

    Supports single policies, rate arguments (e.g. "tou:0.6,0.18,0.35"), and
    comma-combinations of several policies (e.g. "tou,nudge"). A comma starts a
    new *policy* only when the next token names a known policy; otherwise it is a
    rate argument belonging to the current policy. The combined tag joins the
    individual tags with "+" (e.g. "tou+nudge"). Returns ("", None) when empty.
    """
    if not spec:
        return "", None
    groups = []
    for token in (t.strip() for t in spec.split(",")):
        if not token:
            continue
        if groups and _policy_head(token) not in _POLICY_NAMES:
            groups[-1] = groups[-1] + "," + token
        else:
            groups.append(token)
    texts = []
    tags = []
    for group in groups:
        text, tag = _parse_single_policy(group)
        if text:
            texts.append(text)
        tags.append(tag)
    return " ".join(texts), "+".join(tags)


def parse_tariff(spec):
    """Structured tariff (rates + windows) for price policies, else None.

    Used to build the concrete cost context injected into s4. Returns a dict with
    peak_window/valley_window/peak_rate/valley_rate/shoulder_rate.
    """
    if not spec:
        return None
    head = _policy_head(spec)
    if head in ("tou", "tou_soft"):
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        peak = valley = shoulder = None
        if rest:
            nums = [float(v) for v in rest.split(",")]
            if len(nums) >= 2:
                peak, valley = nums[0], nums[1]
            if len(nums) >= 3:
                shoulder = nums[2]
        cfg = _tou_config(peak, valley, shoulder)
        return {
            "peak_window": cfg["peak_window"],
            "valley_window": cfg["valley_window"],
            "peak_rate": cfg["peak_rate"],
            "valley_rate": cfg["valley_rate"],
            "shoulder_rate": cfg["shoulder_rate"],
        }
    if head in ("cpp", "cpp_soft"):
        rest = spec.split(":", 1)[1] if ":" in spec else ""
        rate = float(rest) if rest else CPP_DEFAULT["peak_rate"]
        return {
            "peak_window": CPP_DEFAULT["window"],
            "valley_window": TOU_DEFAULT["valley_window"],
            "peak_rate": rate,
            "valley_rate": TOU_DEFAULT["valley_rate"],
            "shoulder_rate": TOU_DEFAULT["shoulder_rate"],
        }
    return None


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
