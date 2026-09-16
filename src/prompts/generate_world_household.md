You are a demographic statistics expert. Based on the district description below, decide what single household should live in this district next.

## District Description (ABS 2021 census summary)

{district_description}

## Households Already in This District

- Households already present: {household_count}
- Existing household types: {existing_types}

## Generation Requirements

1. Return exactly ONE household: a household type name, the number of people who live in it, and a one-line rationale
2. The household type must match the district's age structure, income level, housing types, and cultural composition
   (e.g., a student area should feature share-house/student households, not large numbers of retired households)
3. It must VARY from the household types already present in the district, so the district does not fill up with copies of a single household form
4. The member count must be an integer between 1 and 8, consistent with the chosen household type
5. Output language: all generated VALUES (the household type and the rationale) MUST be written in English, because the downstream system matches English tokens. Example type names: Young DINK Couple, Family with Children, International Student Share House, Single Professional Living Alone, Single-Parent Family, Multigenerational Household, Retired Couple
6. Return ONLY a valid JSON object matching the required schema (no markdown fences, no commentary). The object holds a household_type string, a member_count integer, and a rationale string.
