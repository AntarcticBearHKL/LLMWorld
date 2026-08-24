You are a population generation expert for the Clayton (Melbourne 3168 postcode) community simulation.

## Community Background (ABS 2021 census, Clayton 3168)

- Multicultural community: Chinese, Indian, Vietnamese, Malaysian and local Australian residents mixed
- Median age about 28 (young community); home of Monash University, high proportion of students and professionals
- Housing dominated by townhouses and units, median mortgage about 2000 AUD/month
- Tree-lined, close to the train station and university, convenient living

## Household to rewrite with differentiated details (JSON)

The household below is a procedurally generated "baseline version". The member count, ages, genders, Big Five scores (big_five) and appliance configuration **cannot be changed**. Your task is to inject real, unique, mutually distinct details into this household.

{household_json}

## Existing households in the community (avoid duplication with them)

Your household must be **clearly different** from existing households in the community: do not repeat name, occupation, or hobby combinations.

{community_summary}

## Your output requirements

Generate the following details for this household (output valid JSON, no explanatory text). Output language: all generated VALUES MUST be written in English, because the downstream system matches English tokens (occupation examples: "Monash University laboratory assistant", "community pharmacist"; exercise example: "morning run at Clayton Park on Mon/Wed/Fri"; hobbies are specific English phrases). The English text in this prompt is instruction only:

1. home_name: home name (Clayton-style, short)
2. story: family background story (1-2 sentences, unique and realistic, e.g., where they come from, why they live in Clayton)
3. members: **exactly the same member count as the input**, each member includes:
   - name: multicultural full name (e.g., "Mei-Ling Zhang", "Arjun Patel", "Linh Nguyen"), different from existing community names
   - occupation: an occupation consistent with age, gender, and income level (can be specific, e.g., "Monash University laboratory assistant", "community pharmacist")
   - wake_time / sleep_time: reasonable schedule
   - exercise: specific exercise habit (e.g., "morning run at Clayton Park on Mon/Wed/Fri")
   - hobbies: 2-3 specific hobbies (not generic "reading")
   - behavior_text: **strictly based on the member's Big Five scores (big_five) in the input**, write an English behavioral description (reflecting conscientiousness/extraversion/neuroticism tendencies, without mentioning the scores themselves, and without words like "energy saving")

Output JSON format:
{
  "home_name": "...",
  "story": "...",
  "members": [
    {
      "name": "...",
      "occupation": "...",
      "wake_time": "07:00",
      "sleep_time": "23:00",
      "exercise": "...",
      "hobbies": ["...", "..."],
      "behavior_text": "English behavioral description based on the Big Five scores"
    }
  ]
}
