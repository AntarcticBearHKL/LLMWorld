Generate only the physical home for this Clayton household. Do not generate people.

Household type: {household_type}
Description: {household_description}
Housing hint: {housing_hint}
Residents: {member_count}

Supported appliance types (use exact tokens only):
{supported_appliances}

Appliance fields:
{appliance_schemas}

The home MUST include exactly {member_count} separately named bedroom rooms, named exactly "Bedroom 1" through "Bedroom {member_count}" (one per resident), plus a Kitchen and a Bathroom. Every appliance requires type, brand, power, and age. Copy appliance type tokens exactly from the supported list. Do not output synonyms such as Television, Dryer, RangeCooker, or ElectricWaterHeater. Include an ElectricVehicle only when the housing hint or household type plausibly implies car ownership (e.g. a family with a driveway); otherwise omit it. List every room explicitly; do not omit the bedrooms.
Never invent appliance types that are not in the supported list (no PV/solar panels, no home battery).
Return ONLY a valid JSON object (no markdown fences, no commentary).
