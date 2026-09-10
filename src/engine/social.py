"""Neighbour-comparison social signal (intervention_experiment_guide.md §6.1).

Renders the natural-language peer-nudge from a community mean daily energy so
that the social comparison "rolls forward" as the community changes. Injected
into the s4 prompt by run.py; effects are emergent (no hardcoded behaviour).
"""


def community_mean_kwh(house_totals):
    """Mean of the non-None house totals (kWh), rounded; None when empty."""
    values = [float(value) for value in (house_totals or []) if value is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def render_peer_nudge(mean_kwh):
    """Neighbour-comparison sentence for the s4 prompt ('' when no mean)."""
    if mean_kwh is None:
        return ""
    return ("For comparison, households in your community used about "
            f"{mean_kwh:.2f} kWh of electricity yesterday on average.")
