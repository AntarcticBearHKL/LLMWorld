You are a household design expert. Based on the district information and household type, generate a specific household configuration.

District information:
{district_info}

Household type:
{household_type}

Supported appliance types: {supported_appliances}

Appliance configuration options:
{appliance_schemas}

Generate the complete household configuration, including:
1. Household basic information
2. Room layout and appliance configuration
3. Detailed household member information

Output JSON format (return ONLY the JSON, nothing else). Output language: all generated VALUES MUST be written in English, because the downstream system matches English tokens (season is one of Spring/Summer/Autumn/Winter; room names like Living Room; gender Male/Female; energy_awareness Low/Medium/High). The English text in this prompt is instruction only:
{{
  "type": "{household_type_name}",
  "season": "season (Spring/Summer/Autumn/Winter)",
  "home": {{
    "name": "home name",
    "type": "housing type",
    "size": area,
    "rooms": [
      {{
        "name": "room name (in English, e.g., Living Room)",
        "size": area,
        "appliances": [
          {{
            "type": "appliance type (must be one of the supported appliance types)",
            "brand": "brand name",
            "power": power in watts,
            "age": years of use
          }}
        ]
      }}
    ]
  }},
  "members": [
    {{
      "name": "full name",
      "age": age,
      "gender": "gender",
      "occupation": "occupation",
      "work_schedule": {{
        "start": "09:00",
        "end": "18:00",
        "remote": true/false,
        "work_days": [1,2,3,4,5]
      }},
      "personality": {{
        "traits": ["personality traits"],
        "energy_awareness": "energy awareness (Low/Medium/High)"
      }},
      "habits": {{
        "wake_time": "07:00",
        "sleep_time": "23:00",
        "exercise": "exercise habit",
        "hobbies": ["hobbies"]
      }},
      "health": {{
        "condition": "health condition",
        "temperature_preference": {{"summer": 26, "winter": 22}}
      }},
      "personal_appliances": [
        {{
          "type": "appliance type (must be one of the supported appliance types)",
          "brand": "brand name",
          "power": power in watts,
          "age": years of use
        }}
      ]
    }}
  ]
}}

Return only the JSON, no other content.
