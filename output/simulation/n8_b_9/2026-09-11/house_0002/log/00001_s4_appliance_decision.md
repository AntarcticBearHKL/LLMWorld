# s4_appliance_decision  (attempt 1)

## 对话信息

- time: 2026-09-12 11:31:37
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
- Occupation: Health Care Professional
- Habits: {}

This member's complete timeline:
[
  {
    "time": "00:00-06:30",
    "location": "Bedroom 1",
    "activity": "Sleeping",
    "desc": "Lie down on the bed. Pull the blanket over the body. Close eyes. Turn onto the right side. Adjust the pillow with the left hand. Remain still. Turn onto the back. Pull the blanket up to the shoulders. Turn onto the left side. Place the right arm under the pillow. Remain still. Kick the right foot out from under the blanket. Pull the blanket back over the foot. Turn onto the right side again. Stretch both arms above the head. Lower the arms. Turn onto the back. Open eyes briefly. Close eyes again. Remain still until 06:30."
  },
  {
    "time": "06:30-07:00",
    "location": "Bathroom",
    "activity": "Washing up and personal hygiene",
    "desc": "Sit up on the bed. Push the blanket aside. Stand up. Walk to the bathroom. Push the bathroom door open. Press the light switch to turn on the light. Step to the toilet. Use the toilet. Stand up. Press the flush button. Walk to the sink. Turn on the tap. Put both hands under the water. Pick up the soap. Rub the soap between the hands. Put the soap back on the dish. Rub the hands together. Rinse the hands under the tap. Turn off the tap. Pick up the toothbrush. Squeeze toothpaste onto the toothbrush. Put the toothpaste tube down. Brush the teeth. Rinse the mouth with water from the cup. Spit into the sink. Turn on the tap. Rinse the toothbrush. Turn off the tap. Put the toothbrush back in the holder. Pick up the towel. Wipe the face. Wipe both hands. Hang the towel on the hook. Press the light switch to turn off the light. Walk out of the bathroom."
  },
  {
    "time": "07:00-07:30",
    "location": "Kitchen",
    "activity": "Preparing and eating breakfast",
    "desc": "Walk into the kitchen. Press the light switch to turn on the light. Open the refrigerator door. Take out the milk carton. Take out the eggs. Take out the bread. Close the refrigerator door. Put the items on the counter. Open the cabinet. Take out a bowl. Take out a plate. Close the cabinet. Put the bowl on the counter. Crack two eggs into the bowl. Beat the eggs with a fork. Place the frying pan on the induction cooker. Press the power button on the induction cooker. Pour oil into the pan. Pour the eggs into the pan. Stir the eggs with a spatula. Turn off the induction cooker. Slide the eggs onto the plate. Put two slices of bread into the toaster. Press the toaster lever down. Wait for the toast to pop up. Take the toast out of the toaster. Pour milk into a glass. Carry the plate, glass, and bowl to the table. Sit down on the chair. Eat the eggs with a fork. Pick up the toast. Bite the toast. Drink the milk. Finish eating. Stand up. Carry the dishes to the sink."
  },
  {
    "time": "07:30-08:00",
    "location": "Bedroom 1",
    "activity": "Getting dressed and preparing for work",
    "desc": "Walk into Bedroom 1. Open the wardrobe door. Take out a work shirt. Take out trousers. Take out a pair of socks. Close the wardrobe door. Lay the clothes on the bed. Take off the sleepwear top. Take off the sleepwear bottoms. Put on the work shirt. Button the shirt. Put on the trousers. Pull up the zipper. Fasten the belt. Sit on the bed. Put on the left sock. Put on the right sock. Stand up. Walk to the desk. Pick up the phone from the desk. Press the phone screen to check messages. Put the phone into the pocket. Pick up the work bag from the floor. Open the bag. Put the wallet into the bag. Close the bag. Walk out of Bedroom 1."
  },
  {
    "time": "08:00-09:00",
    "location": "Out",
    "activity": "Commuting to work",
    "desc": "Walk out of the house. Close the front door. Lock the door with the key. Put the key into the pocket. Walk along the sidewalk. Wait at the crosswalk. Press the pedestrian button. Cross the street when the light changes. Walk to the bus stop. Stand at the bus stop. Take the phone out of the pocket. Look at the phone screen. Put the phone back into the pocket. Step onto the bus. Tap the card on the card reader. Walk down the aisle. Hold the handrail. Stand near the door. Look at the stop display. Press the stop button. Step off the bus. Walk to the workplace entrance. Push the entrance door open. Walk to the staff room. Put the bag into the locker. Close the locker door."
  },
  {
    "time": "09:00-12:00",
    "location": "Out",
    "activity": "Working as a health care professional",
    "desc": "Walk to the nurses station. Turn on the computer. Log in with the username and password. Open the patient record system. Read the patient list on the monitor. Pick up the phone. Call the ward. Speak: \"Patient in room 3 needs a check.\" Put the phone down. Pick up the clipboard. Walk to room 3. Push the door open. Greet the patient. Check the IV line. Adjust the IV drip rate. Measure the blood pressure with the cuff. Write the reading on the clipboard. Measure the body temperature with the thermometer. Write the reading down. Check the pulse with two fingers on the wrist. Write the reading down. Speak: \"Everything looks fine.\" Walk back to the nurses station. Type the readings into the computer. Pick up the medication tray. Walk to room 5. Hand the medication cup to the patient. Hand the water cup to the patient. Walk back to the nurses station. Answer the telephone. Write a note on the pad. Open the cabinet. Take out a dressing pack. Close the cabinet."
  },
  {
    "time": "12:00-13:00",
    "location": "Out",
    "activity": "Taking a lunch break",
    "desc": "Log off the computer. Stand up from the chair. Push the chair under the desk. Walk to the staff room. Open the locker. Take out the lunch box. Close the locker. Sit down at the staff table. Open the lunch box lid. Pick up the fork. Eat the rice. Eat the vegetables. Drink water from the bottle. Speak to a colleague: \"Busy morning today.\" Pick up the phone. Scroll the phone screen. Put the phone down. Close the lunch box. Stand up. Walk to the sink. Rinse the fork under the tap. Turn off the tap. Wipe the fork with a paper towel. Put the lunch box back into the locker. Close the locker door. Walk to the restroom. Open the restroom door. Close the door. Turn on the tap. Wash both hands. Turn off the tap. Open the door. Walk back to the ward."
  },
  {
    "time": "13:00-17:00",
    "location": "Out",
    "activity": "Working as a health care professional",
    "desc": "Sit down at the nurses station. Turn on the computer. Log in. Open the patient record system. Read the new orders on the screen. Pick up the phone. Call the pharmacy. Speak: \"Please send the new batch of medication.\" Put the phone down. Stand up. Push the chair in. Walk to room 3. Push the door open. Check the IV bag. Replace the empty IV bag with a new one. Hang the new bag on the pole. Adjust the drip rate with the roller clamp. Write the time on the label. Walk to room 5. Pick up the blood pressure cuff. Wrap the cuff around the patient's arm. Press the start button. Read the display. Write the reading on the chart. Walk to the supply room. Open the cabinet. Take out gauze packs. Take out gloves. Close the cabinet. Walk back to the nurses station. Put the supplies into the drawer. Answer the telephone. Write an order note on the pad. Type the note into the computer. Print the report. Pick up the printed report from the printer. Put the report into the file. Log off the computer. Turn off the computer."
  },
  {
    "time": "17:00-18:00",
    "location": "Out",
    "activity": "Commuting home",
    "desc": "Walk to the staff room. Open the locker. Take out the bag. Close the locker door. Walk to the exit. Push the exit door open. Walk to the bus stop. Stand at the bus stop. Take the phone out of the pocket. Look at the phone screen. Put the phone back into the pocket. Step onto the bus. Tap the card on the card reader. Walk down the aisle. Hold the handrail. Look at the stop display. Press the stop button. Step off the bus. Walk along the sidewalk. Wait at the crosswalk. Cross the street. Walk to the front door. Take the key out of the pocket. Insert the key into the lock. Turn the key. Push the front door open. Step inside. Close the door. Lock the door with the key. Put the key back into the pocket."
  },
  {
    "time": "18:00-19:00",
    "location": "Kitchen",
    "activity": "Preparing and eating dinner",
    "desc": "Walk into the kitchen. Put the bag down on the chair. Press the light switch to turn on the light. Open the refrigerator door. Take out the vegetables. Take out the chicken. Take out the rice container. Close the refrigerator door. Put the items on the counter. Open the cabinet. Take out a pot. Take out a cutting board. Take out a knife. Close the cabinet. Put the cutting board on the counter. Place the vegetables on the cutting board. Cut the vegetables with the knife. Put the cut vegetables into the pot. Place the pot on the induction cooker. Press the power button on the induction cooker. Press the start button. Stir the vegetables with a spoon. Open the refrigerator. Take out the sauce bottle. Close the refrigerator. Pour the sauce into the pot. Stir again. Press the stop button. Pick up a bowl. Spoon the vegetables into the bowl. Spoon the rice into another bowl. Carry both bowls to the table. Sit down on the chair. Pick up the chopsticks. Eat the rice. Eat the vegetables. Drink water from the glass. Speak to no one. Finish eating. Stand up. Carry the bowls to the sink."
  },
  {
    "time": "19:00-20:00",
    "location": "Kitchen",
    "activity": "Cleaning up after dinner",
    "desc": "Turn on the tap. Rinse the bowls under the water. Put the bowls into the dishwasher. Put the plates into the dishwasher. Put the chopsticks into the basket. Put the spoon into the basket. Put the pot into the dishwasher. Open the dishwasher door. Add detergent to the dispenser. Close the dishwasher door. Press the start button on the dishwasher. Pick up the sponge. Wipe the counter with the sponge. Rinse the sponge under the tap. Turn off the tap. Wipe the cutting board with the towel. Put the knife back into the drawer. Put the cutting board back into the cabinet. Wipe the induction cooker with the towel. Put the sauce bottle back into the refrigerator. Close the refrigerator door. Take the trash bag out of the bin. Tie the trash bag. Walk to the door. Open the door. Put the trash bag into the outside bin. Walk back inside. Close the door. Press the light switch to turn off the light. Walk out of the kitchen."
  },
  {
    "time": "20:00-22:30",
    "location": "Living Room",
    "activity": "Relaxing and watching TV",
    "desc": "Walk into the living room. Sit down on the sofa. Pick up the remote control from the table. Press the power button to turn on the TV. Press the channel button. Lean back on the sofa. Put the remote control on the sofa cushion. Pick up the phone from the pocket. Unlock the phone screen. Scroll the phone screen. Put the phone down on the table. Watch the TV screen. Pick up the remote control. Press the volume button. Put the remote control down. Stand up. Walk to the kitchen. Open the refrigerator. Take out a bottle of water. Close the refrigerator. Walk back to the living room. Sit down on the sofa. Twist the bottle cap open. Drink water from the bottle. Twist the bottle cap closed. Put the bottle on the table. Pick up the remote control. Press the channel button. Put the remote control down. Lean back on the sofa. Watch the TV screen. Pick up the phone. Type a message on the phone. Send the message. Put the phone on the table. Pick up the remote control. Press the power button to turn off the TV. Put the remote control on the table. Stand up from the sofa. Press the light switch to turn off the light. Walk to the bathroom."
  },
  {
    "time": "22:30-23:00",
    "location": "Bathroom",
    "activity": "Getting ready for bed",
    "desc": "Walk into the bathroom. Press the light switch to turn on the light. Press the water heater switch on. Step to the sink. Turn on the tap. Put both hands under the water. Pick up the soap. Rub the soap between the hands. Put the soap back on the dish. Rub the hands together. Rinse the hands under the tap. Turn off the tap. Pick up the towel. Wipe the face. Wipe both hands. Hang the towel on the hook. Pick up the toothbrush. Squeeze toothpaste onto the toothbrush. Put the toothpaste tube down. Brush the teeth. Rinse the mouth with water. Spit into the sink. Turn on the tap. Rinse the toothbrush. Turn off the tap. Put the toothbrush back into the holder. Step to the toilet. Use the toilet. Stand up. Press the flush button. Press the light switch to turn off the light. Walk out of the bathroom."
  },
  {
    "time": "23:00-24:00",
    "location": "Bedroom 1",
    "activity": "Sleeping",
    "desc": "Walk into Bedroom 1. Push the bedroom door closed. Take off the work shirt. Take off the trousers. Fold the shirt. Put the shirt on the chair. Put the trousers on the chair. Open the wardrobe door. Take out the sleepwear. Close the wardrobe door. Put on the sleepwear top. Put on the sleepwear bottoms. Pick up the phone from the pocket. Place the phone on the desk. Press the phone screen to set the alarm. Put the phone down on the desk. Press the light switch to turn off the light. Pull the blanket aside. Lie down on the bed. Pull the blanket over the body. Turn onto the right side. Adjust the pillow with the left hand. Close eyes. Remain still."
  }
]

Household structure and appliances:
{
  "Bedroom 1": {
    "appliances": [
      {
        "unique_id": "bedroom_1_tv",
        "name": "TV",
        "type": "on_demand",
        "power_watts": 150,
        "standby_watts": 3,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "bedroom_1_airconditioner",
        "name": "AirConditioner",
        "type": "on_demand",
        "power_watts": 2000,
        "standby_watts": 0,
        "duty_cycle": 0.6,
        "flexible": true,
        "season": "annual"
      },
      {
        "unique_id": "bedroom_1_desklamp",
        "name": "DeskLamp",
        "type": "on_demand",
        "power_watts": 15,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "bedroom_1_light",
        "name": "Light",
        "type": "on_demand",
        "power_watts": 40,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
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
        "unique_id": "living_room_computer",
        "name": "Computer",
        "type": "on_demand",
        "power_watts": 200,
        "standby_watts": 2,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "living_room_monitor",
        "name": "Monitor",
        "type": "on_demand",
        "power_watts": 30,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
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
        "unique_id": "living_room_spaceheater",
        "name": "SpaceHeater",
        "type": "on_demand",
        "power_watts": 2000,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "heating"
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
        "unique_id": "bathroom_washingmachine",
        "name": "WashingMachine",
        "type": "cycle",
        "power_watts": 500,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": true,
        "season": "annual",
        "energy_per_cycle_kwh": 0.6,
        "cycle_minutes": 90
      },
      {
        "unique_id": "bathroom_clothesdryer",
        "name": "ClothesDryer",
        "type": "cycle",
        "power_watts": 2500,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": true,
        "season": "annual",
        "energy_per_cycle_kwh": 2.5,
        "cycle_minutes": 120
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
      }
    ]
  },
  "Member 1 personal appliances": {
    "appliances": [
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
        "unique_id": "member_1_computer",
        "name": "Computer",
        "type": "on_demand",
        "power_watts": 60,
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

- bedroom_1_tv
- bedroom_1_airconditioner
- bedroom_1_desklamp
- bedroom_1_light
- bedroom_1_fan
- kitchen_microwave
- kitchen_inductioncooker
- kitchen_rangehood
- kitchen_kettle
- kitchen_toaster
- kitchen_oven
- kitchen_dishwasher
- kitchen_light
- living_room_tv
- living_room_computer
- living_room_monitor
- living_room_gameconsole
- living_room_spaceheater
- living_room_light
- living_room_vacuumcleaner
- bathroom_waterheater
- bathroom_washingmachine
- bathroom_clothesdryer
- bathroom_light
- bathroom_dehumidifier
- member_1_phone
- member_1_computer

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
      "operations": [
        {
          "unique_id": "bedroom_1_light",
          "action": "idle"
        },
        {
          "unique_id": "bedroom_1_airconditioner",
          "action": "idle"
        },
        {
          "unique_id": "bedroom_1_tv",
          "action": "idle"
        },
        {
          "unique_id": "member_1_phone",
          "action": "idle"
        }
      ]
    },
    {
      "time": "06:30-07:00",
      "location": "Bathroom",
      "activity": "Washing up and personal hygiene",
      "operations": [
        {
          "unique_id": "bathroom_light",
          "action": "use"
        },
        {
          "unique_id": "bathroom_waterheater",
          "action": "idle"
        }
      ]
    },
    {
      "time": "07:00-07:30",
      "location": "Kitchen",
      "activity": "Preparing and eating breakfast",
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
          "unique_id": "kitchen_toaster",
          "action": "use"
        },
        {
          "unique_id": "kitchen_rangehood",
          "action": "use"
        }
      ]
    },
    {
      "time": "07:30-08:00",
      "location": "Bedroom 1",
      "activity": "Getting dressed and preparing for work",
      "operations": [
        {
          "unique_id": "bedroom_1_light",
          "action": "use"
        },
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "08:00-09:00",
      "location": "Out",
      "activity": "Commuting to work",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "09:00-12:00",
      "location": "Out",
      "activity": "Working as a health care professional",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "12:00-13:00",
      "location": "Out",
      "activity": "Taking a lunch break",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "13:00-17:00",
      "location": "Out",
      "activity": "Working as a health care professional",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "17:00-18:00",
      "location": "Out",
      "activity": "Commuting home",
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
      "activity": "Preparing and eating dinner",
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
      "location": "Kitchen",
      "activity": "Cleaning up after dinner",
      "operations": [
        {
          "unique_id": "kitchen_light",
          "action": "use"
        },
        {
          "unique_id": "kitchen_dishwasher",
          "action": "run"
        }
      ]
    },
    {
      "time": "20:00-22:30",
      "location": "Living Room",
      "activity": "Relaxing and watching TV",
      "operations": [
        {
          "unique_id": "living_room_light",
          "action": "use"
        },
        {
          "unique_id": "living_room_tv",
          "action": "use"
        },
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "22:30-23:00",
      "location": "Bathroom",
      "activity": "Getting ready for bed",
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
      "time": "23:00-24:00",
      "location": "Bedroom 1",
      "activity": "Sleeping",
      "operations": [
        {
          "unique_id": "bedroom_1_light",
          "action": "idle"
        },
        {
          "unique_id": "member_1_phone",
          "action": "charge_home"
        }
      ]
    }
  ]
}
```

