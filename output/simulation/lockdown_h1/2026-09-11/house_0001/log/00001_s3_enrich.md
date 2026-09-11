# s3_enrich  (attempt 1)

## 对话信息

- time: 2026-09-11 03:34:20
- seq: 1
- prefix: Member 1_
- stage: s3_enrich
- attempt: 1
- ok: True

## 输入

```
You are a behavior analysis expert. Generate a detailed **behavior checklist** for Member 1's day.

Member information:
- Name: Member 1
- Age: 24
- Occupation: Full-time Master of Education student at Monash University; part-time hospitality and retail worker
- Personality: 

This member's timeline:
[
  {
    "time": "00:00-06:30",
    "location": "Bedroom 1",
    "activity": "Sleeping"
  },
  {
    "time": "06:30-07:00",
    "location": "Bathroom",
    "activity": "Waking up early, showering and personal hygiene (scheduled before Member 4's 07:00 shower and Member 3's 07:20 wash to avoid the shared bathroom clash)"
  },
  {
    "time": "07:00-07:45",
    "location": "Kitchen",
    "activity": "Preparing and eating breakfast and making tea with the kettle and toaster; Member 4 joins from 07:30 to prepare breakfast, so they chat while sharing the kitchen"
  },
  {
    "time": "07:45-08:00",
    "location": "Bedroom 1",
    "activity": "Setting up the desk and reviewing today's study plan"
  },
  {
    "time": "08:00-12:00",
    "location": "Bedroom 1",
    "activity": "Studying online for the Master of Education at the desk using the computer and desk lamp, attending remote lectures and reading course materials"
  },
  {
    "time": "12:00-12:45",
    "location": "Kitchen",
    "activity": "Cooking and eating lunch, reheating food with the microwave while Member 2 cooks her own lunch on the induction cooker"
  },
  {
    "time": "12:45-13:15",
    "location": "Living Room",
    "activity": "Taking a short break, checking the phone and resting on the sofa"
  },
  {
    "time": "13:15-17:00",
    "location": "Bedroom 1",
    "activity": "Continuing online study and coursework, writing assignments on the computer and reviewing notes"
  },
  {
    "time": "17:00-17:40",
    "location": "Living Room",
    "activity": "Doing light stretching and indoor exercise together with Member 2, then resting with the fan on"
  },
  {
    "time": "17:40-18:30",
    "location": "Kitchen",
    "activity": "Cooking dinner with the induction cooker and rice cooker, sharing the kitchen with Member 3 who is also cooking"
  },
  {
    "time": "18:30-19:15",
    "location": "Kitchen",
    "activity": "Eating dinner together with Member 2 and Member 3"
  },
  {
    "time": "19:15-19:45",
    "location": "Kitchen",
    "activity": "Washing dishes and wiping down the kitchen benches together with Member 2 and Member 3"
  },
  {
    "time": "19:45-20:15",
    "location": "Bathroom",
    "activity": "Doing laundry with the washing machine and tidying up"
  },
  {
    "time": "20:15-21:15",
    "location": "Bedroom 1",
    "activity": "Relaxing, browsing the phone and reading in the bedroom while Member 2 and Member 3 use the Living Room for video calls"
  },
  {
    "time": "21:15-21:45",
    "location": "Kitchen",
    "activity": "Making a hot drink and preparing a light evening snack"
  },
  {
    "time": "21:45-22:45",
    "location": "Bedroom 1",
    "activity": "Reading course materials and planning the next day's study tasks at the desk"
  },
  {
    "time": "22:45-23:15",
    "location": "Bathroom",
    "activity": "Night routine: washing up and brushing teeth (after Member 2's evening shower and laundry finish at 22:40)"
  },
  {
    "time": "23:15-24:00",
    "location": "Bedroom 1",
    "activity": "Winding down, dimming the desk lamp and going to sleep"
  }
]

Other household members' timelines:
{
  "Member 2": [
    {
      "time": "00:00-01:45",
      "location": "Bedroom 2",
      "activity": "Lying in bed doomscrolling YouTube videos and replying to WhatsApp messages on phone"
    },
    {
      "time": "01:45-08:30",
      "location": "Bedroom 2",
      "activity": "Sleeping"
    },
    {
      "time": "08:30-08:50",
      "location": "Bathroom",
      "activity": "Washing face, brushing teeth and getting dressed for the day (after Member 3 finishes their 07:20-08:00 bathroom slot)"
    },
    {
      "time": "08:50-09:20",
      "location": "Kitchen",
      "activity": "Boiling the kettle, making a pot of tea and eating breakfast at the kitchen counter (Member 3 has finished cooking breakfast; Member 4 is studying in Bedroom 4)"
    },
    {
      "time": "09:20-09:45",
      "location": "Bedroom 2",
      "activity": "Daily stretching routine on the floor beside the bed"
    },
    {
      "time": "09:45-10:00",
      "location": "Kitchen",
      "activity": "Washing breakfast dishes and wiping down shared kitchen benches"
    },
    {
      "time": "10:00-12:00",
      "location": "Bedroom 2",
      "activity": "Attending online design studio class on the computer and monitor, taking notes and sketching concepts"
    },
    {
      "time": "12:00-12:40",
      "location": "Kitchen",
      "activity": "Cooking a lunch that fits her medical dietary restriction using the induction cooker, sharing the kitchen with Member 1 who is reheating her own lunch"
    },
    {
      "time": "12:40-13:10",
      "location": "Kitchen",
      "activity": "Eating lunch while listening to a design podcast on phone"
    },
    {
      "time": "13:10-14:30",
      "location": "Bedroom 2",
      "activity": "Working on freelance creative briefs on the computer, editing files and emailing drafts to clients"
    },
    {
      "time": "14:30-15:00",
      "location": "Kitchen",
      "activity": "Brewing another cup of tea and having a light snack"
    },
    {
      "time": "15:00-17:00",
      "location": "Bedroom 2",
      "activity": "Continuing coursework and assignment writing on the computer at her desk"
    },
    {
      "time": "17:00-17:40",
      "location": "Living Room",
      "activity": "Doing a guided stretch and mobility session together with Member 1, then resting with the fan on"
    },
    {
      "time": "17:40-18:30",
      "location": "Kitchen",
      "activity": "Cooking dinner from scratch with ingredients suitable for her dietary restriction, sharing the kitchen with Member 1 and Member 3 who are also cooking"
    },
    {
      "time": "18:30-19:15",
      "location": "Kitchen",
      "activity": "Eating dinner together with Member 1 and Member 3"
    },
    {
      "time": "19:15-19:45",
      "location": "Kitchen",
      "activity": "Washing dishes, wiping benches and taking out kitchen rubbish together with Member 1 and Member 3"
    },
    {
      "time": "19:45-21:15",
      "location": "Living Room",
      "activity": "Joining a big-group virtual hangout with friends over video call together with Member 3, chatting and sharing screens"
    },
    {
      "time": "21:15-21:30",
      "location": "Bedroom 2",
      "activity": "Sorting sketchbooks and art supplies at her desk and browsing art supply sales online"
    },
    {
      "time": "21:30-22:40",
      "location": "Bathroom",
      "activity": "Showering, completing her night hygiene routine and running a load of laundry in the washing machine (after Member 4's 21:00-21:30 evening shower, so Member 1 can use the bathroom from 22:45)"
    },
    {
      "time": "22:40-23:00",
      "location": "Kitchen",
      "activity": "Making a final herbal tea and rinsing her mug"
    },
    {
      "time": "23:00-24:00",
      "location": "Bedroom 2",
      "activity": "In bed half-watching YouTube videos and answering WhatsApp messages while drifting off to sleep"
    }
  ],
  "Member 3": [
    {
      "time": "00:00-06:50",
      "location": "Bedroom 3",
      "activity": "Sleeping restlessly, waking briefly several times with mild chronic pain and stress"
    },
    {
      "time": "06:50-07:30",
      "location": "Bedroom 3",
      "activity": "Slow morning start: lying in bed, checking phone, scrolling Instagram and Messenger"
    },
    {
      "time": "07:30-08:15",
      "location": "Bathroom",
      "activity": "Showering, washing and taking daily medication (after Member 4's 07:00-07:30 bathroom slot; before Member 2's 08:30 bathroom slot)"
    },
    {
      "time": "08:15-08:50",
      "location": "Kitchen",
      "activity": "Cooking and eating a slow breakfast, boiling the kettle for herbal tea, no caffeine (after Member 4 finishes in the kitchen; before Member 2's 08:50 breakfast)"
    },
    {
      "time": "08:50-09:20",
      "location": "Bedroom 3",
      "activity": "Sorting the desk and papers in a chaotic-tidiness way and planning the research day"
    },
    {
      "time": "09:20-10:45",
      "location": "Bedroom 3",
      "activity": "PhD work: drafting a systematic review chapter on the computer"
    },
    {
      "time": "10:45-11:00",
      "location": "Living Room",
      "activity": "Gentle stretching and mobility break for chronic pain and mobility limitation"
    },
    {
      "time": "11:00-12:20",
      "location": "Bedroom 3",
      "activity": "PhD work: analysing public health data and organising references on the computer"
    },
    {
      "time": "12:20-13:00",
      "location": "Kitchen",
      "activity": "Cooking and eating lunch, sharing the kitchen and joining Member 1 and Member 2 during their lunch period"
    },
    {
      "time": "13:00-13:30",
      "location": "Living Room",
      "activity": "Resting on the couch with the TV on quietly, overlapping with Member 1's short break"
    },
    {
      "time": "13:30-14:00",
      "location": "Bedroom 3",
      "activity": "Reviewing supervision notes and preparing for the online PhD supervision meeting"
    },
    {
      "time": "14:00-15:00",
      "location": "Bedroom 3",
      "activity": "Online PhD supervision meeting with the research team over video call"
    },
    {
      "time": "15:00-16:30",
      "location": "Bedroom 3",
      "activity": "Writing and editing thesis sections on the computer"
    },
    {
      "time": "16:30-17:00",
      "location": "Kitchen",
      "activity": "Afternoon snack and herbal tea break"
    },
    {
      "time": "17:00-17:40",
      "location": "Bedroom 3",
      "activity": "Household management: paying bills by mobile wallet, updating the support-shift roster, checking whether today's rostered shift was cancelled by the lockdown, and logging maintenance tasks"
    },
    {
      "time": "17:40-18:30",
      "location": "Kitchen",
      "activity": "Cooking dinner with Member 1 and Member 2, sharing the kitchen"
    },
    {
      "time": "18:30-19:15",
      "location": "Kitchen",
      "activity": "Eating dinner together with Member 1 and Member 2"
    },
    {
      "time": "19:15-19:45",
      "location": "Kitchen",
      "activity": "Washing dishes and wiping down kitchen surfaces together with Member 1 and Member 2"
    },
    {
      "time": "19:45-20:15",
      "location": "Living Room",
      "activity": "Joining the structured online group video call with Member 2"
    },
    {
      "time": "20:15-20:45",
      "location": "Bathroom",
      "activity": "Evening wash and taking night medication (after Member 1's 19:45-20:15 bathroom laundry; before Member 4's 21:00 shower)"
    },
    {
      "time": "20:45-21:15",
      "location": "Living Room",
      "activity": "Rejoining the structured online group video call with Member 2"
    },
    {
      "time": "21:15-22:00",
      "location": "Living Room",
      "activity": "Watching TV and relaxing to wind down"
    },
    {
      "time": "22:00-23:00",
      "location": "Bedroom 3",
      "activity": "Wind-down: reading, setting out tomorrow's things, and switching off the phone"
    },
    {
      "time": "23:00-24:00",
      "location": "Bedroom 3",
      "activity": "Sleeping"
    }
  ],
  "Member 4": [
    {
      "time": "00:00-07:00",
      "location": "Bedroom 4",
      "activity": "Sleeping through the night"
    },
    {
      "time": "07:00-07:30",
      "location": "Bathroom",
      "activity": "Waking up, showering and washing up (own bathroom slot, after Member 1's 06:30-07:00 shower and before Member 3's 07:30 slot)"
    },
    {
      "time": "07:30-08:15",
      "location": "Kitchen",
      "activity": "Preparing and eating breakfast and making a hot drink with the kettle, sharing the kitchen and chatting with Member 1 who is finishing her breakfast until 07:45"
    },
    {
      "time": "08:15-09:00",
      "location": "Bedroom 4",
      "activity": "Checking university emails and reviewing lecture notes on the computer at the desk"
    },
    {
      "time": "09:00-11:00",
      "location": "Bedroom 4",
      "activity": "Attending an online Bachelor of Commerce lecture via video call on the computer"
    },
    {
      "time": "11:00-11:15",
      "location": "Kitchen",
      "activity": "Taking a short break and boiling water for tea"
    },
    {
      "time": "11:15-13:00",
      "location": "Bedroom 4",
      "activity": "Studying IT coursework and completing online assignments on the computer"
    },
    {
      "time": "13:00-13:45",
      "location": "Kitchen",
      "activity": "Cooking lunch on the induction cooker and eating it (kitchen free after Member 3 finishes at 13:00)"
    },
    {
      "time": "13:45-14:15",
      "location": "Living Room",
      "activity": "Relaxing on the sofa and watching news on the TV"
    },
    {
      "time": "14:15-16:00",
      "location": "Bedroom 4",
      "activity": "Conducting a paid online tutoring session from the desk"
    },
    {
      "time": "16:00-16:15",
      "location": "Kitchen",
      "activity": "Making a quick snack and a warm drink"
    },
    {
      "time": "16:15-17:40",
      "location": "Bedroom 4",
      "activity": "Working on freelance analyst tasks and spreadsheet reports on the computer"
    },
    {
      "time": "17:40-18:30",
      "location": "Kitchen",
      "activity": "Cooking dinner together with Member 1, Member 2 and Member 3, sharing the kitchen and the induction cooker and rice cooker"
    },
    {
      "time": "18:30-19:15",
      "location": "Kitchen",
      "activity": "Eating dinner together with Member 1, Member 2 and Member 3"
    },
    {
      "time": "19:15-19:45",
      "location": "Kitchen",
      "activity": "Washing dishes and wiping down the kitchen benches together with Member 1, Member 2 and Member 3"
    },
    {
      "time": "19:45-21:00",
      "location": "Bedroom 4",
      "activity": "Relaxing in the bedroom with a game on the phone and reading, since Member 2 and Member 3 are using the Living Room for their video call"
    },
    {
      "time": "21:00-21:30",
      "location": "Bathroom",
      "activity": "Taking an evening shower and getting ready for bed (own reserved slot, before Member 2's 21:30 shower and laundry)"
    },
    {
      "time": "21:30-22:30",
      "location": "Bedroom 4",
      "activity": "Chatting with family online on the phone and reading course material"
    },
    {
      "time": "22:30-24:00",
      "location": "Bedroom 4",
      "activity": "Sleeping"
    }
  ]
}

Household structure:
{
  "Bedroom 1": {
    "appliances": []
  },
  "Bedroom 2": {
    "appliances": []
  },
  "Bedroom 3": {
    "appliances": []
  },
  "Bedroom 4": {
    "appliances": []
  },
  "Kitchen": {
    "appliances": [
      "Refrigerator",
      "Microwave",
      "RiceCooker",
      "InductionCooker",
      "RangeHood",
      "Kettle",
      "Toaster",
      "Oven",
      "Freezer"
    ]
  },
  "Bathroom": {
    "appliances": [
      "WaterHeater",
      "WashingMachine"
    ]
  },
  "Living Room": {
    "appliances": [
      "TV",
      "GameConsole",
      "Router",
      "AirConditioner",
      "Fan",
      "Light"
    ]
  },
  "Member 1 personal appliances": {
    "appliances": [
      "Computer",
      "Phone",
      "DeskLamp"
    ]
  },
  "Member 2 personal appliances": {
    "appliances": [
      "Computer",
      "Phone",
      "DeskLamp",
      "Monitor"
    ]
  },
  "Member 3 personal appliances": {
    "appliances": [
      "Computer",
      "Phone",
      "DeskLamp"
    ]
  },
  "Member 4 personal appliances": {
    "appliances": [
      "Computer",
      "Phone",
      "DeskLamp"
    ]
  }
}

Environment: Spring, Sunny, 20 degrees

## Important requirements

**This is NOT novel-writing, this is behavior recording!**

You are enriching an existing canonical timeline. Copy every input time, location, and activity value exactly and in the same order. Do not merge, split, add, remove, rename, or extend any segment. Only add the desc field.

The description (desc field) must be a **detailed list of concrete actions**, recording as many observable behaviors as possible.

### Requirements:
1. **Record all concrete actions**:
   - Body actions: walk, sit, stand, lie down, bend, reach, turn around, etc.
   - Hand actions: pick up, put down, press, twist, push, pull, wipe, wash, etc.
   - Operation actions: open, close, start, stop, adjust, etc.
   - Interaction with objects: every object and device touched

2. **Record in chronological order**:
   - What is done first, what comes next
   - The sequence of actions must be reasonable

3. **Include dialogue** (if any):
   - Briefly record what was said
   - Communication with other members

### Strictly forbidden:
❌ Inner mental activity ("thinking..." "considering..." "feeling...")
❌ Emotional description ("warm" "pleasant" "comfortable")
❌ Environment description ("sunlight" "fragrance" "atmosphere")
❌ Literary rhetoric and adjectives

### Description length:
- 1-5 minutes: 3-5 actions
- 5-30 minutes: 5-12 actions
- 30+ minutes: 12-20 actions

### Description format example:

**Good example**:
"Wake up. Walk to the bathroom. Turn on the light. Turn on the tap. Pick up the toothbrush. Squeeze toothpaste onto it. Brush teeth. Rinse mouth. Wipe face with a towel. Turn off the tap. Turn off the light. Walk out of the bathroom."

**Bad example**:
"She woke up feeling a bit sleepy, slowly walked to the bathroom. The warm light made her feel comfortable..."

## Output format

Output JSON format (return ONLY the JSON, nothing else):
- Output language: all generated VALUES (activity, desc, location) MUST be written in English, because the downstream system matches English tokens. The English text in this prompt is instruction only.
{
  "member": "Member 1",
  "enriched_activities": [
    {
      "time": "time segment",
      "location": "location",
      "activity": "activity",
      "desc": "action 1. action 2. action 3. action 4. ... (in English)"
    }
  ]
}

## Core principle

**Write only visible actions, never invisible thoughts!**
**The more detailed the better, but it must be concrete behavior!**
**The member field must exactly equal "Member 1" and names mentioned in descriptions must exactly match the supplied household members.**

```

## Schema

```json
(none)
```

## 返回(原始)

```
{
  "member": "Member 1",
  "enriched_activities": [
    {
      "time": "00:00-06:30",
      "location": "Bedroom 1",
      "activity": "Sleeping",
      "desc": "Lying in bed. Eyes closed. Body relaxed. Breathing steadily. Occasionally turning to the side. Remaining asleep."
    },
    {
      "time": "06:30-07:00",
      "location": "Bathroom",
      "activity": "Waking up early, showering and personal hygiene (scheduled before Member 4's 07:00 shower and Member 3's 07:20 wash to avoid the shared bathroom clash)",
      "desc": "Wake up. Open eyes. Sit up in bed. Swing legs over the side. Stand up. Walk to bathroom. Open bathroom door. Turn on light. Turn on tap. Adjust water temperature. Step into shower. Wet body. Apply soap to body. Wash body. Rinse body. Turn off shower. Step out of shower. Pick up towel. Dry body. Dry hair. Wrap towel around body. Pick up toothbrush. Apply toothpaste to toothbrush. Brush teeth. Rinse mouth. Spit into sink. Wipe face with towel. Turn off tap. Turn off light. Walk out of bathroom. Return to Bedroom 1."
    },
    {
      "time": "07:00-07:45",
      "location": "Kitchen",
      "activity": "Preparing and eating breakfast and making tea with the kettle and toaster; Member 4 joins from 07:30 to prepare breakfast, so they chat while sharing the kitchen",
      "desc": "Walk to kitchen. Open refrigerator. Take out bread. Place bread in toaster. Press toaster lever down. Open cupboard. Take out mug. Take out tea bag. Place tea bag in mug. Fill kettle with water. Turn on kettle. Wait for kettle to boil. Toast pops up. Take toast out of toaster. Place toast on plate. Spread butter on toast. Pour hot water into mug. Add milk to mug. Stir tea with spoon. Pick up toast. Eat toast. Drink tea. Member 4 enters kitchen. Member 1 says 'Good morning' to Member 4. Member 4 says 'Morning' to Member 1. Member 1 continues eating. Member 4 prepares breakfast. Member 1 finishes eating. Rinse plate. Place plate in sink. Rinse mug. Place mug in sink."
    },
    {
      "time": "07:45-08:00",
      "location": "Bedroom 1",
      "activity": "Setting up the desk and reviewing today's study plan",
      "desc": "Walk to Bedroom 1. Sit at desk. Turn on desk lamp. Open computer. Log in to computer. Open study plan document. Read study plan. Make notes on paper. Highlight tasks. Close document. Stand up."
    },
    {
      "time": "08:00-12:00",
      "location": "Bedroom 1",
      "activity": "Studying online for the Master of Education at the desk using the computer and desk lamp, attending remote lectures and reading course materials",
      "desc": "Sit at desk. Open laptop. Turn on desk lamp. Log into university portal. Join online lecture. Listen to lecturer. Type notes on laptop. Scroll through slides. Write in notebook. Adjust desk lamp. Attend lecture. Read course materials on screen. Highlight key points. Write summary. Take short break. Stand up. Stretch arms. Sit back down. Continue studying. Open additional course materials. Read. Take notes. Save notes."
    },
    {
      "time": "12:00-12:45",
      "location": "Kitchen",
      "activity": "Cooking and eating lunch, reheating food with the microwave while Member 2 cooks her own lunch on the induction cooker",
      "desc": "Walk to kitchen. Open refrigerator. Take out lunch container. Remove lid. Place container in microwave. Close microwave door. Set timer. Press start. Microwave beeps. Open microwave door. Take out container. Stir food. Walk to table. Sit down. Eat lunch. Member 2 enters kitchen. Member 1 says 'Hi' to Member 2. Member 2 says 'Hi' to Member 1. Member 2 starts cooking on induction cooker. Member 1 continues eating. Finish eating. Rinse container. Place container in sink. Stand up."
    },
    {
      "time": "12:45-13:15",
      "location": "Living Room",
      "activity": "Taking a short break, checking the phone and resting on the sofa",
      "desc": "Walk to living room. Sit on sofa. Pick up phone. Unlock phone. Scroll through social media. Read messages. Reply to message. Put phone down on sofa. Lean back. Close eyes. Rest."
    },
    {
      "time": "13:15-17:00",
      "location": "Bedroom 1",
      "activity": "Continuing online study and coursework, writing assignments on the computer and reviewing notes",
      "desc": "Walk to Bedroom 1. Sit at desk. Open computer. Open assignment document. Type on keyboard. Read notes. Highlight text. Write paragraphs. Pause. Stretch arms. Continue typing. Save document. Open browser. Research topic. Read article. Take notes. Close browser. Open notes app. Review notes. Edit notes. Save notes."
    },
    {
      "time": "17:00-17:40",
      "location": "Living Room",
      "activity": "Doing light stretching and indoor exercise together with Member 2, then resting with the fan on",
      "desc": "Walk to living room. Member 2 is there. Member 1 says 'Ready to stretch?' Member 2 says 'Yes'. Spread exercise mat on floor. Sit down on mat. Stretch arms. Stretch legs. Do yoga poses. Member 2 does same. After exercise, stand up. Roll up mat. Turn on fan. Sit on sofa. Lean back. Rest."
    },
    {
      "time": "17:40-18:30",
      "location": "Kitchen",
      "activity": "Cooking dinner with the induction cooker and rice cooker, sharing the kitchen with Member 3 who is also cooking",
      "desc": "Walk to kitchen. Open refrigerator. Take out vegetables. Wash vegetables in sink. Chop vegetables on cutting board. Turn on induction cooker. Place pan on cooker. Add oil to pan. Add chopped vegetables to pan. Stir with spatula. Turn on rice cooker. Add rice to rice cooker. Add water to rice cooker. Close rice cooker lid. Press cook button. Member 3 enters kitchen. Member 1 says 'Hi' to Member 3. Member 3 says 'Hi' to Member 1. Member 1 continues cooking. Stir vegetables. Taste food. Add salt. Turn off induction cooker. Wait for rice cooker."
    },
    {
      "time": "18:30-19:15",
      "location": "Kitchen",
      "activity": "Eating dinner together with Member 2 and Member 3",
      "desc": "Sit at table. Serve food onto plate. Pick up fork. Eat food. Chew. Swallow. Talk to Member 2. Ask 'How was your day?' Member 2 replies. Talk to Member 3. Member 3 replies. Continue eating. Drink water from glass. Finish meal. Push plate away. Stand up."
    },
    {
      "time": "19:15-19:45",
      "location": "Kitchen",
      "activity": "Washing dishes and wiping down the kitchen benches together with Member 2 and Member 3",
      "desc": "Stand up. Collect plates from table. Carry plates to sink. Turn on tap. Pick up sponge. Apply soap to sponge. Wash plate. Rinse plate under tap. Place plate in drying rack. Wash utensils. Rinse utensils. Place utensils in drying rack. Pick up cloth. Wipe kitchen bench. Member 2 washes dishes. Member 3 dries dishes. Member 1 wipes bench. Rinse cloth. Hang cloth on hook. Turn off tap."
    },
    {
      "time": "19:45-20:15",
      "location": "Bathroom",
      "activity": "Doing laundry with the washing machine and tidying up",
      "desc": "Walk to bathroom. Open washing machine door. Put dirty clothes into washing machine. Add detergent to dispenser. Close washing machine door. Set wash cycle. Press start button. Pick up clothes from floor. Place clothes in laundry basket. Wipe bathroom sink with cloth. Rinse cloth. Hang cloth on hook. Walk out of bathroom."
    },
    {
      "time": "20:15-21:15",
      "location": "Bedroom 1",
      "activity": "Relaxing, browsing the phone and reading in the bedroom while Member 2 and Member 3 use the Living Room for video calls",
      "desc": "Walk to Bedroom 1. Sit on bed. Pick up phone. Unlock phone. Browse social media. Read article on phone. Put phone down on bed. Pick up book. Open book. Read. Turn page. Continue reading. Put book down. Pick up phone. Check messages. Reply to message. Put phone down. Lean back on bed."
    },
    {
      "time": "21:15-21:45",
      "location": "Kitchen",
      "activity": "Making a hot drink and preparing a light evening snack",
      "desc": "Walk to kitchen. Open cupboard. Take out mug. Take out tea bag. Place tea bag in mug. Fill kettle with water. Turn on kettle. Wait for kettle to boil. Open refrigerator. Take out snack. Place snack on plate. Pour hot water into mug. Add milk to mug. Stir tea with spoon. Pick up plate and mug. Walk to Bedroom 1. Sit at desk. Place plate and mug on desk."
    },
    {
      "time": "21:45-22:45",
      "location": "Bedroom 1",
      "activity": "Reading course materials and planning the next day's study tasks at the desk",
      "desc": "Sit at desk. Open computer. Open course materials. Read course materials on screen. Highlight key points. Open planner. Write tasks for next day. Check calendar. Write notes. Close planner. Close computer. Drink tea. Eat snack. Stand up."
    },
    {
      "time": "22:45-23:15",
      "location": "Bathroom",
      "activity": "Night routine: washing up and brushing teeth (after Member 2's evening shower and laundry finish at 22:40)",
      "desc": "Walk to bathroom. Turn on tap. Wash face with water. Pick up toothbrush. Apply toothpaste to toothbrush. Brush teeth. Rinse mouth. Spit into sink. Wipe face with towel. Turn off tap. Turn off light. Walk out of bathroom. Return to Bedroom 1."
    },
    {
      "time": "23:15-24:00",
      "location": "Bedroom 1",
      "activity": "Winding down, dimming the desk lamp and going to sleep",
      "desc": "Walk to Bedroom 1. Sit on bed. Dim desk lamp. Pick up phone. Set alarm on phone. Put phone down on bedside table. Lie down on bed. Pull blanket over body. Close eyes. Remain still. Fall asleep."
    }
  ]
}
```

