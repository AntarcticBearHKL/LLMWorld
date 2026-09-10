"""Legacy analysis entry point.

The old env.json based simulation layout was removed; analysis now reads the
current layout through `dataset`. Existing scripts keep working with
`from simulation_env import sim_root`.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from dataset import (
    PROJECT_ROOT,
    SIMULATION_DIR,
    WORLDS_DIR,
    sim_root,
    list_dates,
    list_houses,
    household_path,
    read_household,
    read_member_names,
    discover_policy_tags,
    read_activities,
    read_timeline,
    read_decisions,
    iter_house_days,
    population_profile,
    household_features,
)
