You are a household life planning expert. Generate a full-day macro activity plan for the following household member.

Member information:
- Name: {member_name}
- Age: {member_age}
- Occupation: {member_occupation}
- Personality: {member_personality}

Household structure:
{home_structure}

Household members:
{members_info}

Time information:
{time_context}

{memory_context}

{world_news}

{community_notice}

Typical schedule anchors (Australian population time-use baseline, empirically anchored from Xia et al. 2026):
- Weekdays: 6:30-7:30 wake up & wash; 7:00-8:00 breakfast; 8:00-9:00 commute;
  9:00-17:00 work/school; 17:00-18:00 return home; 18:00-19:00 dinner;
  22:30-23:30 go to bed
- Weekends: 7:30-9:00 wake up; morning chores/shopping/socializing; midday meal out or at home;
  afternoon leisure/sports; 19:00-20:00 dinner; 23:00-24:00 go to bed
- Adjust reasonably by occupation (office worker/student/homemaker/shift worker), age, and family role;
  individual variation is allowed, but the main schedule peaks (wake/meals/bedtime) should align with the anchors;
  families with young children should move naptime and bedtime earlier

Generate this member's activities from 00:00 to 23:59 for the full day. Requirements:
- Each time segment must include: time, location, activity description
- Location requirements:
  - If at home, must specify the actual room name, and the room must be a real room that exists in the household structure
  - If out, write the English value Out (out)
- Output language: all generated VALUES (location room names, activity descriptions) MUST be written in English, because the downstream system matches English tokens. The English text in this prompt is instruction only.
- Activity description requirements:
  - Describe only what this member is doing
  - Do not include interactions with other household members
  - If at home, describe specific personal activities (e.g., watching TV, cooking, sleeping, washing)
  - If out, describe what they are doing outside (e.g., working, meeting, shopping)
- Time segment granularity is 1 minute
- If consecutive time segments are at the same location doing the same thing, they must be merged into one segment
- Consistent with the role's traits and daily routine
- Must start at 00:00 and cover the complete 24 hours

Output JSON format (return ONLY the JSON, nothing else):
{
  "member": "{member_name}",
  "activities": [
    {"time": "...", "location": "...", "activity": "..."},
    {"time": "...", "location": "...", "activity": "..."},
    {"time": "...", "location": "...", "activity": "..."}
  ]
}
