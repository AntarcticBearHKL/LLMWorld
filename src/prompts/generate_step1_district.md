You are a district planning expert. Based on the user's description, generate a detailed district setting.

User description: {user_prompt}

Generate the district setting, including:
1. Geographic location (city, district, postcode, coordinates)
2. Economic level and spending power
3. Cultural background and lifestyle
4. Community environment description
5. Typical housing types and area ranges

Output JSON format (return ONLY the JSON, nothing else). Output language: all generated VALUES MUST be written in English, because the downstream system matches English tokens (e.g., economic_level is one of Low/Medium/High). The English text in this prompt is instruction only:
{{
  "postcode": "postcode",
  "location": {{
    "city": "city name",
    "district": "district name",
    "country": "country code (e.g., CN, US, AU)",
    "coordinates": {{"lat": latitude, "lon": longitude}}
  }},
  "description": "detailed district description",
  "economic_level": "economic level (Low/Medium/High)",
  "culture": "cultural background description",
  "lifestyle": "lifestyle description",
  "housing_types": [
    {{
      "type": "housing type",
      "size_range": {{"min": min area, "max": max area}},
      "typical_percentage": percentage
    }}
  ]
}}

Return only the JSON, no other content.
