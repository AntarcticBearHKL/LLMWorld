# s3_enrich  (attempt 1)

## 对话信息

- time: 2026-09-13 01:23:27
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
- Age: 38
- Occupation: Community healthcare worker / primary education aide (hybrid shift)
- Personality: consensus-driven, calm and sociable in public, emotionally anchored to family, faith-oriented, community-minded, detail-hungry in conversation, prefers one-on-one text conversations

This member's timeline:
[
  {
    "time": "00:00-05:30",
    "location": "Bedroom 1",
    "activity": "Sleeping through the night."
  },
  {
    "time": "05:30-05:50",
    "location": "Bathroom",
    "activity": "Showering, brushing teeth, and taking morning chronic-condition medication with water."
  },
  {
    "time": "05:50-06:20",
    "location": "Bedroom 1",
    "activity": "Getting dressed, checking phone messages, and reviewing the day's appointment and community visit list."
  },
  {
    "time": "06:20-06:50",
    "location": "Kitchen",
    "activity": "Boiling the kettle, making toast, eating breakfast, and feeding the dog."
  },
  {
    "time": "06:50-07:05",
    "location": "Out",
    "activity": "Walking the dog around the block."
  },
  {
    "time": "07:05-07:15",
    "location": "Kitchen",
    "activity": "Rinsing breakfast dishes, packing a lunch and school bag."
  },
  {
    "time": "07:15-07:50",
    "location": "Out",
    "activity": "School run and drop-off using public transit."
  },
  {
    "time": "07:50-08:40",
    "location": "Out",
    "activity": "Public transit commute to the clinic."
  },
  {
    "time": "08:40-12:00",
    "location": "Out",
    "activity": "On-site clinic shift: patient intake, vital signs checks, and medication reviews at the community health desk."
  },
  {
    "time": "12:00-12:30",
    "location": "Out",
    "activity": "Lunch break outdoors eating a packed lunch on a park bench."
  },
  {
    "time": "12:30-15:00",
    "location": "Out",
    "activity": "Primary school aide duties: classroom support, reading groups, and supervising the children."
  },
  {
    "time": "15:00-16:00",
    "location": "Out",
    "activity": "Community health visits and follow-up check-ins with neighbours and clients."
  },
  {
    "time": "16:00-16:30",
    "location": "Out",
    "activity": "Buying milk and bread with cash at a local shop."
  },
  {
    "time": "16:30-17:15",
    "location": "Out",
    "activity": "Public transit commute home."
  },
  {
    "time": "17:15-17:45",
    "location": "Kitchen",
    "activity": "Unpacking groceries, starting dinner preparation, and refilling the dog's water bowl."
  },
  {
    "time": "17:45-18:00",
    "location": "Dining Room",
    "activity": "Setting the table for the evening meal."
  },
  {
    "time": "18:00-19:00",
    "location": "Dining Room",
    "activity": "Eating dinner."
  },
  {
    "time": "19:00-19:30",
    "location": "Kitchen",
    "activity": "Clearing the table, loading the dishwasher, and wiping down the counters."
  },
  {
    "time": "19:30-20:15",
    "location": "Out",
    "activity": "Evening dog walk around the neighbourhood."
  },
  {
    "time": "20:15-21:30",
    "location": "Study",
    "activity": "Remote paperwork and community outreach scheduling, sending one-on-one text messages on the phone."
  },
  {
    "time": "21:30-22:00",
    "location": "Bathroom",
    "activity": "Evening wash, taking night medication, and hanging the towel to dry with the dehumidifier running."
  },
  {
    "time": "22:00-22:30",
    "location": "Bedroom 1",
    "activity": "Winding down under the desk lamp: reading, texting relatives and neighbours, and checking tomorrow's shift roster."
  },
  {
    "time": "22:30-24:00",
    "location": "Bedroom 1",
    "activity": "Sleeping."
  }
]

Other household members' timelines:
{}

Household structure:
{
  "Bedroom 1": {
    "appliances": [
      "Light",
      "AirConditioner",
      "TV",
      "DeskLamp"
    ]
  },
  "Bedroom 2": {
    "appliances": [
      "Light",
      "Fan"
    ]
  },
  "Bedroom 3": {
    "appliances": [
      "Light",
      "Fan"
    ]
  },
  "Kitchen": {
    "appliances": [
      "Light",
      "Refrigerator",
      "RiceCooker",
      "Microwave",
      "InductionCooker",
      "RangeHood",
      "Kettle",
      "Toaster",
      "Oven",
      "Dishwasher",
      "Freezer"
    ]
  },
  "Bathroom": {
    "appliances": [
      "Light",
      "WaterHeater",
      "Fan",
      "Dehumidifier"
    ]
  },
  "Living Room": {
    "appliances": [
      "Light",
      "TV",
      "AirConditioner",
      "Router",
      "GameConsole",
      "Phone"
    ]
  },
  "Dining Room": {
    "appliances": [
      "Light",
      "AirConditioner"
    ]
  },
  "Study": {
    "appliances": [
      "Light",
      "Computer",
      "Monitor",
      "DeskLamp"
    ]
  },
  "Laundry": {
    "appliances": [
      "Light",
      "WashingMachine",
      "ClothesDryer",
      "VacuumCleaner"
    ]
  },
  "Garage": {
    "appliances": [
      "Light"
    ]
  },
  "Member 1 personal appliances": {
    "appliances": [
      "Phone",
      "Computer"
    ]
  },
  "Member 2 personal appliances": {
    "appliances": [
      "DeskLamp",
      "Computer",
      "Monitor",
      "Phone",
      "ElectricVehicle"
    ]
  },
  "Member 3 personal appliances": {
    "appliances": [
      "DeskLamp",
      "Computer",
      "Phone"
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
      "time": "00:00-05:30",
      "location": "Bedroom 1",
      "activity": "Sleeping through the night.",
      "desc": "Lies down on the bed in Bedroom 1. Pulls the blanket up to the chest. Closes eyes. Turns onto the right side. Remains still, breathing slowly. Turns onto the left side. Pulls the blanket higher over the shoulder. Remains motionless. Rolls onto the back. Reaches up and adjusts the pillow under the head. Drops the arm back down. Remains still. Turns onto the right side again. Remains motionless under the blanket until 05:30."
    },
    {
      "time": "05:30-05:50",
      "location": "Bathroom",
      "activity": "Showering, brushing teeth, and taking morning chronic-condition medication with water.",
      "desc": "Sits up on the bed. Swings legs to the floor. Stands up. Walks to the bathroom door. Pushes the door open. Reaches for the light switch and turns the light on. Turns the water heater switch on. Pulls off nightwear. Steps into the shower. Turns the shower tap. Stands under the water. Picks up soap and washes the body. Rinses off. Turns the tap off. Steps out. Picks up the towel and dries the body and hair. Wraps the towel around. Picks up the toothbrush. Squeezes toothpaste onto the brush. Brushes teeth. Rinses mouth with water from the cup. Spits into the sink. Opens the medicine cabinet. Takes out the morning chronic-condition medication bottle. Twists the cap open. Tips one tablet into the palm. Puts the tablet in the mouth. Fills the cup with water. Drinks the water and swallows the tablet. Closes the bottle cap. Puts the bottle back in the cabinet. Closes the cabinet door. Turns the light off. Walks out of the bathroom."
    },
    {
      "time": "05:50-06:20",
      "location": "Bedroom 1",
      "activity": "Getting dressed, checking phone messages, and reviewing the day's appointment and community visit list.",
      "desc": "Walks into Bedroom 1. Opens the wardrobe door. Takes out a shirt and trousers. Lays them on the bed. Takes underwear and socks from the drawer. Pulls on the underwear. Pulls on the socks. Puts on the trousers. Buttons the shirt. Closes the wardrobe door. Picks up the phone from the bedside table. Unlocks the screen with the thumb. Opens the message app. Scrolls through message list. Taps and opens three unread messages. Types short replies with both thumbs. Presses send. Locks the phone. Puts the phone in the trouser pocket. Picks up the paper appointment list from the desk. Reads the list down with the index finger. Folds the list. Puts the list into the bag. Zips the bag. Picks up the bag. Walks out of Bedroom 1."
    },
    {
      "time": "06:20-06:50",
      "location": "Kitchen",
      "activity": "Boiling the kettle, making toast, eating breakfast, and feeding the dog.",
      "desc": "Walks into the Kitchen. Puts the bag down on the chair. Turns the kitchen light on. Fills the kettle with water at the tap. Puts the kettle on the base. Presses the kettle switch down. Opens the cupboard door. Takes out the bread bag. Takes two slices out. Puts the slices into the toaster. Presses the toaster lever down. Opens the refrigerator door. Takes out the butter and the milk. Closes the refrigerator door. Puts the butter on the counter. Opens the dog food bin. Scoops dog food into the bowl. Puts the bowl on the floor. Says \"Here you go.\" The kettle clicks off. Pours hot water into the mug. Drops a tea bag into the mug. The toaster pops up. Takes the toast out. Spreads butter on the toast with a knife. Sits down at the kitchen table. Eats the toast and drinks the tea. Stands up. Puts the mug and plate in the sink."
    },
    {
      "time": "06:50-07:05",
      "location": "Out",
      "activity": "Walking the dog around the block.",
      "desc": "Walks to the hallway. Picks up the dog leash from the hook. Clips the leash onto the dog collar. Opens the front door. Steps outside. Closes the door behind. Walks down the front steps. Turns right at the corner. Walks along the pavement. Calls the dog forward. Waits at the crossing. Crosses the street. Turns left. Walks around the block. Pauses while the dog sniffs the grass. Pulls the leash gently. Continues walking. Turns back onto the home street. Walks up the front steps. Opens the front door. Steps inside. Unclips the leash. Hangs the leash on the hook. Closes the door."
    },
    {
      "time": "07:05-07:15",
      "location": "Kitchen",
      "activity": "Rinsing breakfast dishes, packing a lunch and school bag.",
      "desc": "Walks into the Kitchen. Turns the tap on. Rinses the plate and the mug under the water. Puts them on the drying rack. Turns the tap off. Opens the refrigerator door. Takes out the sandwich box and an apple. Closes the refrigerator door. Puts the sandwich box and the apple into the lunch bag. Zips the lunch bag. Picks up the water bottle from the counter. Puts the water bottle into the side pocket of the school bag. Zips the school bag. Lifts the school bag onto the shoulder. Picks up the lunch bag. Walks out of the Kitchen."
    },
    {
      "time": "07:15-07:50",
      "location": "Out",
      "activity": "School run and drop-off using public transit.",
      "desc": "Walks out the front door with the school bag and the lunch bag. Closes the door. Walks to the bus stop. Stands at the stop and checks the phone for the bus time. Steps onto the bus. Taps the transit card on the reader. Walks down the aisle. Sits next to the child. Says to the child, \"Did you put your homework folder in your bag?\" Nods at the answer. Stands up at the stop. Presses the stop button. Steps off the bus. Walks to the school gate. Hands the lunch bag to the child. Says, \"Have a good day, see you later.\" Watches the child walk through the gate. Waves. Turns around. Walks back to the bus stop."
    },
    {
      "time": "07:50-08:40",
      "location": "Out",
      "activity": "Public transit commute to the clinic.",
      "desc": "Stands at the bus stop. Steps onto the bus. Taps the transit card. Walks to the rear. Holds the overhead rail. Looks at the phone screen. Reads a message. Types a reply with the thumb. Presses send. Steps off at the transfer stop. Walks to the train platform. Stands at the yellow line. Steps onto the train. Taps the card. Sits in an empty seat. Puts the bag on the lap. Opens the appointment list and reads it. Folds the list. Stands up at the station. Steps off the train. Walks up the stairs. Exits the station. Walks two blocks to the clinic. Pushes the clinic door open."
    },
    {
      "time": "08:40-12:00",
      "location": "Out",
      "activity": "On-site clinic shift: patient intake, vital signs checks, and medication reviews at the community health desk.",
      "desc": "Walks to the community health desk. Puts the bag down. Turns the desk computer on. Logs in with the password. Opens the patient intake form on the screen. Calls the first patient in. Says \"Good morning, please take a seat.\" Picks up the blood pressure cuff. Wraps the cuff around the patient's arm. Presses the start button. Reads the numbers on the display. Writes the readings into the form. Picks up the thermometer. Places it near the patient's forehead. Presses the button. Reads the temperature. Records it. Picks up the pulse oximeter. Clips it onto the patient's finger. Reads the oxygen level. Records it. Picks up the medication box. Opens the lid. Counts the tablets. Compares with the prescription sheet. Tells the patient \"Two in the morning, one at night.\" Types notes into the computer. Saves the record. Calls the next patient. Repeats the intake and vital signs checks for five more patients. Picks up the phone and sends a one-on-one text to a client about a follow-up visit."
    },
    {
      "time": "12:00-12:30",
      "location": "Out",
      "activity": "Lunch break outdoors eating a packed lunch on a park bench.",
      "desc": "Picks up the lunch bag. Walks out of the clinic. Crosses the street to the park. Walks along the path. Stops at an empty bench. Sits down on the bench. Unzips the lunch bag. Takes out the sandwich box. Opens the lid. Takes out the sandwich. Eats the sandwich. Opens the water bottle. Drinks water. Closes the bottle. Takes out the apple. Bites the apple. Eats the apple. Puts the core into the bag. Wipes the hands with a tissue. Puts the tissue into the bag. Zips the lunch bag. Stands up. Walks back along the path. Crosses the street. Walks into the clinic."
    },
    {
      "time": "12:30-15:00",
      "location": "Out",
      "activity": "Primary school aide duties: classroom support, reading groups, and supervising the children.",
      "desc": "Walks into the classroom. Puts the bag on a chair. Greets the teacher and says \"Good afternoon.\" Takes the reading group list from the desk. Calls four children to the reading table. Sits down at the table. Opens the reading book. Points at the first line. Listens to a child read. Corrects a word. Turns the page. Listens to the next child read. Nods. Closes the book. Stands up. Hands out worksheets to each desk. Walks between the rows. Bends down to help a child hold the pencil. Straightens up. Answers a child's question. Walks to the corridor door. Opens the door and stands at the doorway during the class change. Counts the children coming in. Closes the door. Collects the worksheets from the desks. Stacks them on the desk. Picks up the bag."
    },
    {
      "time": "15:00-16:00",
      "location": "Out",
      "activity": "Community health visits and follow-up check-ins with neighbours and clients.",
      "desc": "Walks out of the school. Takes the visit list from the bag. Reads the first address. Walks to the first house. Knocks on the door. Says \"Hello, it's Member 1, community health visit.\" Steps inside. Asks the client about the medication. Writes the answer on the list. Picks up the pill organizer from the table. Opens the compartments. Checks the tablets. Closes the compartments. Hands the organizer back. Says \"Same time tomorrow.\" Walks to the door. Says \"Take care.\" Walks to the second house. Knocks on the door. Asks the neighbour about the blood pressure readings. Writes the numbers on the list. Checks the dressing on the neighbour's arm. Says \"Keep it dry.\" Walks out. Walks to the third house. Knocks. Leaves a note at the door. Walks back toward the main street. Checks the phone for the time."
    },
    {
      "time": "16:00-16:30",
      "location": "Out",
      "activity": "Buying milk and bread with cash at a local shop.",
      "desc": "Walks to the shop door. Pushes the door open. Walks to the dairy aisle. Picks up a carton of milk. Reads the date on the carton. Puts the carton into the basket. Walks to the bakery shelf. Picks up a loaf of bread. Squeezes the loaf. Puts the loaf into the basket. Walks to the till. Puts the basket on the counter. Says to the shopkeeper \"Just these, thanks.\" Opens the purse. Takes out the cash notes. Hands the notes to the shopkeeper. Takes the change. Puts the change into the purse. Closes the purse. Puts the milk and bread into the bag. Says \"Thank you, see you.\" Picks up the bag. Walks out of the shop."
    },
    {
      "time": "16:30-17:15",
      "location": "Out",
      "activity": "Public transit commute home.",
      "desc": "Walks to the bus stop. Stands at the stop with the bag on the shoulder. Steps onto the bus. Taps the transit card. Walks down the aisle. Sits in an empty seat. Puts the bag on the lap. Takes the phone out. Opens the message app. Reads a message from a relative. Types a reply with the thumb. Presses send. Puts the phone back into the pocket. Looks out of the window. Stands up at the stop. Presses the stop button. Steps off the bus. Walks to the train platform. Steps onto the train. Taps the card. Holds the overhead rail. Steps off at the home station. Walks up the stairs. Exits the station. Walks four blocks. Walks up the front steps. Opens the front door. Steps inside."
    },
    {
      "time": "17:15-17:45",
      "location": "Kitchen",
      "activity": "Unpacking groceries, starting dinner preparation, and refilling the dog's water bowl.",
      "desc": "Walks into the Kitchen. Puts the bag on the counter. Turns the kitchen light on. Takes the milk carton out of the bag. Opens the refrigerator door. Puts the milk on the shelf. Closes the door. Takes the bread loaf out of the bag. Puts it in the bread bin. Folds the empty bag. Puts the bag in the bin. Picks up the dog water bowl from the floor. Turns the tap on. Fills the bowl with water. Turns the tap off. Puts the bowl back on the floor. Opens the cupboard door. Takes out the rice cooker inner pot. Scoops rice into the pot. Rinses the rice under the tap. Pours the water out. Puts the pot into the rice cooker. Puts the rice cooker on the counter. Presses the cook button down. Opens the refrigerator door. Takes out vegetables. Closes the door. Puts the vegetables on the cutting board. Picks up the knife. Cuts the vegetables. Puts the pieces into a bowl."
    },
    {
      "time": "17:45-18:00",
      "location": "Dining Room",
      "activity": "Setting the table for the evening meal.",
      "desc": "Walks into the Dining Room. Turns the dining room light on. Opens the sideboard drawer. Takes out four plates. Carries the plates to the table. Puts one plate at each seat. Walks back to the drawer. Takes out four sets of cutlery. Carries them to the table. Puts a fork and a knife beside each plate. Walks to the kitchen. Picks up four glasses from the shelf. Carries the glasses to the dining table. Puts one glass beside each plate. Walks to the kitchen. Fills a water jug at the tap. Carries the jug back. Puts the jug in the centre of the table. Stands back from the table. Adjusts one plate. Walks back to the Kitchen."
    },
    {
      "time": "18:00-19:00",
      "location": "Dining Room",
      "activity": "Eating dinner.",
      "desc": "Walks into the Dining Room carrying the rice bowl and the vegetable dish. Puts the dishes on the table. Pulls out a chair. Sits down. Says to the household \"Dinner's ready, come and sit.\" Picks up the serving spoon. Spoons rice onto the plate. Passes the bowl to the next person. Picks up the fork. Eats the rice and vegetables. Picks up the glass. Drinks water. Puts the glass down. Talks with the family about the day's visits and the school class. Listens to a reply. Nods. Picks up the fork again. Continues eating. Puts the fork down on the plate. Picks up the glass. Finishes the water. Puts the glass down. Pushes the chair back. Stands up. Picks up the plate and the glass."
    },
    {
      "time": "19:00-19:30",
      "location": "Kitchen",
      "activity": "Clearing the table, loading the dishwasher, and wiping down the counters.",
      "desc": "Walks into the Kitchen with the plate and glass. Puts them on the counter. Walks back to the Dining Room. Picks up the remaining plates and cutlery. Carries them to the Kitchen. Picks up the serving dishes. Carries them to the Kitchen. Opens the dishwasher door. Pulls out the lower rack. Loads the plates into the rack. Loads the glasses into the upper rack. Loads the cutlery into the basket. Pushes the rack in. Closes the dishwasher door. Presses the start button. Picks up the dishcloth. Turns the tap on. Wets the cloth. Turns the tap off. Wipes the counter surface. Rinses the cloth. Wrings the cloth out. Hangs the cloth on the rail. Picks up the broom. Sweeps the floor. Puts the broom back in the corner. Turns the kitchen light off. Walks out of the Kitchen."
    },
    {
      "time": "19:30-20:15",
      "location": "Out",
      "activity": "Evening dog walk around the neighbourhood.",
      "desc": "Walks to the hallway. Picks up the dog leash from the hook. Clips the leash onto the dog collar. Opens the front door. Steps outside. Closes the door. Walks down the front steps. Turns left onto the pavement. Walks past the neighbour's gate. Waves to a neighbour and says \"Good evening.\" Continues walking. Stops at the corner. Crosses the street. Walks along the park fence. Pauses while the dog sniffs the lamp post. Pulls the leash gently. Walks on. Turns at the second corner. Walks back along the home street. Stops to speak with a neighbour about tomorrow's visit. Says \"I'll come by after three.\" Walks up the front steps. Opens the front door. Steps inside. Unclips the leash. Hangs the leash on the hook. Closes the door."
    },
    {
      "time": "20:15-21:30",
      "location": "Study",
      "activity": "Remote paperwork and community outreach scheduling, sending one-on-one text messages on the phone.",
      "desc": "Walks into the Study. Turns the study light on. Pulls out the chair. Sits down at the desk. Presses the computer power button. Waits for the screen to load. Types the password on the keyboard. Opens the paperwork folder on the desk. Picks up the pen. Writes visit notes on the forms. Turns the page. Signs the bottom of the form. Closes the folder. Picks up the phone from the desk. Unlocks the screen. Opens the message app. Taps a client's name. Types a text about the follow-up appointment. Presses send. Taps the next name. Types a text with the appointment time. Presses send. Scrolls the contact list. Sends four more one-on-one texts. Puts the phone down. Opens the outreach schedule on the screen. Types the visit times into the calendar. Saves the calendar. Closes the program. Shuts the computer down. Picks up the paperwork folder. Puts it in the drawer. Closes the drawer. Turns the study light off. Walks out of the Study."
    },
    {
      "time": "21:30-22:00",
      "location": "Bathroom",
      "activity": "Evening wash, taking night medication, and hanging the towel to dry with the dehumidifier running.",
      "desc": "Walks into the Bathroom. Turns the bathroom light on. Turns the dehumidifier on. Presses the dehumidifier start button. Turns the tap on. Washes the face with water. Washes the hands with soap. Rinses the hands. Turns the tap off. Picks up the face towel. Dries the face and hands. Opens the medicine cabinet. Takes out the night medication bottle. Twists the cap open. Tips one tablet into the palm. Puts the tablet in the mouth. Fills the cup with water. Drinks the water and swallows the tablet. Closes the bottle cap. Puts the bottle back in the cabinet. Closes the cabinet door. Shakes out the towel. Hangs the towel on the drying rack. Turns the bathroom light off. Leaves the dehumidifier running. Walks out of the Bathroom."
    },
    {
      "time": "22:00-22:30",
      "location": "Bedroom 1",
      "activity": "Winding down under the desk lamp: reading, texting relatives and neighbours, and checking tomorrow's shift roster.",
      "desc": "Walks into Bedroom 1. Turns the bedroom light on. Reaches to the desk and turns the desk lamp on. Turns the bedroom ceiling light off. Picks up the book from the bedside table. Sits down on the bed. Opens the book. Reads two pages. Closes the book. Puts the book back on the bedside table. Picks up the phone. Unlocks the screen. Opens the message app. Taps a relative's name. Types a goodnight text. Presses send. Taps a neighbour's name. Types a text about tomorrow's visit. Presses send. Opens the shift roster file on the phone. Scrolls through tomorrow's roster. Reads the start time. Closes the file. Locks the phone. Puts the phone on the bedside table. Reaches to the desk lamp. Turns the desk lamp off. Pulls back the blanket. Lies down on the bed."
    },
    {
      "time": "22:30-24:00",
      "location": "Bedroom 1",
      "activity": "Sleeping.",
      "desc": "Lies down on the bed in Bedroom 1. Pulls the blanket up to the chest. Closes eyes. Turns onto the right side. Remains still. Turns onto the back. Adjusts the pillow under the head. Drops the arm down. Turns onto the left side. Pulls the blanket over the shoulder. Remains motionless, breathing slowly. Rolls onto the right side again. Remains still under the blanket until 24:00."
    }
  ]
}
```

