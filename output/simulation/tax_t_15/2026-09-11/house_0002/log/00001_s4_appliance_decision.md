# s4_appliance_decision  (attempt 1)

## 对话信息

- time: 2026-09-12 20:50:35
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
    "desc": "Lie down on the bed. Pull the quilt up over the chest. Close eyes. Turn onto the right side. Sleep. Turn onto the back. Move the right arm under the pillow. Sleep. Turn onto the left side. Pull the quilt up to the shoulders. Bend the knees. Sleep. Stretch the legs out. Turn onto the back. Sleep. Roll onto the right side. Pull the quilt over the head. Sleep. Move the left arm out of the quilt. Turn onto the left side. Sleep."
  },
  {
    "time": "06:30-07:00",
    "location": "Bathroom",
    "activity": "Waking up, washing face and taking a morning shower",
    "desc": "Open eyes. Sit up on the bed. Swing both legs over the edge of the bed. Stand up. Walk to the bathroom. Open the bathroom door. Turn on the bathroom light. Turn on the water heater switch. Take off the pajamas. Drop the pajamas into the laundry basket. Turn on the tap. Put the right hand under the water to test the temperature. Turn the tap to adjust the water temperature. Step into the shower area. Wet the head and body with water. Pick up the shampoo bottle. Squeeze shampoo into the left palm. Rub the shampoo onto the hair. Rinse the hair with water. Pick up the soap. Rub the soap over the arms and body. Put the soap back on the dish. Rinse the soap off the body with water. Turn off the tap. Pick up the towel from the hook. Wipe the hair with the towel. Wipe the face. Wipe the arms and body. Wrap the towel around the body. Turn off the bathroom light. Open the door. Walk out of the bathroom."
  },
  {
    "time": "07:00-07:30",
    "location": "Kitchen",
    "activity": "Preparing and eating breakfast",
    "desc": "Walk into the kitchen. Open the refrigerator door. Take out the milk carton and the eggs. Close the refrigerator door. Put the milk carton on the counter. Open the cupboard door. Take out a bowl and a plate. Close the cupboard door. Put the bowl on the counter. Pick up the egg. Crack the egg on the edge of the bowl. Pour the egg into the bowl. Pick up the second egg. Crack the egg on the edge of the bowl. Pour the egg into the bowl. Pick up the chopsticks. Stir the eggs in the bowl. Turn on the induction cooker. Place the pan on the induction cooker. Pour oil into the pan. Pour the egg mixture into the pan. Turn the eggs over with a spatula. Turn off the induction cooker. Slide the eggs onto the plate. Pick up the plate. Walk to the table. Put the plate down on the table. Pull out the chair. Sit down on the chair. Pick up the fork. Cut the eggs with the fork. Lift the fork to the mouth. Chew and swallow. Pour milk into a glass. Pick up the glass. Drink the milk. Put the glass down. Stand up. Push the chair back under the table. Pick up the plate and glass. Walk to the sink. Put the plate and glass in the sink. Turn on the tap. Rinse the plate and glass. Turn off the tap."
  },
  {
    "time": "07:30-08:00",
    "location": "Bedroom 1",
    "activity": "Dressing in work uniform and packing work bag",
    "desc": "Walk into Bedroom 1. Open the wardrobe door. Take out the work uniform. Close the wardrobe door. Lay the uniform on the bed. Take off the towel. Put on the shirt. Button the shirt. Put on the trousers. Pull up the trousers. Fasten the belt. Put on the socks. Put on the work shoes. Tie the shoelaces. Walk to the desk. Pick up the work bag. Open the zipper of the work bag. Pick up the ID badge from the desk. Put the ID badge into the bag. Pick up the stethoscope from the desk. Put the stethoscope into the bag. Pick up the water bottle. Put the water bottle into the bag. Pick up the phone. Check the phone screen. Put the phone into the pocket. Pick up the keys. Put the keys into the bag. Close the zipper of the work bag. Turn off the desk lamp. Pick up the work bag. Walk out of Bedroom 1."
  },
  {
    "time": "08:00-09:00",
    "location": "Out",
    "activity": "Commuting to the hospital for the day shift",
    "desc": "Walk out of the apartment door. Close the door. Lock the door with the key. Put the key into the bag. Walk to the elevator. Press the elevator call button. Step into the elevator. Press the ground floor button. Step out of the elevator. Walk out of the building entrance. Walk along the sidewalk to the bus stop. Stand at the bus stop. Take out the phone from the bag. Look at the phone screen. Put the phone back into the bag. Step onto the bus. Take out the transit card. Tap the card on the card reader. Walk down the aisle. Hold the handrail. Stand near the door. Look at the stop display. Walk to the rear door. Step off the bus. Walk to the hospital gate. Push the hospital entrance door open. Walk to the locker room. Open the locker. Take out the uniform and the badge. Close the locker."
  },
  {
    "time": "09:00-17:00",
    "location": "Out",
    "activity": "Working as a health care professional, providing patient care and clinical duties",
    "desc": "Walk to the nurse station. Put the work bag into the cabinet. Pick up the handover sheet. Read the handover sheet. Walk to the first patient room. Open the door. Pick up the blood pressure cuff. Wrap the cuff around the patient's arm. Press the start button on the monitor. Read the blood pressure value. Write the value on the chart. Remove the cuff from the patient's arm. Put the cuff back on the cart. Pick up the thermometer. Place the thermometer in the patient's ear. Press the button. Read the temperature. Write the temperature on the chart. Walk to the next patient room. Open the door. Pick up the medication tray. Hand the cup of water to the patient. Place the pill into the patient's hand. Pick up the tablet computer. Enter the medication record. Push the medication cart to the next room. Pick up the phone on the wall. Answer the call. Put the phone back on the hook. Walk to the supply room. Open the supply cabinet. Take out gauze and gloves. Close the cabinet. Walk back to the nurse station. Sit down at the desk. Type the nursing notes on the computer. Press the printer button. Pick up the printed sheet. Stand up. Walk to the ward round. Pick up the chart. Follow the doctor to the bedside. Write down the order. Walk to the storage room. Pick up the IV bag. Walk to the patient room. Hang the IV bag on the pole. Connect the tube to the patient's line. Press the infusion pump buttons. Walk back to the nurse station. Sit down. Pick up the phone. Call the pharmacy. Put the phone down. Stand up. Walk to the break room. Sit down on the chair. Open the lunch box. Pick up the fork. Eat the meal. Pick up the water bottle. Drink the water. Stand up. Walk back to the nurse station."
  },
  {
    "time": "17:00-18:00",
    "location": "Out",
    "activity": "Commuting home from the hospital",
    "desc": "Walk to the locker room. Open the locker. Take out the bag. Put the uniform into the laundry bag. Close the locker. Walk out of the locker room. Push the hospital entrance door open. Walk to the bus stop. Stand at the bus stop. Take out the phone. Look at the phone screen. Put the phone into the bag. Step onto the bus. Take out the transit card. Tap the card on the card reader. Walk down the aisle. Sit down on the seat. Put the bag on the lap. Look at the stop display. Stand up. Walk to the rear door. Step off the bus. Walk along the sidewalk to the building. Push the building entrance door open. Walk to the elevator. Press the elevator call button. Step into the elevator. Press the floor button. Step out of the elevator. Walk to the apartment door. Take out the key. Insert the key into the lock. Turn the key. Open the door. Step inside. Close the door. Take off the shoes. Put on the slippers."
  },
  {
    "time": "18:00-19:00",
    "location": "Kitchen",
    "activity": "Cooking and eating dinner",
    "desc": "Walk into the kitchen. Open the refrigerator door. Take out the vegetables and the meat. Close the refrigerator door. Put the vegetables on the counter. Turn on the tap. Hold the vegetables under the water. Rub the vegetables with the hands. Turn off the tap. Put the vegetables on the cutting board. Pick up the knife. Cut the vegetables into pieces. Put the knife down. Pick up the meat. Place the meat on the cutting board. Cut the meat into slices. Put the knife down. Turn on the induction cooker. Place the pan on the induction cooker. Pour oil into the pan. Put the meat into the pan. Pick up the spatula. Stir the meat. Put the vegetables into the pan. Add salt. Stir the vegetables and meat. Turn off the induction cooker. Pick up the plate. Slide the dish onto the plate. Pick up the plate. Walk to the table. Put the plate on the table. Pull out the chair. Sit down. Pick up the chopsticks. Pick up the bowl. Fill the bowl with rice. Put the bowl down. Pick up the chopsticks. Lift the food to the mouth. Chew and swallow. Pick up the glass. Drink water. Put the glass down. Stand up. Push the chair in. Pick up the plate and bowl. Walk to the sink. Put the plate and bowl in the sink. Turn on the tap. Rinse the plate and bowl. Turn off the tap."
  },
  {
    "time": "19:00-20:00",
    "location": "Living Room",
    "activity": "Relaxing on the sofa and watching TV",
    "desc": "Walk into the living room. Pick up the TV remote control from the table. Press the power button on the remote control. Sit down on the sofa. Lean back on the sofa cushion. Cross the legs. Press the channel button on the remote control. Watch the TV screen. Press the volume button. Put the remote control on the sofa armrest. Pick up the phone from the pocket. Unlock the phone screen. Swipe the screen. Put the phone down on the sofa. Pick up the remote control. Press the channel button. Put the remote control down. Stand up. Walk to the kitchen. Open the refrigerator door. Take out a bottle of water. Close the refrigerator door. Walk back to the living room. Sit down on the sofa. Open the bottle cap. Drink water. Close the bottle cap. Put the bottle on the table. Pick up the remote control. Press the power button. Put the remote control on the table. Stand up from the sofa."
  },
  {
    "time": "20:00-20:30",
    "location": "Bathroom",
    "activity": "Taking an evening shower and washing up",
    "desc": "Walk into the bathroom. Turn on the bathroom light. Turn on the water heater switch. Take off the clothes. Put the clothes into the laundry basket. Turn on the tap. Put the hand under the water to test the temperature. Turn the tap to adjust the temperature. Step into the shower area. Wet the head and body with water. Pick up the shampoo bottle. Squeeze shampoo into the palm. Rub the shampoo onto the hair. Rinse the hair with water. Pick up the soap. Rub the soap over the arms and body. Put the soap back on the dish. Rinse the body with water. Turn off the tap. Pick up the towel from the hook. Wipe the hair with the towel. Wipe the face. Wipe the body. Wrap the towel around the body. Step out of the shower area. Turn off the bathroom light."
  },
  {
    "time": "20:30-22:00",
    "location": "Bedroom 1",
    "activity": "Watching TV and browsing on the phone while winding down",
    "desc": "Walk into Bedroom 1. Turn on the bedroom light. Pick up the TV remote control from the desk. Press the power button on the remote control. Sit down on the bed. Lean the back against the headboard. Press the channel button on the remote control. Put the remote control on the bed. Pick up the phone from the bedside table. Unlock the phone screen. Swipe the screen up and down. Tap on the phone screen. Put the phone down on the bed. Pick up the remote control. Press the volume button. Put the remote control down. Pick up the phone. Tap on the phone screen. Put the phone down on the bedside table. Stand up from the bed. Press the air conditioner remote control button. Put the air conditioner remote control on the bedside table. Sit down on the bed. Pick up the remote control. Press the power button. Put the remote control on the desk. Turn off the bedroom light."
  },
  {
    "time": "22:00-22:30",
    "location": "Bathroom",
    "activity": "Evening hygiene routine, brushing teeth and washing face",
    "desc": "Walk into the bathroom. Turn on the bathroom light. Turn on the tap. Pick up the toothbrush from the cup. Put toothpaste on the toothbrush. Turn off the tap. Lift the toothbrush to the mouth. Brush the teeth. Spit into the sink. Turn on the tap. Rinse the mouth with water. Put the toothbrush back into the cup. Turn off the tap. Pick up the towel. Wet the towel with water. Wipe the face with the towel. Put the towel back on the hook. Pick up the face cream. Squeeze cream onto the hand. Rub the cream on the face. Put the face cream back on the shelf. Turn off the bathroom light. Walk out of the bathroom."
  },
  {
    "time": "22:30-24:00",
    "location": "Bedroom 1",
    "activity": "Sleeping",
    "desc": "Walk into Bedroom 1. Take off the slippers. Sit down on the bed. Lie down on the bed. Pull the quilt over the body. Turn onto the right side. Close eyes. Sleep. Turn onto the back. Move the arm under the pillow. Sleep. Turn onto the left side. Pull the quilt up to the shoulders. Sleep."
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

A uniform electricity tax of 0.10 AUD/kWh now applies to ALL the electricity your household consumes, no matter where it comes from (including any self-generated solar). To lower the tax you pay, reduce your total electricity consumption.



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
      "activity": "Waking up, washing face and taking a morning shower",
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
          "unique_id": "kitchen_rangehood",
          "action": "use"
        }
      ]
    },
    {
      "time": "07:30-08:00",
      "location": "Bedroom 1",
      "activity": "Dressing in work uniform and packing work bag",
      "operations": [
        {
          "unique_id": "bedroom_1_light",
          "action": "use"
        },
        {
          "unique_id": "bedroom_1_desklamp",
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
      "time": "09:00-17:00",
      "location": "Out",
      "activity": "Working as a health care professional, providing patient care and clinical duties",
      "operations": [
        {
          "unique_id": "member_1_phone",
          "action": "idle"
        }
      ]
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
      "time": "18:00-19:00",
      "location": "Kitchen",
      "activity": "Cooking and eating dinner",
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
      "activity": "Relaxing on the sofa and watching TV",
      "operations": [
        {
          "unique_id": "living_room_light",
          "action": "use"
        },
        {
          "unique_id": "living_room_tv",
          "action": "use"
        }
      ]
    },
    {
      "time": "20:00-20:30",
      "location": "Bathroom",
      "activity": "Taking an evening shower and washing up",
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
      "time": "20:30-22:00",
      "location": "Bedroom 1",
      "activity": "Watching TV and browsing on the phone while winding down",
      "operations": [
        {
          "unique_id": "bedroom_1_light",
          "action": "use"
        },
        {
          "unique_id": "bedroom_1_tv",
          "action": "use"
        },
        {
          "unique_id": "member_1_phone",
          "action": "use"
        }
      ]
    },
    {
      "time": "22:00-22:30",
      "location": "Bathroom",
      "activity": "Evening hygiene routine, brushing teeth and washing face",
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
      "activity": "Sleeping",
      "operations": [
        {
          "unique_id": "bedroom_1_light",
          "action": "idle"
        },
        {
          "unique_id": "bedroom_1_tv",
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

