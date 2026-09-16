Generate only the physical home for one household placed in the district described below. Do not generate people.

## District Description (ABS 2021 census summary)

{district_description}

## Household

- Household type: {household_type}
- Residents: {member_count}

## Residents

{members_summary}

## Supported appliance types (use exact tokens only)

{supported_appliances}

## Appliance fields

{appliance_schemas}

## Generation Requirements

1. Create exactly one separately named bedroom per resident, named exactly "Bedroom 1" through "Bedroom {member_count}", one per resident and in order
2. Add the shared rooms a household of this size and type would physically have (for example a Kitchen, a Bathroom, and at most one Living Room); do NOT add studies, offices, dens, garages or any second shared space
3. Every room MUST list the appliances that physically sit in it, and every room MUST be listed explicitly (never omit the bedrooms)
4. Every appliance object needs the fields type, brand, power and age
5. Appliance names MUST be copied exactly from the supported appliance types list above; do NOT invent types (no solar panels, no home battery) and do NOT output synonyms such as Television, Fridge, Dryer, RangeCooker or ElectricWaterHeater
6. Include an ElectricVehicle only when the household type or district plausibly implies car ownership (e.g. a family with a driveway); otherwise omit it
7. Output language: all generated VALUES (the home name, room names, appliance types and brands) MUST be written in English
8. Return ONLY a valid JSON object matching the required schema (no markdown fences, no commentary). The top-level object has a single key whose value is the home object, and the home object holds name, type, size and rooms.
