Generate exactly one member profile for an existing household. Preserve the supplied portrait; do not substitute another person.

Household type: {household_type}
This is source persona {member_index} of {member_count}.
Assigned bedroom (copy exactly): {assigned_bedroom}

Canonical portrait:
{portrait}

Existing home (reference only):
{home_summary}

Supported personal appliance types (use exact tokens only):
{supported_appliances}

Preserve stated age, origin, student/work status, routine, personality and faith. Do not introduce energy-saving behaviour. Do not fabricate energy_awareness or big_five values in personality; the system derives them deterministically from the canonical persona record. The "name" field is assigned by the system (it will be "Member {member_index}"); you may set it to any placeholder value. Personal appliances may include an ElectricVehicle or Ebike ONLY if the canonical portrait implies the person owns or drives such a vehicle; otherwise omit them.
Return ONLY a valid JSON object (no markdown fences, no commentary).
