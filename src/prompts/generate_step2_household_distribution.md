You are a demographic statistics expert. Based on the district information, generate a reasonable household type distribution.

District information:
{district_info}

Generate the household type distribution, including:
1. Total household count (reasonable estimate)
2. Each household type with its count and percentage
3. A feature description for each household type

Output JSON format (return ONLY the JSON, nothing else). Output language: all generated VALUES MUST be written in English, because the downstream system matches English tokens (e.g., type is one of Single Occupant Apartment, Small Family, Middle-class Family, Large Family etc.). The English text in this prompt is instruction only:
{{
  "total_households": total household count,
  "household_types": [
    {{
      "type": "household type (e.g., Single Occupant Apartment, Small Family, Middle-class Family, Large Family etc.)",
      "count": count,
      "percentage": percentage,
      "description": "feature description",
      "typical_members": typical member count,
      "typical_housing": "typical housing type",
      "typical_size": typical area
    }}
  ]
}}

Return only the JSON, no other content.
