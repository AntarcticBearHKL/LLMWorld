# s4_appliance_decision  (attempt 1)

## 对话信息

- time: 2026-09-11 03:17:10
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
- Age: 42
- Occupation: Community health worker (hybrid role)
- Habits: {}

This member's complete timeline:
[
  {
    "time": "00:00-06:30",
    "location": "Bedroom 1",
    "activity": "Sleeping",
    "desc": "Lies down in bed. Pulls blanket over body. Closes eyes. Breathes slowly. Turns to left side. Adjusts pillow. Turns to right side. Moves arm under pillow. Remains still. Breathes deeply. Turns again. Stretches leg. Curls up. Remains asleep."
  },
  {
    "time": "06:30-07:00",
    "location": "Bathroom",
    "activity": "Waking up, washing face and brushing teeth",
    "desc": "Turns on bathroom light. Turns on tap. Wets hands. Picks up soap. Rubs hands together. Applies soap to face. Rinses face. Turns off tap. Picks up toothbrush. Applies toothpaste. Brushes teeth. Rinses mouth. Turns off tap. Wipes face with towel. Turns off light."
  },
  {
    "time": "07:00-07:30",
    "location": "Kitchen",
    "activity": "Making and eating breakfast",
    "desc": "Enters kitchen. Turns on kitchen light. Opens refrigerator. Takes out eggs, milk, bread. Closes refrigerator. Cracks eggs into bowl. Whisk eggs. Turns on stove. Pours eggs into pan. Cooks eggs. Turns off stove. Places eggs on plate. Toasts bread. Pours milk into glass. Sits at table. Eats breakfast. Drinks milk. Picks up plate. Puts plate in sink."
  },
  {
    "time": "07:30-08:00",
    "location": "Bedroom 1",
    "activity": "Getting dressed and checking the day's client visit list on phone",
    "desc": "Walks to bedroom. Opens wardrobe. Takes out shirt. Takes out pants. Closes wardrobe. Takes off pajamas. Puts on shirt. Puts on pants. Puts on socks. Puts on shoes. Picks up phone. Unlocks phone. Opens calendar app. Scrolls through list. Reads client names. Checks addresses. Puts phone in pocket. Picks up bag."
  },
  {
    "time": "08:00-08:45",
    "location": "Out",
    "activity": "Commuting to the community health centre",
    "desc": "Walks out of house. Locks door. Walks to bus stop. Waits for bus. Boards bus. Pays fare. Finds seat. Sits down. Looks out window. Checks phone. Gets off bus. Walks to health centre. Enters building."
  },
  {
    "time": "08:45-12:00",
    "location": "Out",
    "activity": "Conducting community health outreach visits and health checks for residents",
    "desc": "Arrives at first client's home. Knocks on door. Greets client: 'Hello, how are you feeling today?' Enters home. Asks about health. Measures blood pressure. Checks temperature. Listens to lungs. Records notes. Advises on medication. Says goodbye. Walks to next client. Knocks on door. Enters. Greets. Measures blood pressure. Records. Checks medication. Advises. Leaves."
  },
  {
    "time": "12:00-12:45",
    "location": "Out",
    "activity": "Taking a lunch break near the health centre",
    "desc": "Walks to cafe. Enters cafe. Orders food. Pays. Waits. Receives food. Finds table. Sits down. Unwraps sandwich. Takes bite. Chews. Swallows. Drinks water. Wipes mouth. Throws trash. Stands up. Walks back to health centre."
  },
  {
    "time": "12:45-16:30",
    "location": "Out",
    "activity": "Continuing home visits and follow-up consultations with clients",
    "desc": "Knocks on door. Enters. Greets. Asks about symptoms. Measures blood pressure. Checks wound. Changes bandage. Records notes. Advises on diet. Schedules next visit. Says goodbye. Walks to next client. Knocks on door. Enters. Greets. Measures blood pressure. Records. Checks medication. Advises. Leaves."
  },
  {
    "time": "16:30-17:15",
    "location": "Out",
    "activity": "Commuting back home",
    "desc": "Walks to bus stop. Waits. Boards bus. Pays. Sits. Checks phone. Gets off bus. Walks home. Unlocks door. Enters. Closes door. Locks door."
  },
  {
    "time": "17:15-18:00",
    "location": "Bedroom 1",
    "activity": "Changing into comfortable clothes and logging case notes on computer",
    "desc": "Walks to bedroom. Takes off shoes. Takes off work clothes. Puts on t-shirt. Puts on sweatpants. Walks to desk. Turns on computer. Waits for boot. Opens case notes file. Types notes. Saves file. Closes computer. Stands up."
  },
  {
    "time": "18:00-19:00",
    "location": "Kitchen",
    "activity": "Cooking and eating dinner",
    "desc": "Enters kitchen. Turns on light. Opens refrigerator. Takes out vegetables. Closes refrigerator. Washes vegetables. Cuts vegetables. Turns on stove. Places pan on stove. Adds oil. Adds vegetables. Stirs. Adds spices. Turns off stove. Places food on plate. Sits at table. Eats. Drinks water. Picks up plate. Puts in sink."
  },
  {
    "time": "19:00-19:30",
    "location": "Bathroom",
    "activity": "Taking an evening shower",
    "desc": "Enters bathroom. Turns on light. Takes off clothes. Turns on shower. Steps into shower. Washes body. Washes hair. Rinses. Turns off shower. Steps out. Picks up towel. Dries body. Dries hair. Puts on clean clothes. Turns off light. Walks out."
  },
  {
    "time": "19:30-20:30",
    "location": "Bedroom 1",
    "activity": "Reviewing client files and planning tomorrow's schedule on computer",
    "desc": "Walks to bedroom. Sits at desk. Turns on computer. Opens client files. Reads. Takes notes. Opens calendar. Schedules appointments. Checks email. Closes files. Turns off computer. Stands up."
  },
  {
    "time": "20:30-21:30",
    "location": "Living Room",
    "activity": "Watching TV and relaxing",
    "desc": "Walks to living room. Turns on TV. Picks up remote. Sits on couch. Changes channel. Watches TV. Adjusts volume. Changes channel again. Watches more. Picks up phone. Checks phone. Puts phone down. Stretches. Yawns. Turns off TV. Stands up."
  },
  {
    "time": "21:30-22:00",
    "location": "Kitchen",
    "activity": "Making a warm drink and preparing items for the next day",
    "desc": "Walks to kitchen. Turns on light. Opens cabinet. Takes out mug. Closes cabinet. Opens refrigerator. Takes out milk. Closes refrigerator. Pours milk into mug. Places mug in microwave. Turns on microwave. Takes out mug. Stirs. Drinks. Washes mug. Puts mug in rack. Turns off light. Walks to bedroom. Prepares clothes for next day. Packs bag."
  },
  {
    "time": "22:00-22:30",
    "location": "Bathroom",
    "activity": "Evening hygiene routine before bed",
    "desc": "Enters bathroom. Turns on light. Uses toilet. Flushes. Washes hands. Turns on tap. Wets toothbrush. Applies toothpaste. Brushes teeth. Rinses mouth. Washes face. Dries face. Turns off tap. Turns off light. Walks to bedroom."
  },
  {
    "time": "22:30-24:00",
    "location": "Bedroom 1",
    "activity": "Reading on phone briefly and sleeping",
    "desc": "Lies down on bed. Picks up phone. Unlocks phone. Opens reading app. Scrolls. Reads. Turns page. Reads more. Puts phone on nightstand. Turns off lamp. Closes eyes. Turns to side. Pulls blanket. Breathes slowly. Falls asleep."
  }
]

Household structure and appliances:
{
  "Bedroom 1": {
    "appliances": [
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
      }
    ]
  },
  "Bedroom 2": {
    "appliances": [
      {
        "unique_id": "bedroom_2_light",
        "name": "Light",
        "type": "on_demand",
        "power_watts": 40,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
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
        "unique_id": "bedroom_2_monitor",
        "name": "Monitor",
        "type": "on_demand",
        "power_watts": 30,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "bedroom_2_fan",
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
  "Bedroom 3": {
    "appliances": [
      {
        "unique_id": "bedroom_3_light",
        "name": "Light",
        "type": "on_demand",
        "power_watts": 40,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "bedroom_3_computer",
        "name": "Computer",
        "type": "on_demand",
        "power_watts": 200,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      }
    ]
  },
  "Bedroom 4": {
    "appliances": [
      {
        "unique_id": "bedroom_4_light",
        "name": "Light",
        "type": "on_demand",
        "power_watts": 40,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "bedroom_4_spaceheater",
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
  "Bedroom 5": {
    "appliances": [
      {
        "unique_id": "bedroom_5_light",
        "name": "Light",
        "type": "on_demand",
        "power_watts": 40,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "bedroom_5_fan",
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
        "unique_id": "kitchen_light",
        "name": "Light",
        "type": "on_demand",
        "power_watts": 40,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
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
        "unique_id": "kitchen_ricecooker",
        "name": "RiceCooker",
        "type": "cycle",
        "power_watts": 800,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual",
        "energy_per_cycle_kwh": 0.25,
        "cycle_minutes": 40
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
        "unique_id": "kitchen_freezer",
        "name": "Freezer",
        "type": "always_on",
        "power_watts": 100,
        "standby_watts": 0,
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
        "unique_id": "kitchen_washingmachine",
        "name": "WashingMachine",
        "type": "cycle",
        "power_watts": 500,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": true,
        "season": "annual",
        "energy_per_cycle_kwh": 0.6,
        "cycle_minutes": 90
      }
    ]
  },
  "Bathroom": {
    "appliances": [
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
        "unique_id": "bathroom_fan",
        "name": "Fan",
        "type": "on_demand",
        "power_watts": 60,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "cooling"
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
      }
    ]
  },
  "Living Room": {
    "appliances": [
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
        "power_watts": 200,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      }
    ]
  },
  "Member 2 personal appliances": {
    "appliances": [
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
        "unique_id": "member_2_computer",
        "name": "Computer",
        "type": "on_demand",
        "power_watts": 200,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      }
    ]
  },
  "Member 3 personal appliances": {
    "appliances": [
      {
        "unique_id": "member_3_desklamp",
        "name": "DeskLamp",
        "type": "on_demand",
        "power_watts": 15,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "member_3_phone",
        "name": "Phone",
        "type": "charging",
        "power_watts": 20,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": true,
        "season": "annual"
      },
      {
        "unique_id": "member_3_fan",
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
  "Member 4 personal appliances": {
    "appliances": [
      {
        "unique_id": "member_4_computer",
        "name": "Computer",
        "type": "on_demand",
        "power_watts": 200,
        "standby_watts": 1,
        "duty_cycle": 1.0,
        "flexible": false,
        "season": "annual"
      },
      {
        "unique_id": "member_4_phone",
        "name": "Phone",
        "type": "charging",
        "power_watts": 20,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": true,
        "season": "annual"
      },
      {
        "unique_id": "member_4_desklamp",
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
  "Member 5 personal appliances": {
    "appliances": [
      {
        "unique_id": "member_5_phone",
        "name": "Phone",
        "type": "charging",
        "power_watts": 20,
        "standby_watts": 0,
        "duty_cycle": 1.0,
        "flexible": true,
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

- bedroom_1_light
- bedroom_1_airconditioner
- bedroom_1_desklamp
- bedroom_2_light
- bedroom_2_desklamp
- bedroom_2_monitor
- bedroom_2_fan
- bedroom_3_light
- bedroom_3_computer
- bedroom_4_light
- bedroom_4_spaceheater
- bedroom_5_light
- bedroom_5_fan
- kitchen_light
- kitchen_ricecooker
- kitchen_microwave
- kitchen_inductioncooker
- kitchen_rangehood
- kitchen_kettle
- kitchen_toaster
- kitchen_oven
- kitchen_dishwasher
- kitchen_washingmachine
- bathroom_light
- bathroom_waterheater
- bathroom_fan
- bathroom_dehumidifier
- bathroom_clothesdryer
- living_room_light
- living_room_tv
- living_room_airconditioner
- living_room_gameconsole
- living_room_vacuumcleaner
- member_1_phone
- member_1_computer
- member_2_phone
- member_2_computer
- member_3_desklamp
- member_3_phone
- member_3_fan
- member_4_computer
- member_4_phone
- member_4_desklamp
- member_5_phone

Always-on appliances (do NOT create operations for these):
- kitchen_refrigerator
- kitchen_freezer
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
{"member": "Member 1", "appliance_decisions": [{"time": "00:00-06:30", "location": "Bedroom 1", "activity": "Sleeping", "operations": [{"unique_id": "bedroom_1_light", "action": "idle"}, {"unique_id": "bedroom_1_airconditioner", "action": "idle"}, {"unique_id": "bedroom_1_desklamp", "action": "idle"}, {"unique_id": "member_1_phone", "action": "idle"}]}, {"time": "06:30-07:00", "location": "Bathroom", "activity": "Waking up, washing face and brushing teeth", "operations": [{"unique_id": "bathroom_light", "action": "use"}, {"unique_id": "bathroom_fan", "action": "idle"}, {"unique_id": "bathroom_waterheater", "action": "idle"}, {"unique_id": "bathroom_dehumidifier", "action": "idle"}]}, {"time": "07:00-07:30", "location": "Kitchen", "activity": "Making and eating breakfast", "operations": [{"unique_id": "kitchen_light", "action": "use"}, {"unique_id": "kitchen_inductioncooker", "action": "use"}, {"unique_id": "kitchen_rangehood", "action": "use"}, {"unique_id": "kitchen_toaster", "action": "use"}, {"unique_id": "kitchen_microwave", "action": "idle"}, {"unique_id": "kitchen_kettle", "action": "idle"}, {"unique_id": "kitchen_oven", "action": "idle"}, {"unique_id": "kitchen_ricecooker", "action": "idle"}, {"unique_id": "kitchen_dishwasher", "action": "idle"}, {"unique_id": "kitchen_washingmachine", "action": "idle"}]}, {"time": "07:30-08:00", "location": "Bedroom 1", "activity": "Getting dressed and checking the day's client visit list on phone", "operations": [{"unique_id": "bedroom_1_light", "action": "use"}, {"unique_id": "bedroom_1_desklamp", "action": "idle"}, {"unique_id": "bedroom_1_airconditioner", "action": "idle"}, {"unique_id": "member_1_phone", "action": "use"}]}, {"time": "08:00-08:45", "location": "Out", "activity": "Commuting to the community health centre", "operations": [{"unique_id": "member_1_phone", "action": "use"}]}, {"time": "08:45-12:00", "location": "Out", "activity": "Conducting community health outreach visits and health checks for residents", "operations": [{"unique_id": "member_1_phone", "action": "use"}]}, {"time": "12:00-12:45", "location": "Out", "activity": "Taking a lunch break near the health centre", "operations": [{"unique_id": "member_1_phone", "action": "idle"}]}, {"time": "12:45-16:30", "location": "Out", "activity": "Continuing home visits and follow-up consultations with clients", "operations": [{"unique_id": "member_1_phone", "action": "use"}]}, {"time": "16:30-17:15", "location": "Out", "activity": "Commuting back home", "operations": [{"unique_id": "member_1_phone", "action": "use"}]}, {"time": "17:15-18:00", "location": "Bedroom 1", "activity": "Changing into comfortable clothes and logging case notes on computer", "operations": [{"unique_id": "bedroom_1_light", "action": "use"}, {"unique_id": "bedroom_1_desklamp", "action": "idle"}, {"unique_id": "bedroom_1_airconditioner", "action": "idle"}, {"unique_id": "member_1_computer", "action": "use"}]}, {"time": "18:00-19:00", "location": "Kitchen", "activity": "Cooking and eating dinner", "operations": [{"unique_id": "kitchen_light", "action": "use"}, {"unique_id": "kitchen_inductioncooker", "action": "use"}, {"unique_id": "kitchen_rangehood", "action": "use"}, {"unique_id": "kitchen_microwave", "action": "idle"}, {"unique_id": "kitchen_toaster", "action": "idle"}, {"unique_id": "kitchen_kettle", "action": "idle"}, {"unique_id": "kitchen_oven", "action": "idle"}, {"unique_id": "kitchen_ricecooker", "action": "idle"}, {"unique_id": "kitchen_dishwasher", "action": "idle"}, {"unique_id": "kitchen_washingmachine", "action": "idle"}]}, {"time": "19:00-19:30", "location": "Bathroom", "activity": "Taking an evening shower", "operations": [{"unique_id": "bathroom_light", "action": "use"}, {"unique_id": "bathroom_waterheater", "action": "use"}, {"unique_id": "bathroom_fan", "action": "idle"}, {"unique_id": "bathroom_dehumidifier", "action": "idle"}]}, {"time": "19:30-20:30", "location": "Bedroom 1", "activity": "Reviewing client files and planning tomorrow's schedule on computer", "operations": [{"unique_id": "bedroom_1_light", "action": "use"}, {"unique_id": "bedroom_1_desklamp", "action": "use"}, {"unique_id": "bedroom_1_airconditioner", "action": "idle"}, {"unique_id": "member_1_computer", "action": "use"}]}, {"time": "20:30-21:30", "location": "Living Room", "activity": "Watching TV and relaxing", "operations": [{"unique_id": "living_room_light", "action": "use"}, {"unique_id": "living_room_tv", "action": "use"}, {"unique_id": "living_room_airconditioner", "action": "idle"}, {"unique_id": "living_room_gameconsole", "action": "idle"}, {"unique_id": "living_room_vacuumcleaner", "action": "idle"}]}, {"time": "21:30-22:00", "location": "Kitchen", "activity": "Making a warm drink and preparing items for the next day", "operations": [{"unique_id": "kitchen_light", "action": "use"}, {"unique_id": "kitchen_microwave", "action": "use"}, {"unique_id": "kitchen_kettle", "action": "idle"}, {"unique_id": "kitchen_inductioncooker", "action": "idle"}, {"unique_id": "kitchen_rangehood", "action": "idle"}, {"unique_id": "kitchen_toaster", "action": "idle"}, {"unique_id": "kitchen_oven", "action": "idle"}, {"unique_id": "kitchen_ricecooker", "action": "idle"}, {"unique_id": "kitchen_dishwasher", "action": "idle"}, {"unique_id": "kitchen_washingmachine", "action": "idle"}]}, {"time": "22:00-22:30", "location": "Bathroom", "activity": "Evening hygiene routine before bed", "operations": [{"unique_id": "bathroom_light", "action": "use"}, {"unique_id": "bathroom_waterheater", "action": "idle"}, {"unique_id": "bathroom_fan", "action": "idle"}, {"unique_id": "bathroom_dehumidifier", "action": "idle"}]}, {"time": "22:30-24:00", "location": "Bedroom 1", "activity": "Reading on phone briefly and sleeping", "operations": [{"unique_id": "bedroom_1_light", "action": "use"}, {"unique_id": "bedroom_1_desklamp", "action": "idle"}, {"unique_id": "bedroom_1_airconditioner", "action": "idle"}, {"unique_id": "member_1_phone", "action": "charge_home"}]}]}
```

