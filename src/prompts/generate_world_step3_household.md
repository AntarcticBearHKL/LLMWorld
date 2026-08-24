You are a household design expert for the Clayton (Melbourne 3168 postcode) community simulation. Based on the household type and the already-sampled
member persona portraits, generate the complete household configuration (room layout + appliances + member profiles).

## District Background (ABS 2021 census, Clayton 3168)

{district_info}

## Household Type

- Type: {household_type}
- Description: {household_description}
- Housing hint: {housing_hint}

## Member Persona Portraits (already consistency-checked, one per member)

{persona_texts}

## Supported Appliance Types (type must be one of these EXACT English names)

{supported_appliances}

Appliance configuration reference (type: available fields):
{appliance_schemas}

## Generation Requirements

1. **The number of members must exactly equal the number of persona portraits**, and each member's profile must closely match the corresponding portrait
   (schedule/occupation/hobbies/personality must be inferred from the portrait, do not invent contradictory details)
2. Member profile fields: name (multicultural full name, e.g., "Mei-Ling Zhang", "Arjun Patel"), age,
   gender, occupation, work_schedule (schedule window / remote or not / which weekdays),
   personality (traits list, behavior_text an English behavioral description in one paragraph — **strictly based on the portrait**,
   reflecting how the member operates; **must NOT contain preset words like energy-saving or environmental awareness**),
   habits (wake_time/sleep_time/exercise/hobbies), health (health condition and A/C temperature preference),
   personal_appliances (personal appliances the member uses; type must be one of the supported types)
3. Rooms & appliances: configure rooms reasonably according to the household type and housing hint (Living Room/Kitchen/Bathroom/Bedroom etc.),
   appliance type must be one of the supported English names, with brand/power/age fields complete;
   **do NOT preset electric vehicles or energy-saving appliances for a "green persona"** — configure naturally according to the household's economic level
4. Household electricity behavior must have no preset tendency; it should emerge autonomously from the AI during the simulation stage

Output JSON format (return ONLY the JSON, nothing else):

MANDATORY INSTRUCTIONS (must follow):
- Output only the JSON object itself in the format below. Never output markdown code fences (```), never output any explanatory text, never output schema descriptions
- The number of elements in the members array **must exactly equal the number of portraits** ({member_count}), one member per portrait
- Use exactly the field names in the example below: rooms use name (not type), habits use wake_time/sleep_time, health uses condition/temperature_preference, personal_appliances (not appliances)
- Member names must not be duplicated
- Output language: all generated VALUES (story, room names, occupations, behavior_text) MUST be written in English, because the downstream system matches English tokens. Enum values must use the exact English tokens below: season is one of Spring/Summer/Autumn/Winter; gender is one of Male/Female; energy_awareness and news_sensitivity are one of Low/Medium/High; appliance type and room name are English (see the supported list and examples below)

{
  "type": "household type name (in English)",
  "season": "season (Spring/Summer/Autumn/Winter)",
  "story": "family background story (1-2 sentences, unique and realistic)",
  "home": {
    "name": "home name",
    "type": "housing type (e.g., townhouse/unit/detached house/apartment)",
    "size": 120,
    "rooms": [
      {
        "name": "room name (in English, e.g., Living Room)",
        "size": 25,
        "appliances": [
          {"type": "appliance type (exact English name from the supported list)", "brand": "brand", "power": 2000, "age": 3}
        ]
      }
    ]
  },
  "members": [
    {
      "name": "full name",
      "age": 24,
      "gender": "Male/Female",
      "occupation": "occupation",
      "work_schedule": {"start": "09:00", "end": "18:00", "remote": false, "work_days": [1,2,3,4,5]},
      "personality": {
        "traits": ["personality tags"],
        "behavior_text": "English behavioral description based on the portrait (must NOT contain energy-saving presets)",
        "energy_awareness": "Low/Medium/High (inferred naturally from the portrait's values and spending habits, do not deliberately write energy-saving behavior)",
        "news_sensitivity": "Low/Medium/High (inferred from the portrait's anxiety tendency and news habits)",
        "big_five": {"openness": 6, "conscientiousness": 8, "extraversion": 4, "agreeableness": 7, "neuroticism": 3}
      },
      "habits": {"wake_time": "07:00", "sleep_time": "23:00", "exercise": "exercise habit", "hobbies": ["hobby"]},
      "health": {"condition": "health condition", "temperature_preference": {"summer": 26, "winter": 22}},
      "personal_appliances": [
        {"type": "appliance type (exact English name from the supported list)", "brand": "brand", "power": 100, "age": 1}
      ]
    }
  ]
}
