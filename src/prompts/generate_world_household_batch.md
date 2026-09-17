You are a demographic statistics expert. Based on the district description below, decide what new households should live in this district next.

## District Description (ABS 2021 census summary)

{district_description}

## Households Already in This District

- Households already present: {household_count}
- Existing household types: {existing_types}

## Generation Requirements

1. Return exactly {requested_count} households to ADD to this district
2. Each household must have a household type name, the number of people who live in it, and one or two sentences describing who lives there and why it fits this district
3. Every household must match the district's age structure, income level, housing types, and cultural composition
   (e.g., a student area should feature share-house/student households, not large numbers of retired households)
4. The set must be varied, and every household must VARY from the household types already present in the district, so the district does not fill up with copies of a single household form
5. Each member count must be an integer between 1 and 8, consistent with the chosen household type
6. Output language: all generated VALUES (the household type and the description) MUST be written in English, because the downstream system matches English tokens. Example type names: Young DINK Couple, Family with Children, International Student Share House, Single Professional Living Alone, Single-Parent Family, Multigenerational Household, Retired Couple
7. Return ONLY a valid JSON object matching the required schema (no markdown fences, no commentary). The object holds a "households" array of exactly {requested_count} entries; each entry is a household_type string, a member_count integer, and a description string.
