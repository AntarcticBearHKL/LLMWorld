You are a demographic statistics expert. Based on the district description below, generate a list of the household types most likely to appear in this community.

## District Description (ABS 2021 census summary)

{district_info}

## Generation Requirements

1. Generate exactly **{count}** distinct household types (covering the most typical and most common household forms in this community)
2. For each household type provide: a type name, a detailed description, the typical member count, and a typical housing hint
3. Household types must match the district's age structure, income level, housing types, and cultural composition
   (e.g., a student area should feature share-house/student households, not large numbers of retired households)
4. Output language: all generated VALUES (type names, descriptions, housing hints) MUST be written in English, because the downstream system matches English tokens. Example type names: Young DINK Couple, Family with Children, International Student Share House, Single Professional Living Alone, Single-Parent Family, Multigenerational Household, Retired Couple

Output JSON format (return ONLY the JSON, nothing else):

MANDATORY INSTRUCTIONS (must follow):
- Output only the JSON object itself in the format below. Never output markdown code fences (```), never output any explanatory text, never output lists or headings
- Use exactly the field names below: type, description, typical_members (must be an integer 1-8), housing_hint
- Generate exactly {count} types, no more and no fewer

{
  "household_types": [
    {
      "type": "household type name (in English)",
      "description": "detailed feature description (3-5 sentences: member composition, occupation/income, lifestyle, housing needs)",
      "typical_members": 3,
      "housing_hint": "typical housing type hint (e.g., two-bedroom apartment, three-bedroom townhouse, one-bedroom unit)"
    }
  ]
}
