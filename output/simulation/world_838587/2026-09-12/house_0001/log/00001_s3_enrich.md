# s3_enrich  (attempt 1)

## 对话信息

- time: 2026-09-11 00:51:07
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
    "time": "00:00-08:00",
    "location": "Bedroom 3",
    "activity": "Sleeping (slow, disrupted sleep after a high-stress week)"
  },
  {
    "time": "08:00-08:40",
    "location": "Bedroom 3",
    "activity": "Slow waking in bed, taking daily medication, gentle stretching to ease mild chronic pain (bathroom is occupied by Member 4 until 08:40, so this is shifted to fill the wait)"
  },
  {
    "time": "08:40-09:10",
    "location": "Bathroom",
    "activity": "Slow morning routine: washing, showering and getting dressed (bathroom free after Member 4's 08:00-08:40 slot and before Member 2's 09:30 slot)"
  },
  {
    "time": "09:10-09:55",
    "location": "Kitchen",
    "activity": "Cooking and eating a caffeine-free breakfast at home (overlapping briefly with Member 4's breakfast and just before Member 2's 09:55 breakfast)"
  },
  {
    "time": "09:55-10:15",
    "location": "Kitchen",
    "activity": "Clearing dishes and tidying the kitchen surfaces in her chaotic-but-functional way, sharing the kitchen with Member 2 who is brewing tea and cooking breakfast"
  },
  {
    "time": "10:15-11:00",
    "location": "Bedroom 3",
    "activity": "Household admin on her computer: paying bills by mobile wallet, checking support shift rosters and replying to messages on Messenger"
  },
  {
    "time": "11:00-11:45",
    "location": "Out",
    "activity": "Walking to the local shops and doing the weekly grocery shop, paying by mobile wallet (Member 2 is also out grocery shopping from 11:30)"
  },
  {
    "time": "11:45-12:15",
    "location": "Kitchen",
    "activity": "Unpacking and sorting groceries at home, shared with Member 4 unpacking groceries and prepping lunch, while Member 1 eats lunch"
  },
  {
    "time": "12:15-13:00",
    "location": "Kitchen",
    "activity": "Cooking a simple lunch at home (sharing the kitchen with Member 4 cooking and eating lunch from 12:20)"
  },
  {
    "time": "13:00-13:45",
    "location": "Kitchen",
    "activity": "Eating lunch at home together with Member 2 while checking messages"
  },
  {
    "time": "13:45-14:30",
    "location": "Living Room",
    "activity": "Resting on the couch with the fan on, watching TV to manage pain and stress (living room free while Member 2 works in Bedroom 2 and Member 4 tutors in Bedroom 4)"
  },
  {
    "time": "14:30-15:30",
    "location": "Out",
    "activity": "Gentle afternoon walk around the neighbourhood for light exercise and fresh air"
  },
  {
    "time": "15:30-16:15",
    "location": "Bathroom",
    "activity": "Loading and running the washing machine, then folding laundry (washing machine free, between Member 1's 10:00-10:30 and Member 4's 18:00-18:30 loads)"
  },
  {
    "time": "16:15-17:00",
    "location": "Bedroom 3",
    "activity": "PhD research reading and note-taking on her computer with the desk lamp on"
  },
  {
    "time": "17:00-17:45",
    "location": "Bedroom 3",
    "activity": "Video call on Messenger to check in on her elderly relative from a distance and review caregiving arrangements"
  },
  {
    "time": "17:45-18:30",
    "location": "Kitchen",
    "activity": "Preparing dinner from scratch at home, timed so it is ready for the shared household dinner at 18:30"
  },
  {
    "time": "18:30-19:30",
    "location": "Kitchen",
    "activity": "Eating dinner at home together with Member 1, Member 2 and Member 4"
  },
  {
    "time": "19:30-20:00",
    "location": "Kitchen",
    "activity": "Washing up and wiping down the kitchen after dinner"
  },
  {
    "time": "20:00-21:30",
    "location": "Living Room",
    "activity": "Relaxing with the TV and game console and scrolling Instagram on her phone, together with Member 1, Member 2 and Member 4"
  },
  {
    "time": "21:30-22:15",
    "location": "Bedroom 3",
    "activity": "Planning the coming week on her computer: support shift roster, bills, maintenance tasks and a structured group activity she leads"
  },
  {
    "time": "22:15-22:45",
    "location": "Bedroom 3",
    "activity": "Light reading and Messenger chats to settle a busy mind while waiting for the bathroom to free up"
  },
  {
    "time": "22:45-23:15",
    "location": "Bathroom",
    "activity": "Evening hygiene routine: brushing teeth and washing up before bed (bathroom free after Member 4's 22:15-22:45 slot)"
  },
  {
    "time": "23:15-23:45",
    "location": "Bedroom 3",
    "activity": "Winding down in bed with light reading and Messenger chats"
  },
  {
    "time": "23:45-24:00",
    "location": "Bedroom 3",
    "activity": "Lights out and going to sleep"
  }
]

Other household members' timelines:
{
  "Member 1": [
    {
      "time": "00:00-07:30",
      "location": "Bedroom 1",
      "activity": "Sleeping"
    },
    {
      "time": "07:30-08:00",
      "location": "Bathroom",
      "activity": "Morning routine (washing, brushing teeth) - scheduled early to avoid the bathroom being occupied by Member 4 (08:00-08:40) and Member 3 (08:30-09:00)"
    },
    {
      "time": "08:00-08:30",
      "location": "Kitchen",
      "activity": "Preparing and eating breakfast, ahead of Member 4 and Member 3's breakfast slots"
    },
    {
      "time": "08:30-10:00",
      "location": "Bedroom 1",
      "activity": "Studying Master of Education coursework on computer"
    },
    {
      "time": "10:00-10:30",
      "location": "Bathroom",
      "activity": "Doing laundry using the washing machine (free slot, no conflict with Member 3, Member 4 or Member 2's laundry times)"
    },
    {
      "time": "10:30-11:00",
      "location": "Bedroom 1",
      "activity": "Tidying room and organizing study materials"
    },
    {
      "time": "11:00-11:30",
      "location": "Bedroom 1",
      "activity": "Reviewing study notes quietly while the kitchen is busy with Member 3 and Member 4's grocery unloading"
    },
    {
      "time": "11:30-12:30",
      "location": "Kitchen",
      "activity": "Preparing and eating lunch, sharing the kitchen with Member 3 unpacking groceries and Member 4 prepping lunch ingredients"
    },
    {
      "time": "12:30-13:00",
      "location": "Living Room",
      "activity": "Relaxing and watching TV before the work shift"
    },
    {
      "time": "13:00-18:00",
      "location": "Out",
      "activity": "Working part-time shift at hospitality/retail job"
    },
    {
      "time": "18:00-18:30",
      "location": "Out",
      "activity": "Commuting home from work"
    },
    {
      "time": "18:30-19:30",
      "location": "Kitchen",
      "activity": "Cooking dinner from scratch and eating it together with Member 2, Member 3 and Member 4, who are also preparing dinner at this time"
    },
    {
      "time": "19:30-21:30",
      "location": "Living Room",
      "activity": "Watching TV or playing video games together with Member 2 and Member 4 to unwind"
    },
    {
      "time": "21:30-22:00",
      "location": "Bathroom",
      "activity": "Evening hygiene routine (showering) - timed before Member 3 and Member 4's 22:15-22:45 bathroom use"
    },
    {
      "time": "22:00-23:00",
      "location": "Bedroom 1",
      "activity": "Reading or listening to music before bed"
    },
    {
      "time": "23:00-24:00",
      "location": "Bedroom 1",
      "activity": "Preparing for bed and going to sleep"
    }
  ],
  "Member 2": [
    {
      "time": "00:00-01:30",
      "location": "Bedroom 2",
      "activity": "Lying in bed scrolling YouTube and WhatsApp, delaying sleep despite an early alarm habit"
    },
    {
      "time": "01:30-09:30",
      "location": "Bedroom 2",
      "activity": "Sleeping in after a late night, catching up on rest on a weekend morning"
    },
    {
      "time": "09:30-09:55",
      "location": "Bathroom",
      "activity": "Washing face, brushing teeth and taking a warm shower to wake up slowly (bathroom free, Member 3 finished at 09:00 and Member 4 at 08:40)"
    },
    {
      "time": "09:55-10:30",
      "location": "Kitchen",
      "activity": "Boiling the kettle and brewing a strong cup of tea, then cooking a breakfast that fits dietary restrictions"
    },
    {
      "time": "10:30-10:50",
      "location": "Bedroom 2",
      "activity": "Doing daily stretching routine and getting dressed for the day"
    },
    {
      "time": "10:50-11:30",
      "location": "Living Room",
      "activity": "Tidying the shared living space and catching up on overdue cleaning chores while Member 3 and Member 4 are out grocery shopping"
    },
    {
      "time": "11:30-12:30",
      "location": "Out",
      "activity": "Grocery shopping at the local market, checking prices carefully and picking up weekly staples"
    },
    {
      "time": "12:30-13:00",
      "location": "Out",
      "activity": "Driving back home with the groceries"
    },
    {
      "time": "13:00-13:45",
      "location": "Kitchen",
      "activity": "Cooking a simple lunch at home and eating it together with Member 3 while checking messages"
    },
    {
      "time": "13:45-15:45",
      "location": "Bedroom 2",
      "activity": "Working on freelance design projects at the computer and monitor, refining a client layout"
    },
    {
      "time": "15:45-16:15",
      "location": "Kitchen",
      "activity": "Making another cup of tea and having a small snack while standing at the counter"
    },
    {
      "time": "16:15-18:00",
      "location": "Bedroom 2",
      "activity": "Continuing freelance creative work and sketching concepts with art supplies on the desk"
    },
    {
      "time": "18:00-18:30",
      "location": "Living Room",
      "activity": "Doing a slow stretching session and resting the eyes away from screens"
    },
    {
      "time": "18:30-19:30",
      "location": "Kitchen",
      "activity": "Cooking dinner from scratch and eating it together with Member 1, Member 3 and Member 4"
    },
    {
      "time": "19:30-21:00",
      "location": "Living Room",
      "activity": "Watching TV and playing a game on the console with Member 1 and Member 4 to unwind"
    },
    {
      "time": "21:00-21:30",
      "location": "Bathroom",
      "activity": "Taking a quick shower and starting a load of laundry in the washing machine (bathroom and washing machine free, before Member 1's 21:30 shower)"
    },
    {
      "time": "21:30-23:15",
      "location": "Out",
      "activity": "Meeting a large group of friends at a cafe and live music event, staying out socially"
    },
    {
      "time": "23:15-23:30",
      "location": "Out",
      "activity": "Driving home from the social event"
    },
    {
      "time": "23:30-24:00",
      "location": "Bedroom 2",
      "activity": "Lying in bed browsing YouTube and WhatsApp, catching up on messages before sleep"
    }
  ],
  "Member 4": [
    {
      "time": "00:00-08:00",
      "location": "Bedroom 4",
      "activity": "Sleeping"
    },
    {
      "time": "08:00-08:40",
      "location": "Bathroom",
      "activity": "Showering and morning wash"
    },
    {
      "time": "08:40-09:20",
      "location": "Kitchen",
      "activity": "Boiling the kettle, toasting bread and eating breakfast, overlapping briefly with Member 3's breakfast"
    },
    {
      "time": "09:20-10:30",
      "location": "Bedroom 4",
      "activity": "Studying Commerce and IT course readings on the computer"
    },
    {
      "time": "10:30-11:45",
      "location": "Out",
      "activity": "Grocery shopping for the week; meets Member 3 at the local shops from 11:00 and returns together"
    },
    {
      "time": "11:45-12:20",
      "location": "Kitchen",
      "activity": "Unpacking groceries and prepping lunch ingredients with Member 3"
    },
    {
      "time": "12:20-13:10",
      "location": "Kitchen",
      "activity": "Cooking and eating lunch, sharing the kitchen with Member 3 and Member 2"
    },
    {
      "time": "13:10-14:40",
      "location": "Bedroom 4",
      "activity": "Running an online tutoring session for students"
    },
    {
      "time": "14:40-15:40",
      "location": "Living Room",
      "activity": "Watching TV and playing on the game console"
    },
    {
      "time": "15:40-17:00",
      "location": "Bedroom 4",
      "activity": "Doing freelance analyst work on the computer"
    },
    {
      "time": "17:00-18:00",
      "location": "Out",
      "activity": "Walking and light outdoor exercise"
    },
    {
      "time": "18:00-18:30",
      "location": "Bathroom",
      "activity": "Running the washing machine and taking a shower"
    },
    {
      "time": "18:30-19:30",
      "location": "Kitchen",
      "activity": "Cooking dinner and eating it together with Member 1, Member 2 and Member 3"
    },
    {
      "time": "19:30-21:15",
      "location": "Living Room",
      "activity": "Relaxing with TV and game console with Member 1, Member 2 and Member 3"
    },
    {
      "time": "21:15-22:15",
      "location": "Bedroom 4",
      "activity": "Reviewing lecture notes and planning the study week"
    },
    {
      "time": "22:15-22:45",
      "location": "Bathroom",
      "activity": "Evening hygiene routine and brushing teeth"
    },
    {
      "time": "22:45-24:00",
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
      "time": "00:00-08:00",
      "location": "Bedroom 3",
      "activity": "Sleeping (slow, disrupted sleep after a high-stress week)",
      "desc": "Lies on back. Closes eyes. Breathes slowly. Turns to left side. Pulls blanket up. Turns to right side. Adjusts pillow. Stretches legs. Remains still. Sighs. Turns again. Lies on stomach. Pulls blanket down. Turns to back. Opens eyes briefly. Closes eyes. Remains still."
    },
    {
      "time": "08:00-08:40",
      "location": "Bedroom 3",
      "activity": "Slow waking in bed, taking daily medication, gentle stretching to ease mild chronic pain (bathroom is occupied by Member 4 until 08:40, so this is shifted to fill the wait)",
      "desc": "Opens eyes. Stretches arms. Yawns. Sits up. Reaches to bedside table. Picks up medication bottle. Opens cap. Takes out pill. Puts pill in mouth. Picks up water glass. Drinks water. Puts glass down. Closes bottle. Puts bottle back. Stretches legs. Rotates ankles. Bends forward. Reaches for toes. Sits up. Rotates neck. Looks at clock."
    },
    {
      "time": "08:40-09:10",
      "location": "Bathroom",
      "activity": "Slow morning routine: washing, showering and getting dressed (bathroom free after Member 4's 08:00-08:40 slot and before Member 2's 09:30 slot)",
      "desc": "Walks to bathroom. Opens door. Turns on light. Closes door. Turns on shower. Adjusts water temperature. Undresses. Steps into shower. Wets body. Applies soap to body. Scrubs body. Rinses body. Applies shampoo to hair. Scrubs hair. Rinses hair. Turns off shower. Steps out of shower. Picks up towel. Dries body. Dries hair. Wraps towel around body. Walks to sink. Turns on tap. Picks up toothbrush. Applies toothpaste. Brushes teeth. Rinses mouth. Spits. Turns off tap. Wipes face with towel. Opens cabinet. Takes out clothes. Puts on underwear. Puts on pants. Puts on shirt. Puts on socks. Combs hair."
    },
    {
      "time": "09:10-09:55",
      "location": "Kitchen",
      "activity": "Cooking and eating a caffeine-free breakfast at home (overlapping briefly with Member 4's breakfast and just before Member 2's 09:55 breakfast)",
      "desc": "Walks to kitchen. Opens fridge. Takes out eggs, milk, bread. Closes fridge. Takes pan from cupboard. Places pan on stove. Turns on stove. Cracks eggs into bowl. Whisk eggs. Pours eggs into pan. Cooks eggs. Flips eggs. Turns off stove. Places eggs on plate. Toasts bread. Spreads butter. Pours milk into glass. Sits at table. Picks up fork. Eats eggs. Drinks milk. Eats toast. Wipes mouth with napkin. Says 'Morning' to Member 4. Continues eating. Finishes meal."
    },
    {
      "time": "09:55-10:15",
      "location": "Kitchen",
      "activity": "Clearing dishes and tidying the kitchen surfaces in her chaotic-but-functional way, sharing the kitchen with Member 2 who is brewing tea and cooking breakfast",
      "desc": "Stands up. Picks up plate. Picks up fork. Scrapes food into bin. Stacks dishes. Carries to sink. Turns on tap. Rinses dishes. Places dishes in dishwasher. Wipes counter with cloth. Wrings cloth. Wipes table. Picks up crumbs. Throws in bin. Says 'Hi' to Member 2. Continues wiping."
    },
    {
      "time": "10:15-11:00",
      "location": "Bedroom 3",
      "activity": "Household admin on her computer: paying bills by mobile wallet, checking support shift rosters and replying to messages on Messenger",
      "desc": "Walks to bedroom. Sits at desk. Opens laptop. Turns on laptop. Enters password. Opens browser. Goes to banking website. Logs in. Enters payment details. Picks up phone. Opens mobile wallet. Scans QR code. Confirms payment. Puts phone down. Opens email. Opens roster attachment. Reads roster. Opens Messenger. Clicks on message. Types reply. Sends reply. Closes laptop."
    },
    {
      "time": "11:00-11:45",
      "location": "Out",
      "activity": "Walking to the local shops and doing the weekly grocery shop, paying by mobile wallet (Member 2 is also out grocery shopping from 11:30)",
      "desc": "Puts on shoes. Picks up reusable bags. Walks out of house. Walks along street. Enters grocery store. Picks up basket. Walks to produce section. Picks up apples. Puts in basket. Walks to dairy section. Picks up milk. Puts in basket. Walks to bakery. Picks up bread. Puts in basket. Walks to checkout. Places items on counter. Picks up phone. Opens mobile wallet. Scans QR code. Pays. Puts phone away. Picks up bags. Walks out. Meets Member 4 at store entrance. Says 'Hi'. Walks home with Member 4."
    },
    {
      "time": "11:45-12:15",
      "location": "Kitchen",
      "activity": "Unpacking and sorting groceries at home, shared with Member 4 unpacking groceries and prepping lunch, while Member 1 eats lunch",
      "desc": "Enters kitchen. Places bags on counter. Opens bag. Takes out apples. Puts in fruit bowl. Takes out milk. Puts in fridge. Takes out bread. Puts in bread bin. Takes out other items. Puts in pantry. Talks to Member 4 about groceries. Opens bag. Takes out vegetables. Puts in fridge. Closes fridge. Continues unpacking."
    },
    {
      "time": "12:15-13:00",
      "location": "Kitchen",
      "activity": "Cooking a simple lunch at home (sharing the kitchen with Member 4 cooking and eating lunch from 12:20)",
      "desc": "Washes hands. Opens fridge. Takes out vegetables. Closes fridge. Takes out cutting board. Takes out knife. Chops vegetables. Takes out pan. Places on stove. Turns on stove. Adds oil. Adds vegetables. Stirs. Adds spices. Cooks. Turns off stove. Places on plate. Sets plate on table."
    },
    {
      "time": "13:00-13:45",
      "location": "Kitchen",
      "activity": "Eating lunch at home together with Member 2 while checking messages",
      "desc": "Sits at table. Picks up fork. Eats. Picks up phone. Opens Messenger. Reads message. Types reply. Sends reply. Puts phone down. Continues eating. Drinks water. Picks up phone again. Scrolls feed. Puts phone down. Finishes meal."
    },
    {
      "time": "13:45-14:30",
      "location": "Living Room",
      "activity": "Resting on the couch with the fan on, watching TV to manage pain and stress (living room free while Member 2 works in Bedroom 2 and Member 4 tutors in Bedroom 4)",
      "desc": "Walks to living room. Sits on couch. Turns on fan. Picks up remote. Turns on TV. Changes channel. Lies down. Puts feet up. Watches TV. Adjusts fan speed. Changes channel again. Watches TV."
    },
    {
      "time": "14:30-15:30",
      "location": "Out",
      "activity": "Gentle afternoon walk around the neighbourhood for light exercise and fresh air",
      "desc": "Stands up. Puts on shoes. Walks out of house. Walks along sidewalk. Turns corner. Walks past park. Continues walking. Turns around. Walks back. Enters house."
    },
    {
      "time": "15:30-16:15",
      "location": "Bathroom",
      "activity": "Loading and running the washing machine, then folding laundry (washing machine free, between Member 1's 10:00-10:30 and Member 4's 18:00-18:30 loads)",
      "desc": "Walks to bathroom. Opens washing machine door. Picks up laundry basket. Puts clothes into washing machine. Adds detergent. Closes door. Turns dial to set cycle. Presses start button. Waits. Machine runs. When done, opens door. Takes out clothes. Puts in basket. Places basket on floor. Picks up item. Folds. Places folded item on counter. Picks up another item. Folds. Places on counter. Repeats folding. Closes washing machine door."
    },
    {
      "time": "16:15-17:00",
      "location": "Bedroom 3",
      "activity": "PhD research reading and note-taking on her computer with the desk lamp on",
      "desc": "Walks to bedroom. Sits at desk. Turns on desk lamp. Opens laptop. Opens PDF document. Scrolls through pages. Highlights text. Opens note-taking app. Types notes. Scrolls back. Reads. Types more notes. Saves document."
    },
    {
      "time": "17:00-17:45",
      "location": "Bedroom 3",
      "activity": "Video call on Messenger to check in on her elderly relative from a distance and review caregiving arrangements",
      "desc": "Opens Messenger. Clicks on relative's contact. Clicks video call. Waits for answer. Greets relative. Talks. Listens. Nods. Writes down notes. Talks. Listens. Ends call. Closes Messenger."
    },
    {
      "time": "17:45-18:30",
      "location": "Kitchen",
      "activity": "Preparing dinner from scratch at home, timed so it is ready for the shared household dinner at 18:30",
      "desc": "Walks to kitchen. Opens fridge. Takes out ingredients. Closes fridge. Chops vegetables. Turns on stove. Places pan. Adds oil. Adds ingredients. Stirs. Adds sauce. Simmers. Stirs. Turns off stove. Sets table."
    },
    {
      "time": "18:30-19:30",
      "location": "Kitchen",
      "activity": "Eating dinner at home together with Member 1, Member 2 and Member 4",
      "desc": "Sits at table. Serves food onto plate. Picks up fork. Eats. Talks to Member 1. Talks to Member 2. Talks to Member 4. Laughs. Drinks water. Continues eating. Finishes meal. Puts fork down."
    },
    {
      "time": "19:30-20:00",
      "location": "Kitchen",
      "activity": "Washing up and wiping down the kitchen after dinner",
      "desc": "Stands up. Picks up plates. Stacks dishes. Carries to sink. Turns on tap. Washes dishes. Rinses. Places in drying rack. Wipes counter. Wipes table. Wrings cloth. Wipes stove. Turns off tap."
    },
    {
      "time": "20:00-21:30",
      "location": "Living Room",
      "activity": "Relaxing with the TV and game console and scrolling Instagram on her phone, together with Member 1, Member 2 and Member 4",
      "desc": "Walks to living room. Sits on couch. Picks up controller. Plays game. Passes controller to Member 1. Picks up phone. Opens Instagram. Scrolls. Likes post. Comments. Puts phone down. Watches TV. Picks up controller again. Plays game. Laughs. Puts controller down."
    },
    {
      "time": "21:30-22:15",
      "location": "Bedroom 3",
      "activity": "Planning the coming week on her computer: support shift roster, bills, maintenance tasks and a structured group activity she leads",
      "desc": "Walks to bedroom. Sits at desk. Opens laptop. Opens calendar. Checks roster. Opens bills. Notes due dates. Opens notes app. Types tasks. Saves notes. Closes laptop."
    },
    {
      "time": "22:15-22:45",
      "location": "Bedroom 3",
      "activity": "Light reading and Messenger chats to settle a busy mind while waiting for the bathroom to free up",
      "desc": "Picks up book. Reads. Picks up phone. Opens Messenger. Chats with friend. Puts phone down. Reads. Picks up phone again. Chats. Puts phone down. Closes book."
    },
    {
      "time": "22:45-23:15",
      "location": "Bathroom",
      "activity": "Evening hygiene routine: brushing teeth and washing up before bed (bathroom free after Member 4's 22:15-22:45 slot)",
      "desc": "Walks to bathroom. Turns on light. Picks up toothbrush. Applies toothpaste. Brushes teeth. Rinses mouth. Spits. Washes face. Dries face. Turns off light. Walks out."
    },
    {
      "time": "23:15-23:45",
      "location": "Bedroom 3",
      "activity": "Winding down in bed with light reading and Messenger chats",
      "desc": "Walks to bedroom. Lies in bed. Picks up book. Reads. Picks up phone. Opens Messenger. Chats. Puts phone down. Reads. Puts book down."
    },
    {
      "time": "23:45-24:00",
      "location": "Bedroom 3",
      "activity": "Lights out and going to sleep",
      "desc": "Puts down book. Puts down phone. Turns off lamp. Lies down. Closes eyes. Pulls blanket up. Remains still."
    }
  ]
}
```

