# s3_enrich  (attempt 1)

## 对话信息

- time: 2026-09-11 00:48:31
- seq: 1
- prefix: Member 3_
- stage: s3_enrich
- attempt: 1
- ok: True

## 输入

```
You are a behavior analysis expert. Generate a detailed **behavior checklist** for Member 3's day.

Member information:
- Name: Member 3
- Age: 27
- Occupation: PhD candidate in public health, Monash University; part-time disability and aged-care support worker
- Personality: 

This member's timeline:
[
  {
    "time": "00:00-03:15",
    "location": "Bedroom 3",
    "activity": "Sleeping, though sleep is restless and frequently broken"
  },
  {
    "time": "03:15-03:45",
    "location": "Bedroom 3",
    "activity": "Waking with mild chronic pain, lying still and doing slow gentle stretches and breathing to settle back down"
  },
  {
    "time": "03:45-06:55",
    "location": "Bedroom 3",
    "activity": "Sleeping again after the pain settles"
  },
  {
    "time": "06:55-07:10",
    "location": "Bedroom 3",
    "activity": "Slow waking, lying in bed and scrolling Instagram and Messenger on phone"
  },
  {
    "time": "07:10-07:25",
    "location": "Bedroom 3",
    "activity": "Taking daily medication with water and doing gentle mobility stretches for chronic pain and stiff joints"
  },
  {
    "time": "07:25-07:55",
    "location": "Bathroom",
    "activity": "Showering, washing and getting dressed at an unhurried pace"
  },
  {
    "time": "07:55-08:40",
    "location": "Kitchen",
    "activity": "Cooking and eating a caffeine-free breakfast while listening to a public health podcast (joined by Member 2 for tea and toast from 08:10-08:25)"
  },
  {
    "time": "08:40-09:00",
    "location": "Kitchen",
    "activity": "Washing dishes and tidying up the kitchen bench"
  },
  {
    "time": "09:00-10:45",
    "location": "Bedroom 3",
    "activity": "PhD research work: literature review and thesis drafting on Computer at desk"
  },
  {
    "time": "10:45-11:00",
    "location": "Kitchen",
    "activity": "Making herbal tea and a small snack, no caffeine"
  },
  {
    "time": "11:00-12:30",
    "location": "Bedroom 3",
    "activity": "PhD data analysis and reference management on Computer"
  },
  {
    "time": "12:30-13:15",
    "location": "Kitchen",
    "activity": "Cooking and eating lunch at home"
  },
  {
    "time": "13:15-13:45",
    "location": "Out",
    "activity": "Walking through the neighbourhood as a midday break and mobility routine"
  },
  {
    "time": "13:45-14:15",
    "location": "Bedroom 3",
    "activity": "Reviewing the support shift roster and client care notes on phone, packing a small bag"
  },
  {
    "time": "14:15-14:45",
    "location": "Out",
    "activity": "Walking to the client's home for the disability and aged-care support shift"
  },
  {
    "time": "14:45-20:15",
    "location": "Out",
    "activity": "Working a disability and aged-care support shift: personal care assistance, meal preparation, medication prompting and companionship"
  },
  {
    "time": "20:15-20:45",
    "location": "Out",
    "activity": "Walking home from the support shift"
  },
  {
    "time": "20:45-21:20",
    "location": "Bedroom 3",
    "activity": "Resting and doing gentle stretches to manage chronic pain after the shift"
  },
  {
    "time": "21:20-21:50",
    "location": "Kitchen",
    "activity": "Cooking and eating a late dinner at home"
  },
  {
    "time": "21:50-22:20",
    "location": "Bathroom",
    "activity": "Evening wash and preparing for bed"
  },
  {
    "time": "22:20-22:35",
    "location": "Kitchen",
    "activity": "Cleaning up after dinner and wiping down the kitchen surfaces"
  },
  {
    "time": "22:35-23:05",
    "location": "Bedroom 3",
    "activity": "Household administration: paying bills by mobile wallet, updating the shared roster and logging maintenance tasks on Computer and phone"
  },
  {
    "time": "23:05-23:35",
    "location": "Bedroom 3",
    "activity": "Winding down: planning tomorrow, checking distant elder-care arrangements and reading quietly"
  },
  {
    "time": "23:35-24:00",
    "location": "Bedroom 3",
    "activity": "Lights out and going to sleep"
  }
]

Other household members' timelines:
{
  "Member 1": [
    {
      "time": "00:00-06:00",
      "location": "Bedroom 1",
      "activity": "Sleeping"
    },
    {
      "time": "06:00-06:35",
      "location": "Bathroom",
      "activity": "Waking up early, showering and getting dressed (using the bathroom before Member 4's 06:45-07:15 slot to avoid the shared-bathroom clash)"
    },
    {
      "time": "06:35-07:15",
      "location": "Bedroom 1",
      "activity": "Reviewing course readings, organising notes and study materials for the day"
    },
    {
      "time": "07:15-07:50",
      "location": "Kitchen",
      "activity": "Making and eating breakfast together with Member 4, packing lunch and study snacks"
    },
    {
      "time": "07:50-08:35",
      "location": "Out",
      "activity": "Commuting by public transport to Monash University campus"
    },
    {
      "time": "08:35-12:00",
      "location": "Out",
      "activity": "Attending Master of Education lectures and tutorials on campus"
    },
    {
      "time": "12:00-13:00",
      "location": "Out",
      "activity": "Eating lunch on campus while reading set course texts"
    },
    {
      "time": "13:00-16:00",
      "location": "Out",
      "activity": "Studying in the campus library and drafting assignment work on computer"
    },
    {
      "time": "16:00-16:50",
      "location": "Out",
      "activity": "Commuting home from campus"
    },
    {
      "time": "16:50-17:20",
      "location": "Bathroom",
      "activity": "Freshening up and changing into part-time work uniform (bathroom is free at this time)"
    },
    {
      "time": "17:20-17:55",
      "location": "Kitchen",
      "activity": "Cooking and eating an early dinner before the evening shift, coordinating kitchen use with Member 4 who starts cooking around 17:40"
    },
    {
      "time": "17:55-18:20",
      "location": "Out",
      "activity": "Walking to the part-time hospitality and retail job"
    },
    {
      "time": "18:20-22:20",
      "location": "Out",
      "activity": "Working the evening hospitality and retail shift"
    },
    {
      "time": "22:20-22:50",
      "location": "Out",
      "activity": "Commuting home after the shift"
    },
    {
      "time": "22:50-23:00",
      "location": "Bedroom 1",
      "activity": "Settling in and changing out of work clothes, waiting for Member 4 to finish in the bathroom before showering"
    },
    {
      "time": "23:00-23:30",
      "location": "Bathroom",
      "activity": "Showering and winding down after work (bathroom free after Member 4's 22:30-23:00 night routine)"
    },
    {
      "time": "23:30-24:00",
      "location": "Bedroom 1",
      "activity": "Preparing for bed, briefly checking phone and going to sleep"
    }
  ],
  "Member 2": [
    {
      "time": "00:00-01:30",
      "location": "Bedroom 2",
      "activity": "Late-night doomscrolling YouTube and WhatsApp on phone instead of sleeping"
    },
    {
      "time": "01:30-07:45",
      "location": "Bedroom 2",
      "activity": "Sleeping"
    },
    {
      "time": "07:45-07:55",
      "location": "Bedroom 2",
      "activity": "Waking up late, slow start and light stretching in bed while waiting for the shared bathroom to free up after Member 3's 07:25-07:55 morning slot"
    },
    {
      "time": "07:55-08:10",
      "location": "Bathroom",
      "activity": "Quick wash and brushing teeth (bathroom now free after Member 3, avoiding the 06:45-07:15 Member 4 and 07:25-07:55 Member 3 slots)"
    },
    {
      "time": "08:10-08:25",
      "location": "Kitchen",
      "activity": "Rushed breakfast of tea and toast shared with Member 3 in the kitchen, packing a thermos of tea for the day"
    },
    {
      "time": "08:25-09:10",
      "location": "Out",
      "activity": "Commuting by public transport to Monash University Caulfield campus, running behind schedule"
    },
    {
      "time": "09:10-12:30",
      "location": "Out",
      "activity": "Attending Master of Design studio classes and critique sessions at Caulfield campus"
    },
    {
      "time": "12:30-13:15",
      "location": "Out",
      "activity": "Buying and eating a budget-friendly lunch on campus that fits dietary restrictions"
    },
    {
      "time": "13:15-16:30",
      "location": "Out",
      "activity": "Working on design studio projects and print/workshop tasks on campus"
    },
    {
      "time": "16:30-17:15",
      "location": "Out",
      "activity": "Commuting home from Caulfield campus in afternoon traffic"
    },
    {
      "time": "17:15-17:45",
      "location": "Bedroom 2",
      "activity": "Changing out of day clothes and doing the daily stretching routine"
    },
    {
      "time": "17:45-18:30",
      "location": "Kitchen",
      "activity": "Cooking a daily homemade dinner that meets dietary restrictions and eating it in the kitchen alongside Member 4, who is cooking and eating dinner from 17:40"
    },
    {
      "time": "18:30-19:00",
      "location": "Kitchen",
      "activity": "Washing dishes and wiping down shared kitchen counters after cooking"
    },
    {
      "time": "19:00-21:00",
      "location": "Bedroom 2",
      "activity": "Doing freelance creative work on computer and monitor at desk"
    },
    {
      "time": "21:00-21:40",
      "location": "Bathroom",
      "activity": "Showering and putting a load of laundry in the washing machine (bathroom free before Member 3's 22:20-22:50, Member 4's 22:30-23:00 and Member 1's 23:00-23:30 slots)"
    },
    {
      "time": "21:40-22:40",
      "location": "Living Room",
      "activity": "Relaxing with TV and game console to unwind"
    },
    {
      "time": "22:40-24:00",
      "location": "Bedroom 2",
      "activity": "Lying in bed browsing YouTube and WhatsApp on phone before settling down to sleep"
    }
  ],
  "Member 4": [
    {
      "time": "00:00-06:45",
      "location": "Bedroom 4",
      "activity": "Sleeping"
    },
    {
      "time": "06:45-07:15",
      "location": "Bathroom",
      "activity": "Shower, brushing teeth and getting dressed for the day (bathroom free: Member 1 finished at 06:35 and Member 3 starts at 07:25)"
    },
    {
      "time": "07:15-07:50",
      "location": "Kitchen",
      "activity": "Preparing and eating breakfast together with Member 1"
    },
    {
      "time": "07:50-08:20",
      "location": "Out",
      "activity": "Commuting to university campus (Member 1 departs at the same time)"
    },
    {
      "time": "08:20-12:00",
      "location": "Out",
      "activity": "Attending Bachelor of Commerce and IT lectures and tutorials"
    },
    {
      "time": "12:00-12:40",
      "location": "Out",
      "activity": "Eating lunch on campus"
    },
    {
      "time": "12:40-17:00",
      "location": "Out",
      "activity": "Studying in the library and attending afternoon classes"
    },
    {
      "time": "17:00-17:40",
      "location": "Out",
      "activity": "Commuting home from campus"
    },
    {
      "time": "17:40-18:20",
      "location": "Kitchen",
      "activity": "Cooking and eating dinner (joined by Member 1 until 17:55 and Member 2 from 17:45)"
    },
    {
      "time": "18:20-19:00",
      "location": "Living Room",
      "activity": "Relaxing and watching TV"
    },
    {
      "time": "19:00-21:00",
      "location": "Bedroom 4",
      "activity": "Conducting online tutoring sessions using the computer"
    },
    {
      "time": "21:00-21:20",
      "location": "Kitchen",
      "activity": "Making a hot drink and having a snack (kitchen free before Member 3's dinner at 21:20)"
    },
    {
      "time": "21:20-22:30",
      "location": "Bedroom 4",
      "activity": "Doing freelance analyst work on the computer"
    },
    {
      "time": "22:30-23:00",
      "location": "Bathroom",
      "activity": "Showering and completing night routine (bathroom free: Member 3 finished at 22:20 and Member 1 starts at 23:00)"
    },
    {
      "time": "23:00-24:00",
      "location": "Bedroom 4",
      "activity": "Winding down on the phone and falling asleep"
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
  "member": "Member 3",
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
**The member field must exactly equal "Member 3" and names mentioned in descriptions must exactly match the supplied household members.**

```

## Schema

```json
(none)
```

## 返回(原始)

```
{
  "member": "Member 3",
  "enriched_activities": [
    {
      "time": "00:00-03:15",
      "location": "Bedroom 3",
      "activity": "Sleeping, though sleep is restless and frequently broken",
      "desc": "Lie in bed. Close eyes. Turn onto right side. Pull blanket up to shoulders. Shift legs. Open eyes. Look at ceiling. Turn onto left side. Adjust pillow. Close eyes. Breathe deeply. Turn onto back. Move arm. Turn onto right side again. Open eyes briefly. Close eyes. Shift position. Pull blanket. Turn onto left side. Close eyes."
    },
    {
      "time": "03:15-03:45",
      "location": "Bedroom 3",
      "activity": "Waking with mild chronic pain, lying still and doing slow gentle stretches and breathing to settle back down",
      "desc": "Open eyes. Lie still on back. Inhale slowly. Exhale slowly. Lift right arm. Rotate wrist clockwise. Rotate wrist counterclockwise. Lower right arm. Lift left arm. Rotate wrist clockwise. Rotate wrist counterclockwise. Lower left arm. Bend right knee. Straighten right leg. Bend left knee. Straighten left leg. Inhale deeply. Exhale slowly. Close eyes."
    },
    {
      "time": "03:45-06:55",
      "location": "Bedroom 3",
      "activity": "Sleeping again after the pain settles",
      "desc": "Close eyes. Turn onto right side. Pull blanket. Breathe slowly. Shift legs. Turn onto left side. Adjust pillow. Sleep. Open eyes briefly. Turn onto back. Close eyes. Turn onto right side. Pull blanket. Shift position. Open eyes. Look at clock. Close eyes. Turn onto left side. Breathe deeply. Sleep."
    },
    {
      "time": "06:55-07:10",
      "location": "Bedroom 3",
      "activity": "Slow waking, lying in bed and scrolling Instagram and Messenger on phone",
      "desc": "Open eyes. Stretch arms. Reach for phone on bedside table. Pick up phone. Press power button. Swipe screen. Enter passcode. Open Instagram. Scroll feed. Tap like on post. Open Messenger. Read message from friend. Tap reply. Type message. Send. Put phone down on chest. Close eyes briefly. Open eyes. Pick up phone again. Scroll Instagram. Put phone down."
    },
    {
      "time": "07:10-07:25",
      "location": "Bedroom 3",
      "activity": "Taking daily medication with water and doing gentle mobility stretches for chronic pain and stiff joints",
      "desc": "Sit up. Pick up medication bottle. Open cap. Take pill. Drink water. Stand up. Stretch arms overhead. Bend forward. Straighten up. Sit on bed. Rotate ankles."
    },
    {
      "time": "07:25-07:55",
      "location": "Bathroom",
      "activity": "Showering, washing and getting dressed at an unhurried pace",
      "desc": "Walk to bathroom. Turn on light. Turn on shower. Adjust water. Step in. Wet body. Apply soap. Wash body. Rinse. Shampoo hair. Rinse hair. Turn off shower. Step out. Pick up towel. Dry body. Walk to bedroom. Open wardrobe. Pick clothes. Put on underwear, shirt, pants. Comb hair."
    },
    {
      "time": "07:55-08:40",
      "location": "Kitchen",
      "activity": "Cooking and eating a caffeine-free breakfast while listening to a public health podcast (joined by Member 2 for tea and toast from 08:10-08:25)",
      "desc": "Walk to kitchen. Open refrigerator. Take out eggs and bread. Place pan on induction cooker. Turn on cooker. Crack eggs. Cook eggs. Toast bread. Pour herbal tea. Sit at table. Open podcast on phone. Play podcast. Eat breakfast. At 08:10, Member 2 enters. Greet Member 2. Pour tea for Member 2. Share toast. Talk with Member 2. At 08:25, Member 2 leaves. Finish eating. Clear dishes."
    },
    {
      "time": "08:40-09:00",
      "location": "Kitchen",
      "activity": "Washing dishes and tidying up the kitchen bench",
      "desc": "Collect plates and cups. Carry to sink. Turn on tap. Rinse dishes. Apply dish soap to sponge. Scrub plates. Scrub cups. Rinse dishes. Place in drying rack. Wipe counter with cloth. Turn off tap."
    },
    {
      "time": "09:00-10:45",
      "location": "Bedroom 3",
      "activity": "PhD research work: literature review and thesis drafting on Computer at desk",
      "desc": "Walk to bedroom 3. Sit at desk. Turn on desk lamp. Open laptop. Log in. Open browser. Go to academic database. Search for articles. Read abstract. Download PDF. Open PDF. Read article. Take notes in notebook. Open Word document. Type thesis section. Save document. Open second article. Read. Summarize. Type more. Check references. Save again."
    },
    {
      "time": "10:45-11:00",
      "location": "Kitchen",
      "activity": "Making herbal tea and a small snack, no caffeine",
      "desc": "Walk to kitchen. Fill kettle. Boil water. Place tea bag in mug. Pour water. Wait. Remove tea bag. Take biscuits from pantry. Sit. Drink tea. Eat biscuits."
    },
    {
      "time": "11:00-12:30",
      "location": "Bedroom 3",
      "activity": "PhD data analysis and reference management on Computer",
      "desc": "Return to desk. Open statistical software. Import dataset. Run descriptive statistics. Check output. Run regression. Check results. Open reference manager. Add new reference. Edit citation. Format bibliography. Open thesis document. Insert citation. Save document. Run another analysis. Check for errors. Save again. Close software."
    },
    {
      "time": "12:30-13:15",
      "location": "Kitchen",
      "activity": "Cooking and eating lunch at home",
      "desc": "Walk to kitchen. Open refrigerator. Take out vegetables, tofu, rice. Wash vegetables. Chop vegetables. Place pan on induction cooker. Turn on cooker. Add oil. Add vegetables. Stir. Add tofu. Add soy sauce. Stir. Turn off cooker. Place rice in bowl. Add cooked vegetables. Sit at table. Eat lunch. Drink water. Clear dishes."
    },
    {
      "time": "13:15-13:45",
      "location": "Out",
      "activity": "Walking through the neighbourhood as a midday break and mobility routine",
      "desc": "Put on shoes. Open front door. Step outside. Close door. Walk along sidewalk. Turn left at corner. Walk past park. Continue walking. Turn right at next street. Walk uphill. Reach top. Turn around. Walk back downhill. Turn left. Walk past shops. Turn right. Walk home. Open front door. Enter. Close door. Remove shoes."
    },
    {
      "time": "13:45-14:15",
      "location": "Bedroom 3",
      "activity": "Reviewing the support shift roster and client care notes on phone, packing a small bag",
      "desc": "Sit on bed. Pick up phone. Open roster app. Read shift times. Open notes app. Read client care notes. Put phone down. Open backpack. Place water bottle inside. Place snacks inside. Place gloves inside. Place hand sanitizer inside. Zip backpack. Pick up phone again. Check messages. Put phone down. Stand up."
    },
    {
      "time": "14:15-14:45",
      "location": "Out",
      "activity": "Walking to the client's home for the disability and aged-care support shift",
      "desc": "Pick up backpack. Walk to front door. Open door. Step outside. Close door. Lock door. Walk along sidewalk. Turn left at corner. Cross street. Walk past supermarket. Turn right. Walk two blocks. Arrive at client's house. Walk up driveway. Knock on door."
    },
    {
      "time": "14:45-20:15",
      "location": "Out",
      "activity": "Working a disability and aged-care support shift: personal care assistance, meal preparation, medication prompting and companionship",
      "desc": "Enter client's home. Greet client. Assist with shower. Help dress. Prepare lunch. Cook meal. Serve meal. Sit with client. Prompt medication. Give medication. Wash dishes. Sit in living room. Talk. Play cards. Prepare afternoon tea. Serve tea. Assist with walking. Prepare dinner. Cook dinner. Serve dinner. Prompt evening medication. Assist to bed. Say goodbye."
    },
    {
      "time": "20:15-20:45",
      "location": "Out",
      "activity": "Walking home from the support shift",
      "desc": "Say goodbye to client. Walk out front door. Close door. Walk down driveway. Turn left. Walk along sidewalk. Cross street. Walk past supermarket. Turn right at corner. Walk two blocks. Turn left. Walk along park. Turn right. Walk home. Open front door. Enter. Close door."
    },
    {
      "time": "20:45-21:20",
      "location": "Bedroom 3",
      "activity": "Resting and doing gentle stretches to manage chronic pain after the shift",
      "desc": "Walk to bedroom 3. Sit on bed. Lie down on back. Inhale deeply. Exhale slowly. Lift right leg. Stretch hamstring. Lower leg. Lift left leg. Stretch hamstring. Lower leg. Bend knees. Rotate hips. Straighten legs. Sit up. Rotate neck left. Rotate neck right. Roll shoulders. Stand up. Walk to kitchen."
    },
    {
      "time": "21:20-21:50",
      "location": "Kitchen",
      "activity": "Cooking and eating a late dinner at home",
      "desc": "Open refrigerator. Take out leftovers. Place on plate. Put plate in microwave. Close door. Press start. Wait. Remove plate. Sit at table. Eat dinner. Drink water. Clear plate. Wash plate. Put away leftovers. Wipe table."
    },
    {
      "time": "21:50-22:20",
      "location": "Bathroom",
      "activity": "Evening wash and preparing for bed",
      "desc": "Walk to bathroom. Turn on tap. Wet face. Apply cleanser. Rinse face. Pat dry. Pick up toothbrush. Apply toothpaste. Brush teeth. Rinse mouth. Spit. Turn off tap. Walk to bedroom. Open wardrobe. Take out pajamas. Put on pajamas. Fold day clothes. Place on chair."
    },
    {
      "time": "22:20-22:35",
      "location": "Kitchen",
      "activity": "Cleaning up after dinner and wiping down the kitchen surfaces",
      "desc": "Walk to kitchen. Collect dishes. Carry to sink. Wash dishes. Rinse. Place in drying rack. Spray counter with cleaner. Wipe counter with cloth. Turn off light."
    },
    {
      "time": "22:35-23:05",
      "location": "Bedroom 3",
      "activity": "Household administration: paying bills by mobile wallet, updating the shared roster and logging maintenance tasks on Computer and phone",
      "desc": "Walk to bedroom 3. Sit at desk. Open laptop. Log in. Open banking website. Pay electricity bill. Pay internet bill. Open shared roster document. Update roster. Open maintenance log. Add task. Save. Pick up phone. Open mobile wallet. Confirm payment. Put phone down. Close laptop."
    },
    {
      "time": "23:05-23:35",
      "location": "Bedroom 3",
      "activity": "Winding down: planning tomorrow, checking distant elder-care arrangements and reading quietly",
      "desc": "Open planner. Write tomorrow's tasks. Check calendar. Pick up phone. Open messaging app. Send message to elder-care facility. Read reply. Put phone down. Pick up book. Open book. Read pages. Close book. Place book on bedside table."
    },
    {
      "time": "23:35-24:00",
      "location": "Bedroom 3",
      "activity": "Lights out and going to sleep",
      "desc": "Turn off desk lamp. Lie down in bed. Pull blanket up. Close eyes. Breathe slowly. Turn onto side. Adjust pillow. Close eyes. Sleep."
    }
  ]
}
```

