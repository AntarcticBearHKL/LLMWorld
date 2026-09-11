# s4_appliance_decision  (attempt 1)

## 对话信息

- time: 2026-09-11 14:15:46
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
    "activity": "Sleeping in own private bedroom",
    "desc": "Lie down on the bed. Close eyes. Remain lying on the bed. Turn over onto one side. Pull the duvet up. Remain asleep. Turn over onto the other side. Adjust pillow. Remain lying on the bed asleep until the alarm sounds."
  },
  {
    "time": "06:30-07:00",
    "location": "Bathroom",
    "activity": "Showering, brushing teeth and getting ready for the day",
    "desc": "Sit up on the bed. Stand up. Walk to the bathroom. Turn on the bathroom light. Turn on the shower tap. Step into the shower. Wet hair and body. Apply shampoo. Rub scalp. Rinse hair. Apply soap to body. Rinse body. Turn off the shower tap. Step out. Pick up towel. Rub hair dry. Rub body dry. Hang towel on the rack. Pick up toothbrush. Turn on the tap. Squeeze toothpaste onto the toothbrush. Brush teeth. Rinse mouth. Spit into the sink. Turn off the tap. Wipe face with the towel. Turn off the light. Walk out of the bathroom."
  },
  {
    "time": "07:00-07:45",
    "location": "Kitchen",
    "activity": "Preparing and eating breakfast, making coffee with the kettle",
    "desc": "Walk into the kitchen. Turn on the kitchen light. Open the refrigerator door. Take out milk and eggs. Close the refrigerator door. Place the items on the counter. Open the cupboard. Take out a bowl and a pan. Close the cupboard. Pick up the kettle. Open the kettle lid. Fill the kettle with water at the tap. Close the lid. Place the kettle on its base. Press the kettle switch on. Crack the eggs into the bowl. Pick up the pan. Place the pan on the induction cooker. Press the induction cooker power button. Pour oil into the pan. Pour the egg mixture into the pan. Stir the eggs with a spatula. Turn off the induction cooker. Slide the eggs onto a plate. Pick up a mug. Pour coffee powder into the mug. Pour hot water from the kettle into the mug. Pour milk into the mug. Stir with a spoon. Carry the plate and mug to the table. Sit down on the chair. Eat the eggs with a fork. Drink the coffee. Stand up. Carry the plate and mug to the sink. Rinse the plate and mug. Place them in the dishwasher."
  },
  {
    "time": "07:45-08:00",
    "location": "Bedroom 1",
    "activity": "Packing work bag, checking phone for shift messages and tidying up",
    "desc": "Walk to Bedroom 1. Pick up the work bag from the floor. Open the bag. Place a water bottle inside. Place a stethoscope inside. Zip the bag closed. Pick up the phone from the bedside table. Press the phone power button. Tap the screen. Scroll through shift messages. Tap a message to reply. Type a reply. Send the message. Place the phone in the bag pocket. Pick up a jacket. Put the jacket on. Smooth the duvet on the bed. Place a pillow at the head of the bed. Pick up the bag. Turn off the bedroom light. Walk out of the bedroom."
  },
  {
    "time": "08:00-09:00",
    "location": "Out",
    "activity": "Commuting to the hospital for the day shift",
    "desc": "Walk out of the house. Close the front door. Lock the front door with the key. Walk to the bus stop. Stand at the bus stop. Take the phone out. Check the time on the phone. Put the phone back in the pocket. Board the bus. Tap the travel card on the reader. Sit down on a seat. Place the bag on the lap. Look out of the window. Stand up when the stop arrives. Walk to the bus door. Step off the bus. Walk to the hospital entrance. Push the entrance door open. Walk to the staff changing room. Open the locker. Take out the work uniform. Change into the uniform. Place the bag in the locker. Close the locker. Walk to the ward."
  },
  {
    "time": "09:00-13:00",
    "location": "Out",
    "activity": "Working as a health care professional: patient assessments, medication rounds and clinical documentation",
    "desc": "Pick up the patient chart. Walk to the first patient bed. Greet the patient. Ask the patient how they are feeling. Measure the patient's blood pressure with the cuff. Wrap the cuff around the arm. Press the start button on the monitor. Read the numbers on the screen. Write the numbers on the chart. Pick up the thermometer. Place it near the patient's forehead. Press the button. Read the temperature. Record the temperature on the chart. Walk to the medication cart. Push the cart along the corridor. Pick up the medication cup. Check the patient wristband. Hand the cup to the patient. Hand a cup of water to the patient. Replace the cup on the cart. Push the cart to the next bed. Repeat the medication round. Sit down at the desk. Turn on the computer. Type clinical notes into the system. Save the notes. Pick up the phone. Call the pharmacy. Speak about a medication order. Hang up the phone."
  },
  {
    "time": "13:00-13:30",
    "location": "Out",
    "activity": "Taking a lunch break in the staff room",
    "desc": "Walk to the staff room. Push the door open. Walk to the locker. Open the locker. Take out the lunch bag. Close the locker. Walk to the table. Sit down on the chair. Open the lunch bag. Take out a sandwich. Unwrap the sandwich. Take a bite. Chew and swallow. Open the water bottle. Take a sip. Close the bottle. Continue eating the sandwich. Wipe hands with a napkin. Place the wrapper in the bin. Stand up. Walk to the sink. Rinse the water bottle. Walk to the locker. Open the locker. Place the lunch bag inside. Close the locker. Walk to the door. Push the door open. Walk to the ward."
  },
  {
    "time": "13:30-17:00",
    "location": "Out",
    "activity": "Continuing clinical duties: patient care, handover notes and coordinating with the care team",
    "desc": "Walk to the patient bed. Pick up the chart. Check the patient's IV line. Adjust the IV drip rate. Write the adjusted rate on the chart. Pick up the blood pressure cuff. Wrap it around the patient's arm. Press the button. Read the numbers. Write the numbers on the chart. Walk to the supply room. Open the cupboard. Take out dressing packs. Close the cupboard. Walk back to the patient bed. Open the dressing pack. Put on gloves. Clean the wound with a swab. Apply a new dressing. Remove the gloves. Dispose of the gloves in the bin. Walk to the nurses' station. Sit down at the computer. Type handover notes. Save the file. Pick up the phone. Call the next shift nurse. Speak about the patient status. Hang up the phone. Stand up. Walk to the team meeting room. Sit down. Discuss the care plan with the team. Stand up. Walk back to the ward."
  },
  {
    "time": "17:00-18:00",
    "location": "Out",
    "activity": "Commuting home from the hospital",
    "desc": "Walk to the staff changing room. Open the locker. Take out the bag. Change out of the work uniform. Put on casual clothes. Place the uniform in the laundry bag. Close the locker. Pick up the bag. Walk to the exit. Push the exit door open. Walk to the bus stop. Stand at the bus stop. Take the phone out. Check the bus arrival time. Put the phone back in the pocket. Board the bus. Tap the travel card on the reader. Sit down on a seat. Place the bag on the lap. Look out of the window. Stand up when the stop arrives. Walk to the bus door. Step off the bus. Walk to the house. Unlock the front door. Push the door open. Close the door behind."
  },
  {
    "time": "18:00-18:45",
    "location": "Kitchen",
    "activity": "Cooking and eating dinner, loading the dishwasher afterwards",
    "desc": "Walk into the kitchen. Turn on the kitchen light. Open the refrigerator door. Take out vegetables and chicken. Close the refrigerator door. Place the items on the counter. Pick up a knife. Cut the vegetables on the cutting board. Pick up the pan. Place the pan on the induction cooker. Press the power button. Pour oil into the pan. Add the chicken. Stir with a spatula. Add the vegetables. Stir again. Add salt with a spoon. Turn off the induction cooker. Slide the food onto a plate. Carry the plate to the table. Sit down on the chair. Eat the dinner with a fork and knife. Drink water from a glass. Stand up. Carry the plate, fork, knife and glass to the sink. Rinse them under the tap. Open the dishwasher door. Place the plate, fork, knife and glass in the rack. Close the dishwasher door. Press the start button on the dishwasher."
  },
  {
    "time": "18:45-19:15",
    "location": "Bathroom",
    "activity": "Washing up and changing into comfortable clothes",
    "desc": "Walk to the bathroom. Turn on the bathroom light. Turn on the tap. Wet hands. Pick up soap. Rub soap between hands. Rinse hands under the tap. Turn off the tap. Wipe hands with a towel. Walk back to Bedroom 1. Open the wardrobe door. Take out a t-shirt and sweatpants. Close the wardrobe door. Take off the day clothes. Fold the day clothes. Place them on the chair. Put on the t-shirt. Put on the sweatpants. Walk back to the bathroom. Pick up the toothbrush. Turn on the tap. Wet the toothbrush. Turn off the tap. Hang the toothbrush on the holder. Turn off the bathroom light. Walk to the living room."
  },
  {
    "time": "19:15-21:00",
    "location": "Living Room",
    "activity": "Relaxing on the sofa watching TV",
    "desc": "Walk to the sofa. Sit down on the sofa. Pick up the TV remote from the side table. Press the power button on the remote. Point the remote at the TV. Press the channel button. Scroll through channels. Stop on a programme. Place the remote on the sofa armrest. Lean back on the sofa. Watch the TV. Pick up the remote again. Press the volume up button. Place the remote back on the armrest. Stand up. Walk to the kitchen. Open the refrigerator door. Take out a bottle of water. Close the refrigerator door. Walk back to the living room. Sit down on the sofa. Open the bottle. Drink water. Close the bottle. Place the bottle on the side table. Continue watching the TV. Pick up the remote. Press the power button to turn off the TV. Place the remote on the side table. Stand up."
  },
  {
    "time": "21:00-22:00",
    "location": "Living Room",
    "activity": "Using the computer for online continuing education and reviewing the next day's roster",
    "desc": "Walk to the desk. Pull out the chair. Sit down on the chair. Press the computer power button. Wait for the screen to load. Move the mouse. Click the browser icon. Type the web address in the address bar. Press Enter. Log into the continuing education portal. Click the course module. Watch the video lesson. Take notes in a notebook with a pen. Click the next module. Read the slides. Click the quiz link. Answer the quiz questions. Click submit. Close the browser tab. Open the roster page. Read the shift times. Write the shift times in the notebook. Close the browser. Press the computer power button to shut down. Stand up. Push the chair under the desk."
  },
  {
    "time": "22:00-22:30",
    "location": "Bathroom",
    "activity": "Evening hygiene routine before bed",
    "desc": "Walk to the bathroom. Turn on the bathroom light. Pick up the toothbrush. Turn on the tap. Wet the toothbrush. Squeeze toothpaste onto the toothbrush. Turn off the tap. Brush teeth. Rinse mouth with water. Spit into the sink. Turn on the tap. Rinse the toothbrush. Turn off the tap. Place the toothbrush in the holder. Turn on the tap. Wash face with water. Pick up a towel. Wipe face dry. Hang the towel on the rack. Pick up the hairbrush. Brush hair. Place the hairbrush on the shelf. Turn off the bathroom light. Walk out of the bathroom."
  },
  {
    "time": "22:30-24:00",
    "location": "Bedroom 1",
    "activity": "Sleeping in own private bedroom",
    "desc": "Walk into Bedroom 1. Turn on the desk lamp. Sit down on the bed. Take the phone out of the pocket. Place the phone on the bedside table. Plug the phone charger into the wall socket. Connect the cable to the phone. Take off the t-shirt. Take off the sweatpants. Put on pyjamas. Pull back the duvet. Lie down on the bed. Pull the duvet over the body. Turn off the desk lamp. Place the head on the pillow. Close eyes. Turn over onto one side. Remain lying on the bed asleep."
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

Today your household is on a time-of-use (TOU) electricity tariff: peak period 16:00-21:00 at 0.60 AUD/kWh; valley period 22:00-07:00 at 0.18 AUD/kWh; shoulder period (all other times) at 0.35 AUD/kWh. To reduce your bill, shift flexible appliances (electric vehicle charging, washing machine, dishwasher-free routines like hot water use) into the valley period, and avoid running high-power appliances during the peak period unless necessary.



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
      "activity": "Sleeping in own private bedroom",
      "operations": []
    },
    {
      "time": "06:30-07:00",
      "location": "Bathroom",
      "activity": "Showering, brushing teeth and getting ready for the day",
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
      "time": "07:00-07:45",
      "location": "Kitchen",
      "activity": "Preparing and eating breakfast, making coffee with the kettle",
      "operations": [
        {
          "unique_id": "kitchen_light",
          "action": "use"
        },
        {
          "unique_id": "kitchen_kettle",
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
      "time": "07:45-08:00",
      "location": "Bedroom 1",
      "activity": "Packing work bag, checking phone for shift messages and tidying up",
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
      "activity": "Commuting to the hospital for the day shift",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "09:00-13:00",
      "location": "Out",
      "activity": "Working as a health care professional: patient assessments, medication rounds and clinical documentation",
      "operations": []
    },
    {
      "time": "13:00-13:30",
      "location": "Out",
      "activity": "Taking a lunch break in the staff room",
      "operations": []
    },
    {
      "time": "13:30-17:00",
      "location": "Out",
      "activity": "Continuing clinical duties: patient care, handover notes and coordinating with the care team",
      "operations": []
    },
    {
      "time": "17:00-18:00",
      "location": "Out",
      "activity": "Commuting home from the hospital",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "18:00-18:45",
      "location": "Kitchen",
      "activity": "Cooking and eating dinner, loading the dishwasher afterwards",
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
        },
        {
          "unique_id": "kitchen_dishwasher",
          "action": "run"
        }
      ]
    },
    {
      "time": "18:45-19:15",
      "location": "Bathroom",
      "activity": "Washing up and changing into comfortable clothes",
      "operations": [
        {
          "unique_id": "bathroom_light",
          "action": "use"
        }
      ]
    },
    {
      "time": "19:15-21:00",
      "location": "Living Room",
      "activity": "Relaxing on the sofa watching TV",
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
      "time": "21:00-22:00",
      "location": "Living Room",
      "activity": "Using the computer for online continuing education and reviewing the next day's roster",
      "operations": [
        {
          "unique_id": "living_room_computer",
          "action": "use"
        },
        {
          "unique_id": "living_room_monitor",
          "action": "use"
        },
        {
          "unique_id": "living_room_light",
          "action": "use"
        }
      ]
    },
    {
      "time": "22:00-22:30",
      "location": "Bathroom",
      "activity": "Evening hygiene routine before bed",
      "operations": [
        {
          "unique_id": "bathroom_light",
          "action": "use"
        }
      ]
    },
    {
      "time": "22:30-24:00",
      "location": "Bedroom 1",
      "activity": "Sleeping in own private bedroom",
      "operations": [
        {
          "unique_id": "bedroom_1_desklamp",
          "action": "use"
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

