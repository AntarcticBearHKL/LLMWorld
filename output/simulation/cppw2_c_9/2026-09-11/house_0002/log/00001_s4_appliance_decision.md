# s4_appliance_decision  (attempt 1)

## 对话信息

- time: 2026-09-12 19:12:37
- seq: 1
- prefix: Member 1_
- stage: s4_appliance_decision
- attempt: 1
- ok: True

## 输入

```
You are a household electricity behavior expert. Generate the complete appliance usage decisions for Member 1's day.

Member information:
- Name: Member 1
- Age: 29
- Occupation: Community program coordinator at a nonprofit
- Habits: {}

This member's complete timeline:
[
  {
    "time": "00:00-06:30",
    "location": "Bedroom 1",
    "activity": "Sleeping",
    "desc": "Lie down on the bed. Pull the blanket up to the shoulders. Close eyes. Turn body onto the right side. Place one arm under the pillow. Turn onto the left side. Pull the blanket higher. Adjust the pillow. Turn onto the back. Rest both arms beside the body. Turn onto the right side again. Pull the blanket over the shoulder. Keep eyes closed. Remain lying still. Turn onto the left side. Reach out and pull the blanket back up. Remain lying still until the alarm sounds."
  },
  {
    "time": "06:30-07:00",
    "location": "Bathroom",
    "activity": "Waking up, washing face and brushing teeth",
    "desc": "Open eyes. Reach out an arm and press the alarm clock to stop it. Sit up on the edge of the bed. Swing both legs off the bed. Stand up. Walk to the bathroom door. Push the door open. Step inside. Raise a hand and press the light switch on. Stand in front of the sink. Turn the tap handle. Put both hands under the running water. Cup water and splash it onto the face. Pick up the towel. Wipe the face with the towel. Pick up the toothbrush. Turn the tap on. Wet the toothbrush under the water. Put the toothbrush down. Pick up the toothpaste tube. Unscrew the cap. Squeeze toothpaste onto the bristles. Put the toothpaste down. Raise the toothbrush to the mouth. Brush the teeth up and down. Spit into the sink. Rinse the mouth with water. Turn the tap off. Put the toothbrush back into the holder. Turn the light switch off. Walk out of the bathroom."
  },
  {
    "time": "07:00-07:30",
    "location": "Kitchen",
    "activity": "Making and eating breakfast, preparing coffee with the kettle",
    "desc": "Walk into the kitchen. Press the light switch on. Open the refrigerator door. Take out the milk and eggs. Close the refrigerator door. Put the items on the counter. Open the cupboard door. Take out a bowl and a plate. Close the cupboard door. Crack the egg into the bowl. Pick up a fork and beat the egg. Pick up a slice of bread. Put the bread into the toaster. Press the toaster lever down. Pick up the kettle. Walk to the sink. Turn the tap on. Fill the kettle with water. Turn the tap off. Carry the kettle back. Place the kettle on its base. Press the kettle switch on. Pick up a mug. Put a spoon of coffee powder into the mug. Wait for the kettle to boil. Press the kettle switch off. Lift the kettle and pour hot water into the mug. Put the kettle down. Take the toast out of the toaster. Put the toast on the plate. Sit down at the table. Pick up the fork and eat the egg. Lift the mug and drink the coffee. Stand up. Carry the plate and mug to the sink. Rinse them under the tap."
  },
  {
    "time": "07:30-08:00",
    "location": "Bedroom 1",
    "activity": "Getting dressed and packing work bag for the day",
    "desc": "Walk into Bedroom 1. Open the wardrobe door. Take out a shirt and trousers. Lay them on the bed. Take off the sleepwear. Put on the shirt. Button the shirt. Put on the trousers. Pull up the zip. Fasten the belt. Walk to the dresser. Pick up the socks. Sit on the bed. Pull the socks onto both feet. Stand up. Pick up the shoes from the floor. Put on the left shoe. Tie the laces. Put on the right shoe. Tie the laces. Pick up the work bag from the chair. Open the bag. Put the laptop charger into the bag. Put the notebook and pen into the bag. Zip the bag closed. Pick up the phone from the nightstand. Put the phone into the pocket. Pull the fan cord to switch the fan off. Walk out of the bedroom."
  },
  {
    "time": "08:00-09:00",
    "location": "Out",
    "activity": "Commuting to the nonprofit office",
    "desc": "Walk out of the apartment door. Pull the door closed. Lock the door with the key. Walk down the corridor. Press the elevator button. Step into the elevator. Press the ground floor button. Step out of the elevator. Walk out of the building. Walk to the bus stop. Stand at the bus stop. Take the phone out of the pocket. Check the bus arrival time on the phone. Put the phone back into the pocket. Step onto the bus. Tap the card on the card reader. Walk down the aisle. Hold the handrail. Get off the bus at the stop. Walk along the pavement. Turn the corner. Walk to the office entrance. Push the glass door open. Step into the office. Walk to the desk. Put the bag down beside the desk."
  },
  {
    "time": "09:00-17:00",
    "location": "Out",
    "activity": "Working as a community program coordinator: coordinating programs, meeting community partners and running sessions",
    "desc": "Sit down at the desk. Open the work bag. Take out the notebook and pen. Place them on the desk. Open the laptop. Press the power button. Type the login password. Open the email client. Read the new emails. Reply to the emails by typing. Stand up. Walk to the meeting room. Sit at the meeting table. Open the notebook. Take notes with the pen during the partner meeting. Speak to the partner: 'Let's confirm the schedule for next week.' Nod and write down the agreed date. Stand up. Shake hands with the partner. Walk back to the desk. Sit down. Open the program spreadsheet on the laptop. Type the updated participant list. Pick up the phone. Call a community partner. Say: 'The session starts at ten on Friday.' End the call. Put the phone down. Stand up. Walk to the activity hall. Arrange the chairs in a circle. Set the sign-in sheet on the table. Greet the participants at the door. Start the session. Speak to the group and give instructions. Hand out the printed materials. Walk among the participants. Answer questions. Collect the sign-in sheet. End the session. Walk back to the desk. Sit down. Type the session summary into the laptop. Save the file. Close the laptop."
  },
  {
    "time": "17:00-18:00",
    "location": "Out",
    "activity": "Commuting home from the office",
    "desc": "Stand up from the desk. Put the notebook and pen into the bag. Zip the bag. Pick up the bag. Walk to the office door. Push the door open. Walk to the bus stop. Stand at the bus stop. Take the phone out of the pocket. Look at the phone screen. Put the phone back. Step onto the bus. Tap the card on the card reader. Hold the handrail. Get off the bus at the stop. Walk along the pavement. Walk to the apartment building. Push the entrance door open. Press the elevator button. Step into the elevator. Press the floor button. Step out of the elevator. Walk to the apartment door. Unlock the door with the key. Push the door open. Step inside. Close the door. Take off the shoes. Put the shoes on the shoe rack. Walk into the kitchen."
  },
  {
    "time": "18:00-19:00",
    "location": "Kitchen",
    "activity": "Cooking dinner with the induction cooker and eating",
    "desc": "Press the kitchen light switch on. Open the refrigerator door. Take out the vegetables and meat. Close the refrigerator door. Put the items on the counter. Walk to the sink. Turn the tap on. Rinse the vegetables under the water. Turn the tap off. Put the vegetables on the cutting board. Pick up the knife. Cut the vegetables into pieces. Pick up the meat. Cut the meat into pieces. Push the cut pieces to one side. Place the pot on the induction cooker. Press the power button on the induction cooker. Press the heat button to set the power. Pour oil into the pot. Wait for the oil to heat. Put the meat into the pot. Pick up the spatula and stir the meat. Put the vegetables into the pot. Add salt and stir. Press the heat button to lower the power. Put the lid on the pot. Open the cupboard door. Take out a plate and a bowl. Close the cupboard door. Press the power button on the induction cooker to switch it off. Pick up the pot. Pour the food onto the plate. Carry the plate to the table. Sit down at the table. Pick up the chopsticks and eat. Stand up. Carry the plate and bowl to the sink. Rinse them under the tap. Press the kitchen light switch off. Walk to the living room."
  },
  {
    "time": "19:00-20:00",
    "location": "Living Room",
    "activity": "Relaxing and watching TV",
    "desc": "Walk to the sofa. Sit down on the sofa. Lean back against the cushion. Pick up the TV remote from the coffee table. Press the power button on the remote. Point the remote at the TV. Press the channel button. Put the remote down on the sofa armrest. Take the phone out of the pocket. Look at the phone screen. Scroll the phone with the thumb. Put the phone down on the coffee table. Pick up the remote again. Press the volume button. Put the remote down. Cross the legs. Lean back. Pick up the remote. Press the channel button again. Put the remote down. Sit and watch the TV screen. Pick up the mug from the coffee table. Lift the mug and drink. Put the mug down. Pick up the remote. Press the power button to switch the TV off. Put the remote on the coffee table. Stand up from the sofa."
  },
  {
    "time": "20:00-20:30",
    "location": "Living Room",
    "activity": "Tidying the living room and vacuuming the floor",
    "desc": "Pick up the mug from the coffee table. Carry the mug to the kitchen. Put the mug into the sink. Walk back to the living room. Pick up the cushion from the floor. Put the cushion on the sofa. Pick up the magazines from the coffee table. Put the magazines on the shelf. Fold the blanket. Put the folded blanket on the sofa armrest. Walk to the corner. Unwind the vacuum cleaner cord. Plug the cord into the wall socket. Press the power button on the vacuum cleaner. Hold the handle. Push the vacuum cleaner across the floor. Pull it back toward the body. Bend down and push the nozzle under the coffee table. Pull it out. Vacuum along the sofa edge. Vacuum toward the door. Push the vacuum cleaner over the rug. Pull it back. Press the power button to switch it off. Pull the plug out of the socket. Wind the cord around the hooks. Carry the vacuum cleaner back to the corner. Put it down."
  },
  {
    "time": "20:30-21:30",
    "location": "Living Room",
    "activity": "Using the computer to plan next day's community program and reply to emails",
    "desc": "Walk to the desk. Pull out the chair. Sit down on the chair. Open the laptop lid. Press the power button. Type the login password. Open the email client. Click the inbox. Open the first email. Type a reply. Click send. Open the second email. Type a reply. Click send. Open the calendar program. Click on tomorrow's date. Type the program title into the entry. Type the start time and end time. Type the location of the session. Click save. Open the document with the participant list. Scroll down the list. Type the new names. Delete the cancelled names. Click save. Open the checklist document. Type the items for tomorrow. Move the mouse and click the print preview. Close the laptop lid. Stand up. Push the chair back under the desk."
  },
  {
    "time": "21:30-22:00",
    "location": "Bathroom",
    "activity": "Taking a shower and getting ready for bed",
    "desc": "Walk into the bathroom. Press the light switch on. Pull the shower curtain aside. Turn the shower tap on. Put a hand under the water to check the temperature. Turn the tap to adjust the temperature. Step into the shower. Wet the hair under the water. Pick up the shampoo bottle. Open the cap. Pour shampoo into the palm. Put the bottle down. Rub the shampoo into the hair. Rinse the hair under the water. Pick up the soap. Rub the soap over the body. Put the soap back into the dish. Rinse the body under the water. Turn the shower tap off. Step out of the shower. Pick up the towel from the hook. Rub the towel over the hair. Wipe the body with the towel. Hang the towel back on the hook. Pick up the toothbrush. Turn the tap on. Wet the toothbrush. Put the toothbrush down. Pick up the toothpaste. Squeeze toothpaste onto the bristles. Brush the teeth. Spit into the sink. Rinse the mouth. Turn the tap off. Hang the toothbrush in the holder. Press the light switch off. Walk out of the bathroom."
  },
  {
    "time": "22:00-22:30",
    "location": "Bedroom 1",
    "activity": "Reading with the desk lamp to wind down",
    "desc": "Walk into Bedroom 1. Walk to the desk. Press the desk lamp switch on. Pull out the chair. Sit down on the chair. Pick up the book from the desk. Open the book to the marked page. Hold the book with both hands. Read the page. Turn the page with a finger. Read the next page. Turn the page again. Close the book. Put the book down on the desk. Stand up from the chair. Push the chair under the desk. Press the desk lamp switch off. Walk to the bed. Pull back the blanket. Sit on the edge of the bed."
  },
  {
    "time": "22:30-24:00",
    "location": "Bedroom 1",
    "activity": "Sleeping",
    "desc": "Lie down on the bed. Pull the blanket up over the body. Place the head on the pillow. Turn onto the right side. Pull the blanket up to the shoulders. Place one arm under the pillow. Close eyes. Turn onto the left side. Adjust the pillow with a hand. Turn onto the back. Rest both arms along the body. Turn onto the right side. Pull the blanket higher. Remain lying still. Turn onto the left side. Remain lying still with eyes closed."
  }
]

Household structure and appliances:
{
  "Bedroom 1": {
    "appliances": [
      {
        "unique_id": "bedroom_1_fan",
        "name": "Fan",
        "type": "on_demand",
        "power_watts": 60,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "cooling"
      }
    ]
  },
  "Bedroom 2": {
    "appliances": [
      {
        "unique_id": "bedroom_2_desklamp",
        "name": "DeskLamp",
        "type": "on_demand",
        "power_watts": 15,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "bedroom_2_spaceheater",
        "name": "SpaceHeater",
        "type": "on_demand",
        "power_watts": 2000,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "heating"
      }
    ]
  },
  "Kitchen": {
    "appliances": [
      {
        "unique_id": "kitchen_refrigerator",
        "name": "Refrigerator",
        "type": "always_on",
        "power_watts": 100,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "kitchen_microwave",
        "name": "Microwave",
        "type": "on_demand",
        "power_watts": 1000,
        "standby_watts": 2,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "kitchen_inductioncooker",
        "name": "InductionCooker",
        "type": "on_demand",
        "power_watts": 2000,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "kitchen_rangehood",
        "name": "RangeHood",
        "type": "on_demand",
        "power_watts": 200,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "kitchen_oven",
        "name": "Oven",
        "type": "cycle",
        "power_watts": 2200,
        "standby_watts": 2,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual",
        "energy_per_cycle_kwh": 1.5,
        "cycle_minutes": 60
      },
      {
        "unique_id": "kitchen_toaster",
        "name": "Toaster",
        "type": "on_demand",
        "power_watts": 1200,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "kitchen_kettle",
        "name": "Kettle",
        "type": "on_demand",
        "power_watts": 2000,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "kitchen_dishwasher",
        "name": "Dishwasher",
        "type": "cycle",
        "power_watts": 1800,
        "standby_watts": 2,
        "duty_cycle": 1.0,
        "flexible": true,
        "season": "annual",
        "energy_per_cycle_kwh": 1.1,
        "cycle_minutes": 120
      },
      {
        "unique_id": "kitchen_light",
        "name": "Light",
        "type": "on_demand",
        "power_watts": 40,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      }
    ]
  },
  "Bathroom": {
    "appliances": [
      {
        "unique_id": "bathroom_waterheater",
        "name": "WaterHeater",
        "type": "on_demand",
        "power_watts": 3000,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": true,
        "season": "annual"
      },
      {
        "unique_id": "bathroom_light",
        "name": "Light",
        "type": "on_demand",
        "power_watts": 40,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "bathroom_dehumidifier",
        "name": "Dehumidifier",
        "type": "on_demand",
        "power_watts": 500,
        "standby_watts": 0,
        "duty_cycle": 0.7,
        "flexible": false,
        "season": "heating"
      },
      {
        "unique_id": "bathroom_fan",
        "name": "Fan",
        "type": "on_demand",
        "power_watts": 60,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "cooling"
      }
    ]
  },
  "Living Room": {
    "appliances": [
      {
        "unique_id": "living_room_tv",
        "name": "TV",
        "type": "on_demand",
        "power_watts": 150,
        "standby_watts": 3,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "living_room_airconditioner",
        "name": "AirConditioner",
        "type": "on_demand",
        "power_watts": 2000,
        "standby_watts": 0,
        "duty_cycle": 0.6,
        "flexible": true,
        "season": "annual"
      },
      {
        "unique_id": "living_room_router",
        "name": "Router",
        "type": "always_on",
        "power_watts": 12,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "living_room_gameconsole",
        "name": "GameConsole",
        "type": "on_demand",
        "power_watts": 150,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "living_room_light",
        "name": "Light",
        "type": "on_demand",
        "power_watts": 40,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "living_room_vacuumcleaner",
        "name": "VacuumCleaner",
        "type": "on_demand",
        "power_watts": 1200,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      }
    ]
  },
  "Member 1 personal appliances": {
    "appliances": [
      {
        "unique_id": "member_1_computer",
        "name": "Computer",
        "type": "on_demand",
        "power_watts": 200,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "member_1_phone",
        "name": "Phone",
        "type": "charging",
        "power_watts": 20,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": true,
        "season": "annual"
      },
      {
        "unique_id": "member_1_desklamp",
        "name": "DeskLamp",
        "type": "on_demand",
        "power_watts": 15,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      }
    ]
  },
  "Member 2 personal appliances": {
    "appliances": [
      {
        "unique_id": "member_2_computer",
        "name": "Computer",
        "type": "on_demand",
        "power_watts": 65,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "member_2_phone",
        "name": "Phone",
        "type": "charging",
        "power_watts": 20,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": true,
        "season": "annual"
      },
      {
        "unique_id": "member_2_monitor",
        "name": "Monitor",
        "type": "on_demand",
        "power_watts": 30,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      }
    ]
  }
}

Environment information:
- Season: Spring
- Weather: Sunny
- Temperature: 20 degrees

Today is a critical peak pricing (CPP) event: electricity used during the critical peak window 17:00-20:00 is charged at 0.90 AUD/kWh, several times the normal rate. To avoid the high critical-peak price, shift flexible high-power use outside 17:00-20:00 where possible.



## Appliance type explanation

### 1. on_demand (use-on-demand appliances)
- Description: devices that only consume power when used (e.g., desk lamp, TV, A/C)
- Available actions:
  - "use": use the device (consumes power)
  - "idle": do not use the device (no power consumption)

### 2. charging (charging devices)
- Description: charging devices (e.g., phone, electric vehicle)
- Available actions:
  - "charge_home": charge using household electricity (counts toward household usage)
  - "charge_external": charge using external electricity (does not count toward household usage)
  - "use": use the device (consumes previously charged power, no new consumption)
  - "idle": neither use nor charge
- Charge the EV/E-bike only until its battery is full, then set it to "idle". A device can absorb at most one full battery per day, so never charge beyond its remaining capacity. Prefer overnight/off-peak hours for EV and E-bike charging.

### 3. always_on (continuously consuming devices)
- Description: devices that consume power continuously (e.g., refrigerator)
- Available actions: none (auto-runs, no decision needed)

### 4. cycle (fixed-energy-per-run appliances)
- Description: multi-phase appliances that complete a fixed program per run (e.g., washing machine, clothes dryer, dishwasher, oven, rice cooker)
- Available actions:
  - "run": start one full cycle (costs the appliance's fixed cycle energy; do not model the cost as power x time)
  - "idle": do not run (no cycle energy consumed)
- A full run costs the full cycle energy; a partial run costs proportionally.

## Decision principles

1. **Decide based on activity content**: decide which appliances are needed based on the member's activity and room
2. **Only use available actions**: each appliance can only use the actions listed in its available_actions
3. **always_on devices need no decision**: continuously consuming devices like refrigerators auto-run; do not include them in the output
4. **Consider environmental factors**: season, weather, and temperature affect electricity demand (e.g., A/C in summer)
5. **Match lifestyle habits**: decide according to the member's habit traits
6. **Be mindful of energy saving**: set appliances in a room to idle when leaving it
7. **Appliance use when out**:
   - When the location is "Out", ONLY this member's personal portable appliances may be operated (e.g. Phone, Laptop, Computer, DeskLamp).
   - Room appliances (lights, TV, A/C, kitchen appliances, water heater, washing machine, etc.) MUST NOT be operated while Out.
   - While Out, `charge_home` is FORBIDDEN; only `charge_external`, `use`, and `idle` are valid for personal appliances.
    - The downstream validator drops every room appliance operation and every `charge_home` issued while Out.
8. **Use standby_watts for idle draw**: an appliance left idle/standby still draws its `standby_watts`; do not assume idle means zero consumption.
9. **Respect duty_cycle**: appliances with `duty_cycle` below 1 (e.g. thermostatic loads such as A/C) cycle on and off; never assume 100% duty when deciding runtime.
10. **Respect season**: match `season` against the environment: `heating` appliances matter in cold weather, `cooling` appliances in hot weather.
11. **Prefer off-peak for flexible loads**: when a peak/policy context is given, shift appliances marked `flexible: true` away from the configured peak periods.

## Typical usage durations (must follow, keep realistic)

| Appliance | Typical single-use duration | Daily cumulative cap |
|---|---|---|
| EV charging | Charge 2-4 hours at night to full, **stop when full** (one full battery per day max); recommended after 22:00 | 4 hours |
| E-bike charging | Charge 1-3 hours overnight, **stop when full** (one full battery per day max) | 0.7 kWh |
| Water heater | 15-30 minutes per shower | 45 minutes |
| A/C | Can turn off after 1-3 hours (comfortable temperature reached) | 6 hours |
| Space heater | 1-3 hours per session | 6 hours |
| Fan | 1-8 hours during daytime/heat | 8 hours |
| Dehumidifier | 1-3 hours per session | 8 hours |
| Washing machine | 1 cycle (1-1.5 hours per load) | 1-2 loads per day |
| Clothes dryer | 1 cycle (1.5-2 hours per load) | 1 load per day |
| Dishwasher | 1 cycle (1.5-2 hours) | 1-2 loads per day; prefer off-peak/after 21:00 |
| Induction cooker/rice cooker | 30-60 minutes for cooking | 2 hours |
| Oven | 30-90 minutes per use | 2 hours |
| Microwave | 3-10 minutes to heat | 1 hour |
| Kettle | 2-6 minutes per boil | as needed |
| Toaster | 2-5 minutes per use | as needed |
| TV | 1-3 hours of watching | 8 hours |
| Computer | used during work hours | 10 hours |
| Monitor | on only while the computer is in use | same as computer |
| Game console | 1-3 hours per session | as needed |
| Phone charging | 1-2 hours to full | 4 hours |
| Lamp/desk lamp | on whenever someone is in the room | 16 hours |
| Vacuum cleaner | 15-30 minutes per cleaning | 1 hour |
| Range hood | on while cooking | 2 hours |
| Freezer/Router | always_on - auto-runs, no decision | n/a |

**Important**: do not run high-power appliances (A/C/EV/water heater) continuously for long periods. For example, the EV may charge at most 4 hours per day and should be set to idle once full; never charge more than one full battery per day.
If a canonical activity segment is longer than an appliance's allowed runtime, still include the semantically necessary operation. The downstream energy calculator will clip its actual powered minutes to the daily cap; never omit a required appliance solely because the timeline segment cannot be split.

## Typical usage periods (Australian schedule baseline, Xia et al. 2026)

| Period | Typical appliance activity |
|---|---|
| 6:30-8:00 wake/breakfast | rice cooker/microwave/induction cooker (breakfast), lamps |
| 8:00-17:00 work hours | computer (when working from home), standby |
| 17:00-19:00 return/dinner | induction cooker/range hood/rice cooker (dinner), water heater (shower) |
| 19:00-22:30 evening leisure | TV/computer/lamps, washing machine/vacuum (as needed) |
| 22:30-07:00 night | EV charging (starting after 22:00, 2-4 hours), phone charging |

- A/C: hot summer periods (12:00-21:00 as needed), turn off once comfortable
- Washing machine/vacuum: weekday evenings or weekend daytime (do not run late at night, noise)
- The above are typical periods and must be consistent with the member's timeline activities; reasonable deviations are allowed

## Allowed unique_id list (copy exactly, nothing else is valid)

Every operation's `unique_id` MUST be copied character-for-character from the list below. Do NOT invent, shorten, translate, or paraphrase an id. Any id that is not in this list is invalid and will be discarded by the downstream validator.

- bedroom_1_fan
- bedroom_2_desklamp
- bedroom_2_spaceheater
- kitchen_microwave
- kitchen_inductioncooker
- kitchen_rangehood
- kitchen_oven
- kitchen_toaster
- kitchen_kettle
- kitchen_dishwasher
- kitchen_light
- bathroom_waterheater
- bathroom_light
- bathroom_dehumidifier
- bathroom_fan
- living_room_tv
- living_room_airconditioner
- living_room_gameconsole
- living_room_light
- living_room_vacuumcleaner
- member_1_computer
- member_1_phone
- member_1_desklamp
- member_2_computer
- member_2_phone
- member_2_monitor

Always-on appliances (do NOT create operations for these):
- kitchen_refrigerator
- living_room_router

## Output format

Output JSON format (return ONLY the JSON, nothing else):
- Output language: all generated VALUES (location room names, activity descriptions) MUST be written in English, because the downstream system matches English tokens. The English text in this prompt is instruction only.
{
  "member": "Member 1",
  "appliance_decisions": [
    {
      "time": "time segment (e.g., 08:00-09:00)",
      "location": "room name",
      "activity": "activity description",
      "operations": [
        {
          "unique_id": "appliance unique ID",
          "action": "action (must be one of the appliance's available_actions)"
        }
      ]
    }
  ]
}

## Important constraints

1. **Must use unique_id**: do not use appliance names. Copy a unique_id character-for-character from the supplied household structure; never construct, shorten, or guess an ID.
2. **Actions must be valid**: action must be in the appliance's available_actions list. For `cycle` appliances output ONLY `run` or `idle`; never output `use` for a cycle appliance, and never output `run` for an on_demand appliance.
3. **Skip always_on devices**: do not generate decisions for always_on type appliances
4. **Decide for every time segment**: generate decisions for every time segment in the member's timeline
5. **Decide appliances by location**: decide the appliances of the specific room when in a room; decide personal appliances when out
6. Activity descriptions must be in English
7. Copy every input time, location, and activity value exactly and in the same order. Do not merge, split, add, remove, rename, or extend segments. Only add the operations array.
8. The member field must exactly equal "Member 1".
9. For room appliances, use only appliances belonging to that exact room. When Out, use only this member's personal appliances, or an actual ElectricVehicle if one is supplied.
10. An empty operations array is valid when the activity does not use electricity. Never invent an operation merely to make the list non-empty.
11. Never substitute aliases or synonyms: `computer` vs `laptop` and `tv` vs `television` are different strings. Only the exact unique_ids from the allowed list are valid; aliased ids will be discarded.

```

## Schema

```json
(none)
```

## 返回(原始)

```
{
  "member": "Member 1",
  "appliance_decisions": [
    {
      "time": "00:00-06:30",
      "location": "Bedroom 1",
      "activity": "Sleeping",
      "operations": []
    },
    {
      "time": "06:30-07:00",
      "location": "Bathroom",
      "activity": "Waking up, washing face and brushing teeth",
      "operations": [
        {
          "unique_id": "bathroom_light",
          "action": "use"
        }
      ]
    },
    {
      "time": "07:00-07:30",
      "location": "Kitchen",
      "activity": "Making and eating breakfast, preparing coffee with the kettle",
      "operations": [
        {
          "unique_id": "kitchen_light",
          "action": "use"
        },
        {
          "unique_id": "kitchen_toaster",
          "action": "use"
        },
        {
          "unique_id": "kitchen_kettle",
          "action": "use"
        }
      ]
    },
    {
      "time": "07:30-08:00",
      "location": "Bedroom 1",
      "activity": "Getting dressed and packing work bag for the day",
      "operations": [
        {
          "unique_id": "bedroom_1_fan",
          "action": "idle"
        }
      ]
    },
    {
      "time": "08:00-09:00",
      "location": "Out",
      "activity": "Commuting to the nonprofit office",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "09:00-17:00",
      "location": "Out",
      "activity": "Working as a community program coordinator: coordinating programs, meeting community partners and running sessions",
      "operations": [
        {
          "unique_id": "member_1_computer",
          "action": "use"
        },
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "17:00-18:00",
      "location": "Out",
      "activity": "Commuting home from the office",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "18:00-19:00",
      "location": "Kitchen",
      "activity": "Cooking dinner with the induction cooker and eating",
      "operations": [
        {
          "unique_id": "kitchen_light",
          "action": "use"
        },
        {
          "unique_id": "kitchen_inductioncooker",
          "action": "use"
        },
        {
          "unique_id": "kitchen_rangehood",
          "action": "use"
        }
      ]
    },
    {
      "time": "19:00-20:00",
      "location": "Living Room",
      "activity": "Relaxing and watching TV",
      "operations": [
        {
          "unique_id": "living_room_tv",
          "action": "use"
        },
        {
          "unique_id": "living_room_light",
          "action": "use"
        }
      ]
    },
    {
      "time": "20:00-20:30",
      "location": "Living Room",
      "activity": "Tidying the living room and vacuuming the floor",
      "operations": [
        {
          "unique_id": "living_room_vacuumcleaner",
          "action": "use"
        },
        {
          "unique_id": "living_room_light",
          "action": "use"
        }
      ]
    },
    {
      "time": "20:30-21:30",
      "location": "Living Room",
      "activity": "Using the computer to plan next day's community program and reply to emails",
      "operations": [
        {
          "unique_id": "member_1_computer",
          "action": "use"
        },
        {
          "unique_id": "living_room_light",
          "action": "use"
        }
      ]
    },
    {
      "time": "21:30-22:00",
      "location": "Bathroom",
      "activity": "Taking a shower and getting ready for bed",
      "operations": [
        {
          "unique_id": "bathroom_light",
          "action": "use"
        },
        {
          "unique_id": "bathroom_waterheater",
          "action": "use"
        }
      ]
    },
    {
      "time": "22:00-22:30",
      "location": "Bedroom 1",
      "activity": "Reading with the desk lamp to wind down",
      "operations": [
        {
          "unique_id": "member_1_desklamp",
          "action": "use"
        }
      ]
    },
    {
      "time": "22:30-24:00",
      "location": "Bedroom 1",
      "activity": "Sleeping",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "charge_home"
        }
      ]
    }
  ]
}
```

