You are a persona adaptation expert. Rewrite the sampled personas so they fit the household type while remaining coherent and useful for a household simulation.

## Household Type

- Type: {household_type}
- Description: {household_description}
- Total people: {household_member_count}

## Sampled Personas

{persona_texts}

Rewrite them into complete English portraits, one per person, in the same order, written in third person and consistent with the household type and location.
Return ONLY a valid JSON object with exactly this shape (no markdown fences, no commentary):

{"members": [{"portrait": "<the rewritten portrait, in English>", "age": <integer>, "gender": "<string>"}]}

The members array MUST contain exactly {household_member_count} entries, one per sampled persona, in the same order. Do not invent personal names — the sampled personas already carry them.
