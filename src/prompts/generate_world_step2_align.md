You are a persona adaptation expert. Below is a household type definition and a set of original persona portraits sampled from a personality library.
Directly output the **final portraits that are fully consistent with the household definition**: rewrite the parts that conflict with the definition so they fit it,
and keep unrelated details unchanged. Do not explain what was wrong; just output the corrected result.

## Household Type

- Type: {household_type}
- Description: {household_description}
- Member count: {member_count}

## Original Personas (one per member, in the same order as the output)

{persona_texts}

## Output Requirements

1. Output exactly one final portrait per member, **the count and order must match the input exactly**
2. Only modify parts that conflict with the household definition (household form / member role / schedule & occupation / values etc.);
   keep unrelated details unchanged, including the original wording
3. The result must be self-consistent with the household type (e.g., a "family with children" must have at least one member showing a caregiving tendency;
   a "student share-house" allows student schedules; a single occupant needs no caregiving role)
4. Output language: each final portrait MUST be written in English (the downstream system matches English tokens). Do not use preset words such as energy-saving or environmental awareness, and do not invent equipment preferences such as electric vehicles
5. Natural English-language descriptions, consistent with the input style

Output JSON format (return ONLY the JSON, nothing else):

MANDATORY INSTRUCTIONS (must follow):
- Output only the JSON object itself in the format below. Never output markdown code fences (```), never output any explanatory text, never output schema descriptions (such as "type": "object")
- members must be an array of strings, with exactly {member_count} elements, in the same order as the input personas
- Each array element is a complete final portrait string; do not give elements field names (such as member2)

{
  "members": [
    "final portrait of member 1 (in English)",
    "final portrait of member 2 (in English)"
  ]
}
