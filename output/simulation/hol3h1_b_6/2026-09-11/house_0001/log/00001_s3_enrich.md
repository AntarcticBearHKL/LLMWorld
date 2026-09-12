# s3_enrich  (attempt 1)

## 对话信息

- time: 2026-09-13 04:26:42
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
- Occupation: Master of Social Work student at Monash University; part-time aged-care support worker
- Personality: communal, organised, consensus-seeking, loyal, cautious about risk and money, late adopter of technology, detail-oriented

This member's timeline:
[
  {
    "time": "00:00-06:30",
    "location": "Out",
    "activity": "Working a night shift as an aged-care support worker, doing overnight checks and assisting residents with personal care"
  },
  {
    "time": "06:30-07:40",
    "location": "Out",
    "activity": "Commuting home from the night shift by train and bus"
  },
  {
    "time": "07:40-08:10",
    "location": "Bathroom",
    "activity": "Showering and changing out of work clothes after the night shift, keeping quiet"
  },
  {
    "time": "08:10-08:30",
    "location": "Kitchen",
    "activity": "Making tea and a light breakfast before sleeping, cleaning up as he goes"
  },
  {
    "time": "08:30-14:00",
    "location": "Bedroom 1",
    "activity": "Sleeping after the night shift with the fan on and the light off for quiet rest"
  },
  {
    "time": "14:00-14:20",
    "location": "Bathroom",
    "activity": "Washing his face and freshening up after waking, and starting one load of laundry in the washing machine"
  },
  {
    "time": "14:20-15:00",
    "location": "Kitchen",
    "activity": "Eating a flexitarian lunch of rice and vegetables and drinking tea"
  },
  {
    "time": "15:00-15:20",
    "location": "Kitchen",
    "activity": "Washing the dishes and wiping down the shared bench"
  },
  {
    "time": "15:20-16:30",
    "location": "Bedroom 1",
    "activity": "Studying social work course readings at the desk with the desk lamp on and the computer"
  },
  {
    "time": "16:30-17:00",
    "location": "Kitchen",
    "activity": "Tea break while reading detailed written messages on his phone"
  },
  {
    "time": "17:00-18:00",
    "location": "Bedroom 1",
    "activity": "Drafting a social work assignment on the monitor at his desk"
  },
  {
    "time": "18:00-18:30",
    "location": "Kitchen",
    "activity": "Cooking a simple flexitarian dinner using the induction cooker and rice cooker"
  },
  {
    "time": "18:30-19:10",
    "location": "Kitchen",
    "activity": "Eating dinner and drinking tea"
  },
  {
    "time": "19:10-19:40",
    "location": "Bathroom",
    "activity": "Moving the laundry from the washing machine to the clothes dryer and tidying the bathroom"
  },
  {
    "time": "19:40-20:30",
    "location": "Bedroom 1",
    "activity": "Writing notes and reminders for the next house meeting and drafting text messages to housemates"
  },
  {
    "time": "20:30-21:15",
    "location": "Bedroom 1",
    "activity": "Reviewing his weekly budget with cash envelopes and checking rent and bill due dates"
  },
  {
    "time": "21:15-22:00",
    "location": "Bedroom 1",
    "activity": "Quiet leisure: looking at the photo of his family dog and reading"
  },
  {
    "time": "22:00-22:20",
    "location": "Bathroom",
    "activity": "Night routine of brushing teeth and washing his face"
  },
  {
    "time": "22:20-22:40",
    "location": "Bedroom 1",
    "activity": "Setting alarms and reminders for tomorrow's shift and study tasks"
  },
  {
    "time": "22:40-24:00",
    "location": "Bedroom 1",
    "activity": "Sleeping with the fan on and the light off"
  }
]

Other household members' timelines:
{}

Household structure:
{
  "Bedroom 1": {
    "appliances": [
      "Light",
      "Fan"
    ]
  },
  "Bedroom 2": {
    "appliances": [
      "Light",
      "SpaceHeater"
    ]
  },
  "Bedroom 3": {
    "appliances": [
      "Light",
      "Fan"
    ]
  },
  "Bedroom 4": {
    "appliances": [
      "Light"
    ]
  },
  "Bedroom 5": {
    "appliances": [
      "Light",
      "SpaceHeater"
    ]
  },
  "Bedroom 6": {
    "appliances": [
      "Light",
      "Fan"
    ]
  },
  "Kitchen": {
    "appliances": [
      "Light",
      "Refrigerator",
      "Freezer",
      "RiceCooker",
      "Microwave",
      "InductionCooker",
      "RangeHood",
      "Oven",
      "Kettle",
      "Toaster",
      "Dishwasher",
      "Router"
    ]
  },
  "Bathroom": {
    "appliances": [
      "Light",
      "WaterHeater",
      "WashingMachine",
      "ClothesDryer",
      "Dehumidifier"
    ]
  },
  "Member 1 personal appliances": {
    "appliances": [
      "DeskLamp",
      "Computer",
      "Monitor",
      "Phone"
    ]
  },
  "Member 2 personal appliances": {
    "appliances": [
      "DeskLamp",
      "Computer",
      "Phone",
      "Kettle",
      "ElectricVehicle"
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
      "DeskLamp",
      "Computer",
      "Monitor",
      "Phone"
    ]
  },
  "Member 5 personal appliances": {
    "appliances": [
      "DeskLamp",
      "Computer",
      "Phone"
    ]
  },
  "Member 6 personal appliances": {
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
      "time": "00:00-06:30",
      "location": "Out",
      "activity": "Working a night shift as an aged-care support worker, doing overnight checks and assisting residents with personal care",
      "desc": "Clock in at the staff room and sign the shift register. Attend handover with the outgoing worker and write notes in the care log. Pick up the torch and walk down the corridor. Push open the first resident's door. Shine the torch on the bed. Lean over and check the resident is breathing. Pull the blanket up over the resident's shoulders. Step back and close the door quietly. Walk to the second room. Open the door, turn on the dim night light, and check the resident's position. Bend down, slide hands under the resident, and roll the resident onto their side. Place a pillow behind the resident's back. Turn off the night light and close the door. Walk to the nurse station and write the check time in the log. Put on gloves. Assist a resident to the toilet, hold the resident's arm, and steady them back to bed. Remove gloves and wash hands at the sink. Change wet bed linen, pull the sheet tight, and place the soiled linen in the laundry bag. Help a resident drink water from a cup. Record fluid intake on the chart. Walk the corridor again and repeat the round at two-hourly intervals. Write the end-of-shift report and hand over to the morning worker. Clock out at the staff room."
    },
    {
      "time": "06:30-07:40",
      "location": "Out",
      "activity": "Commuting home from the night shift by train and bus",
      "desc": "Walk out of the facility to the bus stop. Stand at the kerb. Board the bus and tap the myki card on the reader. Sit down on the seat. Hold the bag on the lap. Stand up at the stop and pull the cord. Step off the bus. Walk to the train station entrance. Tap the myki card on the gate. Walk up the platform ramp. Stand behind the yellow line. Step onto the train when the doors open. Sit down by the window. Put the bag on the lap. Take the phone out of the pocket and check the time. Put the phone back in the pocket. Stand up as the train approaches the station. Step off the train. Tap the card on the gate. Walk out of the station. Walk along the footpath to the house. Open the front gate. Walk up the path. Unlock the front door with the key. Step inside. Close and lock the door behind."
    },
    {
      "time": "07:40-08:10",
      "location": "Bathroom",
      "activity": "Showering and changing out of work clothes after the night shift, keeping quiet",
      "desc": "Walk into the bathroom. Close the door. Turn on the light. Unbutton the work shirt and take it off. Pull off the trousers. Place the work clothes in the laundry basket. Turn on the shower tap. Hold a hand under the water to test the temperature. Adjust the tap with the other hand. Step into the shower. Wet the hair under the water. Pick up the shampoo bottle and open the lid. Squeeze shampoo into the palm. Rub the shampoo into the hair. Rinse the hair under the water. Pick up the body wash and squeeze it onto the hand. Rub the body wash over the arms, chest and legs. Rinse off under the water. Turn off the tap. Step out of the shower. Pick up the towel from the hook. Dry the hair with the towel. Dry the body. Wrap the towel around the waist. Open the cupboard and take out clean clothes. Put on the clean shirt. Pull on the trousers. Hang the towel back on the hook. Turn off the light. Open the door quietly. Walk out of the bathroom."
    },
    {
      "time": "08:10-08:30",
      "location": "Kitchen",
      "activity": "Making tea and a light breakfast before sleeping, cleaning up as he goes",
      "desc": "Walk into the kitchen. Turn on the kitchen light. Pick up the kettle and fill it with water at the tap. Place the kettle on the base and press the switch down. Open the cupboard and take out a mug. Place the mug on the bench. Open the drawer and take out a tea bag. Drop the tea bag into the mug. Open the fridge and take out the milk. Close the fridge. Pour hot water from the kettle into the mug. Pour a splash of milk into the mug. Put the milk back in the fridge. Open the cupboard and take out a box of cereal. Pour cereal into a bowl. Open the fridge and take out the milk again, pour milk over the cereal, and return the milk. Sit down at the table. Pick up the spoon. Eat the cereal. Drink the tea. Stand up and carry the bowl and mug to the sink. Rinse the bowl and mug under the tap. Place them in the drying rack. Wipe the bench with a cloth. Turn off the kitchen light. Walk out of the kitchen."
    },
    {
      "time": "08:30-14:00",
      "location": "Bedroom 1",
      "activity": "Sleeping after the night shift with the fan on and the light off for quiet rest",
      "desc": "Walk into Bedroom 1. Close the bedroom door. Turn off the ceiling light. Press the button on the fan to switch it on. Press the speed button to set the fan to low. Pull the curtain across the window. Walk to the bed. Pull back the blanket. Lie down on the bed on the back. Pull the blanket up over the chest. Turn onto the left side. Adjust the pillow under the head. Move the arm under the pillow. Remain lying on the bed with eyes closed. Turn over onto the right side. Pull the blanket up again. Push the pillow flatter with the hand. Remain lying still. Turn onto the back. Rest the arm across the forehead. Remain lying. Turn onto the left side again. Pull the blanket to the shoulder. Remain lying. Shift the legs under the sheet. Remain lying still until the alarm sounds."
    },
    {
      "time": "14:00-14:20",
      "location": "Bathroom",
      "activity": "Washing his face and freshening up after waking, and starting one load of laundry in the washing machine",
      "desc": "Sit up on the bed. Stand up and walk to the bathroom. Turn on the light. Turn on the tap. Cup both hands under the water. Splash water on the face. Repeat twice. Turn off the tap. Pick up the towel from the hook. Wipe the face dry. Hang the towel back. Pick up the laundry basket from the floor. Open the washing machine lid. Take the clothes out of the basket and drop them into the drum. Close the lid. Open the detergent drawer and pour in detergent. Close the drawer. Press the power button. Press the cycle button to select a normal wash. Press the start button. Turn off the light. Walk out of the bathroom."
    },
    {
      "time": "14:20-15:00",
      "location": "Kitchen",
      "activity": "Eating a flexitarian lunch of rice and vegetables and drinking tea",
      "desc": "Walk into the kitchen. Turn on the light. Open the fridge and take out the container of cooked rice. Take out the container of vegetables. Close the fridge door. Place both containers on the bench. Open the cupboard and take out a bowl and a plate. Spoon the rice from the container into the bowl. Tip the vegetables onto the plate. Open the microwave door and place the bowl and plate inside. Close the door. Press the buttons to set one minute. Press start. Wait in front of the microwave. Open the door when the timer beeps. Take out the bowl and the plate. Place them on the table. Pick up the kettle and fill it with water. Place it on the base and press the switch. Open the cupboard and take out a mug. Drop a tea bag into the mug. Pour hot water into the mug. Sit down at the table. Pick up the fork and eat the rice and vegetables. Pick up the mug and drink the tea. Stand up and carry the bowl, plate and mug to the sink."
    },
    {
      "time": "15:00-15:20",
      "location": "Kitchen",
      "activity": "Washing the dishes and wiping down the shared bench",
      "desc": "Turn on the tap. Pick up the sponge from the sink caddy. Press soap onto the sponge. Scrub the bowl under the running water. Rinse the bowl and place it in the drying rack. Scrub the plate and place it in the rack. Scrub the mug and place it in the rack. Scrub the fork and place it in the rack. Turn off the tap. Wring out the sponge. Pick up the cloth from the rail. Wipe the bench surface from left to right. Turn the cloth over and wipe the other half of the bench. Wipe around the kettle base. Rinse the cloth under the tap and wring it out. Hang the cloth back on the rail. Walk out of the kitchen."
    },
    {
      "time": "15:20-16:30",
      "location": "Bedroom 1",
      "activity": "Studying social work course readings at the desk with the desk lamp on and the computer",
      "desc": "Walk into Bedroom 1. Pull the chair out from the desk. Sit down on the chair. Press the switch on the desk lamp. Open the course reader on the desk. Turn to the assigned chapter. Pick up the highlighter. Draw a line under the first heading. Turn the page. Read the paragraph. Pick up the pen and write margin notes in the notebook. Turn another page. Highlight two sentences. Put the pen down. Press the power button on the computer. Wait for the screen to load. Move the mouse and click on the browser. Type a search term in the search bar. Press enter. Scroll down the page with the mouse wheel. Read the article on the screen. Click on a link. Scroll again. Write a note in the notebook. Turn to the next reading in the course reader. Highlight another paragraph. Save the reading list in a document with Ctrl+S. Lean back and stretch both arms up."
    },
    {
      "time": "16:30-17:00",
      "location": "Kitchen",
      "activity": "Tea break while reading detailed written messages on his phone",
      "desc": "Stand up from the desk and walk to the kitchen. Turn on the light. Pick up the kettle and fill it at the tap. Place it on the base and press the switch down. Open the cupboard and take out a mug. Place the mug on the bench. Open the drawer and take out a tea bag. Drop the tea bag into the mug. Pour hot water into the mug. Pick up the mug and place it on the table. Pull out the chair and sit down. Take the phone out of the pocket. Press the side button to wake the screen. Unlock the phone with the thumb. Tap the messaging app icon. Scroll through the message thread. Read each message to the bottom. Tap the reply box. Type a reply with both thumbs. Press send. Scroll back up and re-read an earlier message. Pick up the mug and drink the tea. Put the mug down. Tap back to the message list. Open a second conversation. Read the messages. Type a short reply and press send. Lock the phone and place it on the table."
    },
    {
      "time": "17:00-18:00",
      "location": "Bedroom 1",
      "activity": "Drafting a social work assignment on the monitor at his desk",
      "desc": "Stand up from the kitchen table and walk back to Bedroom 1. Pull the chair out and sit down at the desk. Press the power button on the monitor. Tap the keyboard to wake the computer. Open the word processor document. Click into the title field and type the assignment title. Move the mouse to the heading style and click. Type the introduction paragraph on the keyboard. Scroll up with the mouse to check the reference list. Open the browser tab and copy a citation. Paste it into the document. Type the body section. Delete a sentence with the backspace key. Retype the sentence. Press Ctrl+S to save. Check the word count at the bottom of the screen. Open a second browser tab and read a source article. Type two more sentences. Highlight a paragraph and move it up with the mouse. Press Ctrl+S again. Lean forward and read the draft on the monitor from start to finish. Click the save icon once more."
    },
    {
      "time": "18:00-18:30",
      "location": "Kitchen",
      "activity": "Cooking a simple flexitarian dinner using the induction cooker and rice cooker",
      "desc": "Stand up and walk to the kitchen. Turn on the kitchen light. Press the switch on the range hood. Open the fridge and take out the vegetables and tofu. Close the fridge. Place them on the bench. Open the cupboard and take out the cutting board. Place the board on the counter. Pick up the knife and cut the vegetables into pieces. Push the pieces to the side of the board. Open the cupboard and take out a pot. Place the pot on the induction cooker. Press the power button and press the heat setting. Pour oil into the pot. Tip the vegetables into the pot. Pick up the spatula and stir the vegetables. Open the cupboard and take out the rice. Pour rice into the rice cooker inner pot. Rinse the rice under the tap. Add water to the level line. Place the inner pot in the rice cooker. Close the lid. Press the cook button. Pick up the lid of the pot and place it on the bench. Stir the vegetables again. Press the power button off on the induction cooker. Turn off the range hood."
    },
    {
      "time": "18:30-19:10",
      "location": "Kitchen",
      "activity": "Eating dinner and drinking tea",
      "desc": "Open the cupboard and take out a bowl and a plate. Open the rice cooker lid and spoon rice into the bowl. Spoon the vegetables onto the plate. Close the rice cooker lid. Carry the bowl and plate to the table. Place them down. Pull out the chair and sit down. Pick up the chopsticks. Lift the bowl with the left hand. Pick up rice with the chopsticks and eat. Take a piece of vegetable from the plate. Chew and swallow. Put the chopsticks down. Pick up the kettle and pour hot water into the mug. Pick up the mug and drink the tea. Pick up the chopsticks again and continue eating. Finish the rice in the bowl. Drink the rest of the tea. Stand up and carry the bowl, plate, chopsticks and mug to the sink. Place them in the sink."
    },
    {
      "time": "19:10-19:40",
      "location": "Bathroom",
      "activity": "Moving the laundry from the washing machine to the clothes dryer and tidying the bathroom",
      "desc": "Walk to the bathroom. Turn on the light. Open the washing machine lid. Pull the wet clothes out of the drum one item at a time. Drop the items into the laundry basket. Open the clothes dryer door. Take the items out of the basket and place them in the dryer drum. Close the dryer door. Press the power button on the dryer. Press the program button to select the cycle. Press the start button. Close the washing machine lid. Pick up the towel from the floor and hang it on the rail. Pick up the cloth and wipe the sink basin. Wipe the tap with the cloth. Rinse the cloth and wring it out. Hang the cloth on the hook. Straighten the bottles on the shelf. Turn off the light. Walk out of the bathroom."
    },
    {
      "time": "19:40-20:30",
      "location": "Bedroom 1",
      "activity": "Writing notes and reminders for the next house meeting and drafting text messages to housemates",
      "desc": "Walk into Bedroom 1. Pull the chair out and sit at the desk. Press the desk lamp switch on. Open the notebook to a clean page. Pick up the pen. Write the date at the top of the page. Write a heading for the house meeting. Write the first item about the shared kitchen bench. Write the second item about the bin roster. Write the third item about the electricity bill. Number each item. Underline the heading. Put the pen down. Pick up the phone. Unlock it with the thumb. Tap the messaging app. Tap the group chat with the housemates. Tap the message box. Type a message about the house meeting time. Press send. Wait and read the reply. Type a second message listing the agenda items. Press send. Read the replies. Type a short confirmation and press send. Lock the phone and place it on the desk. Pick up the pen and add one more note to the page."
    },
    {
      "time": "20:30-21:15",
      "location": "Bedroom 1",
      "activity": "Reviewing his weekly budget with cash envelopes and checking rent and bill due dates",
      "desc": "Open the desk drawer and take out the cash envelopes. Place the envelopes on the desk. Open the first envelope labelled groceries. Take out the notes and count them one by one. Write the amount on the budget sheet. Put the notes back in the envelope and close it. Open the second envelope labelled transport. Count the notes. Write the amount down. Close the envelope. Open the third envelope labelled bills. Count the notes and write the amount. Place the envelopes back in the drawer. Pick up the phone and unlock it. Open the calculator app. Tap in the amounts and press equals. Write the total on the budget sheet. Open the calendar app and check the rent due date. Tap the rent date and read the reminder. Open the notes app and check the electricity bill due date. Write both dates in the notebook. Lock the phone and put it on the desk. Close the notebook."
    },
    {
      "time": "21:15-22:00",
      "location": "Bedroom 1",
      "activity": "Quiet leisure: looking at the photo of his family dog and reading",
      "desc": "Open the desk drawer and take out the printed photo. Hold the photo in both hands. Look at the photo for a moment. Place the photo back in the drawer and close it. Stand up and walk to the bed. Sit down on the edge of the bed. Reach to the bedside table and pick up the book. Open the book at the bookmark. Turn to the marked page. Read down the page. Turn the page. Continue reading. Shift position and lean back against the pillow. Turn another page. Read two more pages. Place the bookmark on the current page. Close the book. Place the book back on the bedside table. Reach over and press the fan button on. Press the speed button to low."
    },
    {
      "time": "22:00-22:20",
      "location": "Bathroom",
      "activity": "Night routine of brushing teeth and washing his face",
      "desc": "Stand up from the bed and walk to the bathroom. Turn on the light. Pick up the toothbrush from the holder. Turn on the tap and wet the bristles. Turn off the tap. Pick up the toothpaste tube and unscrew the cap. Squeeze toothpaste onto the brush. Screw the cap back on. Brush the teeth up and down. Spit into the sink. Turn on the tap and rinse the mouth. Turn off the tap. Rinse the brush under the water. Tap the brush on the sink edge. Place the brush back in the holder. Turn on the tap and cup water in the hands. Splash water on the face. Turn off the tap. Pick up the towel and wipe the face dry. Hang the towel on the hook. Turn off the light. Walk out of the bathroom."
    },
    {
      "time": "22:20-22:40",
      "location": "Bedroom 1",
      "activity": "Setting alarms and reminders for tomorrow's shift and study tasks",
      "desc": "Walk into Bedroom 1. Sit down on the bed. Pick up the phone from the bedside table. Unlock the phone with the thumb. Tap the clock app icon. Tap the add alarm button. Scroll the hour wheel and set the alarm time. Tap the minute wheel and set the minutes. Tap the save button. Tap the add alarm button again and set a second alarm. Tap save. Press the back button. Tap the notes app icon. Tap the new note button. Type the first study task. Type the second study task. Type the shift start time. Tap save and close the note. Plug the charging cable into the phone. Place the phone on the bedside table. Press the ceiling light switch off."
    },
    {
      "time": "22:40-24:00",
      "location": "Bedroom 1",
      "activity": "Sleeping with the fan on and the light off",
      "desc": "Pull back the blanket. Lie down on the bed on the back. Pull the blanket up over the chest. Turn onto the left side. Adjust the pillow under the head. Move the arm under the pillow. Remain lying with eyes closed. Turn onto the right side. Pull the blanket up to the shoulder. Push the pillow flatter with the hand. Remain lying still. Turn onto the back. Rest one arm across the forehead. Remain lying. Turn onto the left side again. Tuck the blanket under the arm. Remain lying still. Shift the legs under the sheet. Remain lying without moving until the end of the night."
    }
  ]
}
```

