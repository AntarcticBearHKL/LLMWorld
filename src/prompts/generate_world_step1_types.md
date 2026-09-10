You are a demographic statistics expert. Based on the district description below, generate a list of the household types most likely to appear in this community.

## District Description (ABS 2021 census summary)

{district_info}

## Generation Requirements

1. Generate exactly **{count}** distinct household types (covering the most typical and most common household forms in this community)
2. For each household type provide: a type name, a detailed description, the member count minimum and maximum, and a typical housing hint
3. Household types must match the district's age structure, income level, housing types, and cultural composition
   (e.g., a student area should feature share-house/student households, not large numbers of retired households)
4. Output language: all generated VALUES (type names, descriptions, housing hints) MUST be written in English, because the downstream system matches English tokens. Example type names: Young DINK Couple, Family with Children, International Student Share House, Single Professional Living Alone, Single-Parent Family, Multigenerational Household, Retired Couple
5. Return ONLY a valid JSON object matching the required schema (no markdown fences, no commentary).
