# s4_appliance_decision  (attempt 1)

## 对话信息

- time: 2026-09-13 11:44:36
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
    "time": "00:00-07:45",
    "location": "Bedroom 1",
    "activity": "Sleeping",
    "desc": "Lie down on bed. Pull blanket over body. Close eyes. Breathe slowly. Turn to left side. Adjust pillow. Turn to right side. Pull blanket up. Move arm under pillow. Move leg. Remain still. Continue sleeping."
  },
  {
    "time": "07:45-08:15",
    "location": "Bathroom",
    "activity": "Waking up, washing face and taking a morning shower",
    "desc": "Open eyes. Sit up in bed. Swing legs over side. Stand up. Walk to bathroom. Turn on light. Turn on shower. Adjust water temperature. Step into shower. Wet body. Apply soap. Rinse body. Turn off shower. Step out of shower. Pick up towel. Dry body. Dry hair. Wrap towel around body. Walk to sink. Turn on tap. Wet face. Apply face wash. Rub face. Rinse face. Turn off tap. Pick up hand towel. Dry face. Turn off light. Walk out of bathroom."
  },
  {
    "time": "08:15-08:45",
    "location": "Kitchen",
    "activity": "Making and eating breakfast with coffee using the kettle and toaster",
    "desc": "Enter kitchen. Turn on light. Open refrigerator. Take out bread, eggs, butter, milk. Close refrigerator. Open cupboard. Take out plate, mug, bowl. Close cupboard. Place bread in toaster. Press lever down. Plug in kettle. Fill kettle with water. Turn on kettle. Crack eggs into bowl. Whisk eggs. Place pan on stove. Turn on stove. Add butter to pan. Pour eggs into pan. Stir eggs. Turn off stove. Place scrambled eggs on plate. Toast pops up. Remove toast from toaster. Butter toast. Pour coffee into mug. Add milk. Sit at table. Pick up fork. Eat eggs. Pick up toast. Bite toast. Drink coffee. Finish meal. Pick up plate and mug. Walk to sink. Place dishes in sink."
  },
  {
    "time": "08:45-09:30",
    "location": "Living Room",
    "activity": "Relaxing on the sofa, checking news and messages on the computer",
    "desc": "Walk to living room. Sit on sofa. Open laptop. Press power button. Wait for computer to boot. Type password. Press enter. Open web browser. Type news website address. Press enter. Scroll through headlines. Click on article. Read article. Scroll down. Close article. Open messaging application. Click on conversation. Type reply. Press send. Read new messages. Type another reply. Press send. Close messaging application. Open email. Read emails. Delete spam. Close email. Close web browser. Close laptop."
  },
  {
    "time": "09:30-10:15",
    "location": "Bathroom",
    "activity": "Sorting laundry and running the washing machine",
    "desc": "Walk to bathroom. Open laundry hamper. Take out clothes. Sort clothes into whites and colors. Pick up whites. Walk to washing machine. Open washing machine door. Place whites into drum. Close door. Open detergent drawer. Pour detergent into compartment. Close drawer. Turn cycle selector to white wash. Press start button. Pick up colors. Wait for wash cycle to finish. Open washing machine door. Remove whites. Place whites into dryer. Close dryer door. Press start button on dryer. Walk out of bathroom."
  },
  {
    "time": "10:15-11:00",
    "location": "Living Room",
    "activity": "Vacuuming and tidying up the living room",
    "desc": "Walk to living room. Pick up vacuum cleaner. Plug cord into outlet. Turn on vacuum. Push vacuum across floor. Vacuum under coffee table. Move sofa. Vacuum under sofa. Move sofa back. Vacuum corners. Turn off vacuum. Unplug cord. Wind cord around vacuum. Put vacuum in closet. Pick up items on coffee table. Place magazines in rack. Place remote control on shelf. Fluff pillows on sofa. Fold blanket. Place blanket on sofa. Pick up trash. Throw trash in bin. Walk out of living room."
  },
  {
    "time": "11:00-12:00",
    "location": "Kitchen",
    "activity": "Preparing and cooking lunch at home",
    "desc": "Enter kitchen. Open refrigerator. Take out vegetables, chicken, spices. Close refrigerator. Place vegetables on cutting board. Wash vegetables. Chop vegetables. Cut chicken into pieces. Heat pan on stove. Add oil. Add chicken. Stir chicken. Add vegetables. Stir vegetables. Add spices. Stir. Cover pan. Reduce heat. Simmer. Open cupboard. Take out plate. Close cupboard. Turn off stove. Place food on plate. Walk to table. Sit down. Pick up fork. Eat lunch. Drink water. Finish meal. Pick up plate. Walk to sink. Place plate in sink. Wash hands."
  },
  {
    "time": "12:00-12:45",
    "location": "Kitchen",
    "activity": "Eating lunch",
    "desc": "Sit at table. Pick up fork. Take bite of food. Chew. Swallow. Pick up glass. Drink water. Put down glass. Take another bite. Chew. Swallow. Pick up napkin. Wipe mouth. Continue eating. Finish food. Push plate away. Stand up. Pick up plate. Walk to sink. Place plate in sink. Pick up glass. Place glass in sink. Walk out of kitchen."
  },
  {
    "time": "12:45-13:30",
    "location": "Bedroom 1",
    "activity": "Resting and watching TV in bed",
    "desc": "Walk to bedroom. Lie down on bed. Pull blanket over legs. Pick up remote control. Press power button. Turn on TV. Browse channels. Stop on news channel. Watch TV. Adjust pillow. Turn to side. Watch TV. Change channel. Watch movie. Turn off TV. Put down remote. Close eyes. Rest."
  },
  {
    "time": "13:30-15:30",
    "location": "Out",
    "activity": "Grocery shopping and running personal errands",
    "desc": "Put on shoes. Pick up keys. Pick up wallet. Walk to door. Open door. Step out. Lock door. Walk to car. Unlock car. Open car door. Sit in driver seat. Close door. Fasten seatbelt. Insert key. Start engine. Drive to grocery store. Park car. Turn off engine. Unfasten seatbelt. Open door. Step out. Close door. Lock car. Walk to store entrance. Pick up shopping cart. Push cart through aisles. Pick up vegetables. Place in cart. Pick up milk. Place in cart. Pick up bread. Place in cart. Push cart to checkout. Unload items onto conveyor belt. Pay cashier. Place items in bags. Put bags in cart. Push cart to car. Unload bags into trunk. Return cart. Get in car. Fasten seatbelt. Start engine. Drive to post office. Park car. Get out. Walk to post office. Mail package. Return to car. Drive home. Park car. Turn off engine. Get out. Lock car. Carry bags to door. Unlock door. Enter home. Close door. Put bags on kitchen counter."
  },
  {
    "time": "15:30-16:30",
    "location": "Living Room",
    "activity": "Leisure time browsing on the computer and listening to music",
    "desc": "Walk to living room. Sit on sofa. Open laptop. Press power button. Wait for boot. Enter password. Open music player. Select playlist. Press play. Open web browser. Type social media address. Scroll through feed. Like posts. Comment on post. Open video site. Watch video. Pause video. Open news site. Read article. Close browser. Close music player. Close laptop. Stand up. Walk out of living room."
  },
  {
    "time": "16:30-17:30",
    "location": "Out",
    "activity": "Brisk walk and light exercise in the park",
    "desc": "Put on shoes. Pick up keys. Walk out of house. Lock door. Walk to park. Enter park. Start walking briskly. Swing arms. Breathe deeply. Walk around path. Pass bench. Continue walking. Stop at exercise area. Do arm stretches. Do leg stretches. Do squats. Do lunges. Do push-ups against bench. Rest. Walk back home. Unlock door. Enter home. Close door. Remove shoes."
  },
  {
    "time": "17:30-18:15",
    "location": "Bathroom",
    "activity": "Showering after exercise",
    "desc": "Walk to bathroom. Turn on light. Turn on shower. Adjust water temperature. Step into shower. Wet body. Apply soap. Rinse body. Wash hair. Rinse hair. Turn off shower. Step out. Pick up towel. Dry body. Dry hair. Wrap towel around body. Walk to sink. Turn on tap. Wash face. Turn off tap. Dry face. Turn off light. Walk out of bathroom."
  },
  {
    "time": "18:15-19:00",
    "location": "Kitchen",
    "activity": "Cooking dinner using the induction cooker and oven",
    "desc": "Enter kitchen. Turn on light. Open refrigerator. Take out fish, vegetables, spices. Close refrigerator. Preheat oven to 200 degrees. Wash vegetables. Chop vegetables. Season fish. Place fish on baking tray. Put tray in oven. Set timer. Place pan on induction cooker. Turn on induction cooker. Add oil. Add vegetables. Stir vegetables. Add spices. Stir. Cover pan. Simmer. Check oven timer. Remove fish from oven. Place fish on plate. Turn off induction cooker. Place vegetables on plate. Walk to table. Sit down. Eat dinner. Drink water. Finish meal. Pick up plate. Walk to sink. Place plate in sink."
  },
  {
    "time": "19:00-20:00",
    "location": "Kitchen",
    "activity": "Eating dinner",
    "desc": "Sit at table. Pick up fork. Cut fish. Take bite. Chew. Swallow. Pick up glass. Drink water. Put down glass. Take another bite. Chew. Swallow. Pick up napkin. Wipe mouth. Continue eating. Finish food. Push plate away. Stand up. Pick up plate. Walk to sink. Place plate in sink. Pick up glass. Place glass in sink. Walk out of kitchen."
  },
  {
    "time": "20:00-22:00",
    "location": "Living Room",
    "activity": "Watching TV and playing video games for evening relaxation",
    "desc": "Walk to living room. Sit on sofa. Pick up remote control. Press power button. Turn on TV. Browse channels. Select movie. Watch TV. Pick up game controller. Press power button on console. Select game. Start game. Play game. Pause game. Watch TV. Resume game. Play game. Finish game. Turn off console. Put down controller. Watch TV. Turn off TV. Put down remote. Stand up. Walk out of living room."
  },
  {
    "time": "22:00-22:45",
    "location": "Bedroom 1",
    "activity": "Winding down, using phone and watching TV",
    "desc": "Walk to bedroom. Lie down on bed. Pull blanket over legs. Pick up phone. Unlock phone. Scroll through social media. Open messaging app. Type message. Send message. Read reply. Type reply. Send reply. Put down phone. Pick up remote control. Press power button. Turn on TV. Browse channels. Select show. Watch TV. Adjust pillow. Turn to side. Watch TV. Turn off TV. Put down remote. Pick up phone. Scroll through news. Put down phone. Close eyes."
  },
  {
    "time": "22:45-23:15",
    "location": "Bathroom",
    "activity": "Night-time hygiene routine, brushing teeth and washing",
    "desc": "Walk to bathroom. Turn on light. Pick up toothbrush. Apply toothpaste. Turn on tap. Wet toothbrush. Brush teeth. Rinse mouth. Spit in sink. Turn off tap. Pick up cup. Fill with water. Rinse mouth. Spit. Put down cup. Pick up face wash. Apply to face. Rub face. Rinse face. Turn off tap. Pick up towel. Dry face. Turn off light. Walk out of bathroom."
  },
  {
    "time": "23:15-24:00",
    "location": "Bedroom 1",
    "activity": "Reading briefly and sleeping",
    "desc": "Walk to bedroom. Lie down on bed. Pick up book from nightstand. Open book to bookmark. Read page. Turn page. Read page. Close book. Place book on nightstand. Turn off bedside lamp. Pull blanket over body. Close eyes. Breathe slowly. Turn to side. Adjust pillow. Remain still. Sleep."
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

Today your household is on a time-of-use (TOU) electricity tariff: peak period 16:00-21:00 at 0.90 AUD/kWh; valley period 22:00-07:00 at 0.18 AUD/kWh; shoulder period (all other times) at 0.35 AUD/kWh. To reduce your bill, shift flexible appliances (electric vehicle charging, washing machine, dishwasher-free routines like hot water use) into the valley period, and avoid running high-power appliances during the peak period unless necessary.

Flexible-appliance costs under today's tariff (peak 16:00-21:00 @0.90 AUD/kWh; off-peak 22:00-07:00 @0.18 AUD/kWh):
- bedroom_1_airconditioner: 1.80 AUD now (peak) vs 0.36 AUD off-peak — save 1.44 per hour
- kitchen_dishwasher: 0.99 AUD now (peak) vs 0.20 AUD off-peak — save 0.79 per cycle
- bathroom_waterheater: 2.70 AUD now (peak) vs 0.54 AUD off-peak — save 2.16 per hour
- bathroom_washingmachine: 0.54 AUD now (peak) vs 0.11 AUD off-peak — save 0.43 per cycle
- bathroom_clothesdryer: 2.25 AUD now (peak) vs 0.45 AUD off-peak — save 1.80 per cycle
- member_1_phone: 0.02 AUD now (peak) vs 0.00 AUD off-peak — save 0.01 per hour
To minimise cost: if a flexible appliance would otherwise run in the peak window, you MAY move it to an off-peak segment earlier or later the same day (for example run the dishwasher overnight, or shower before 16:00) — the activity still happens, only its time changes. Keep it in the peak window only if the activity genuinely cannot move.





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
12. **Minimise cost (when a cost table is given)**: for every flexible appliance, compare its peak cost with its off-peak cost and schedule it at the cheapest feasible time; only run it in the peak window if the activity or comfort genuinely requires it.

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
      "time": "00:00-07:45",
      "location": "Bedroom 1",
      "activity": "Sleeping",
      "operations": [
        {"unique_id": "bedroom_1_tv", "action": "idle"},
        {"unique_id": "bedroom_1_light", "action": "idle"},
        {"unique_id": "bedroom_1_desklamp", "action": "idle"}
      ]
    },
    {
      "time": "07:45-08:15",
      "location": "Bathroom",
      "activity": "Waking up, washing face and taking a morning shower",
      "operations": [
        {"unique_id": "bathroom_light", "action": "use"},
        {"unique_id": "bathroom_waterheater", "action": "use"}
      ]
    },
    {
      "time": "08:15-08:45",
      "location": "Kitchen",
      "activity": "Making and eating breakfast with coffee using the kettle and toaster",
      "operations": [
        {"unique_id": "kitchen_light", "action": "use"},
        {"unique_id": "kitchen_kettle", "action": "use"},
        {"unique_id": "kitchen_toaster", "action": "use"},
        {"unique_id": "kitchen_inductioncooker", "action": "use"},
        {"unique_id": "kitchen_rangehood", "action": "use"}
      ]
    },
    {
      "time": "08:45-09:30",
      "location": "Living Room",
      "activity": "Relaxing on the sofa, checking news and messages on the computer",
      "operations": [
        {"unique_id": "living_room_computer", "action": "use"},
        {"unique_id": "living_room_monitor", "action": "use"},
        {"unique_id": "living_room_light", "action": "use"}
      ]
    },
    {
      "time": "09:30-10:15",
      "location": "Bathroom",
      "activity": "Sorting laundry and running the washing machine",
      "operations": [
        {"unique_id": "bathroom_light", "action": "use"},
        {"unique_id": "bathroom_washingmachine", "action": "run"},
        {"unique_id": "bathroom_clothesdryer", "action": "run"}
      ]
    },
    {
      "time": "10:15-11:00",
      "location": "Living Room",
      "activity": "Vacuuming and tidying up the living room",
      "operations": [
        {"unique_id": "living_room_vacuumcleaner", "action": "use"},
        {"unique_id": "living_room_light", "action": "use"}
      ]
    },
    {
      "time": "11:00-12:00",
      "location": "Kitchen",
      "activity": "Preparing and cooking lunch at home",
      "operations": [
        {"unique_id": "kitchen_light", "action": "use"},
        {"unique_id": "kitchen_inductioncooker", "action": "use"},
        {"unique_id": "kitchen_rangehood", "action": "use"}
      ]
    },
    {
      "time": "12:00-12:45",
      "location": "Kitchen",
      "activity": "Eating lunch",
      "operations": [
        {"unique_id": "kitchen_light", "action": "use"}
      ]
    },
    {
      "time": "12:45-13:30",
      "location": "Bedroom 1",
      "activity": "Resting and watching TV in bed",
      "operations": [
        {"unique_id": "bedroom_1_tv", "action": "use"},
        {"unique_id": "bedroom_1_light", "action": "use"}
      ]
    },
    {
      "time": "13:30-15:30",
      "location": "Out",
      "activity": "Grocery shopping and running personal errands",
      "operations": [
        {"unique_id": "member_1_phone", "action": "charge_external"}
      ]
    },
    {
      "time": "15:30-16:30",
      "location": "Living Room",
      "activity": "Leisure time browsing on the computer and listening to music",
      "operations": [
        {"unique_id": "living_room_computer", "action": "use"},
        {"unique_id": "living_room_monitor", "action": "use"},
        {"unique_id": "living_room_light", "action": "use"}
      ]
    },
    {
      "time": "16:30-17:30",
      "location": "Out",
      "activity": "Brisk walk and light exercise in the park",
      "operations": [
        {"unique_id": "member_1_phone", "action": "idle"}
      ]
    },
    {
      "time": "17:30-18:15",
      "location": "Bathroom",
      "activity": "Showering after exercise",
      "operations": [
        {"unique_id": "bathroom_light", "action": "use"},
        {"unique_id": "bathroom_waterheater", "action": "use"}
      ]
    },
    {
      "time": "18:15-19:00",
      "location": "Kitchen",
      "activity": "Cooking dinner using the induction cooker and oven",
      "operations": [
        {"unique_id": "kitchen_light", "action": "use"},
        {"unique_id": "kitchen_oven", "action": "run"},
        {"unique_id": "kitchen_inductioncooker", "action": "use"},
        {"unique_id": "kitchen_rangehood", "action": "use"}
      ]
    },
    {
      "time": "19:00-20:00",
      "location": "Kitchen",
      "activity": "Eating dinner",
      "operations": [
        {"unique_id": "kitchen_light", "action": "use"}
      ]
    },
    {
      "time": "20:00-22:00",
      "location": "Living Room",
      "activity": "Watching TV and playing video games for evening relaxation",
      "operations": [
        {"unique_id": "living_room_tv", "action": "use"},
        {"unique_id": "living_room_gameconsole", "action": "use"},
        {"unique_id": "living_room_light", "action": "use"}
      ]
    },
    {
      "time": "22:00-22:45",
      "location": "Bedroom 1",
      "activity": "Winding down, using phone and watching TV",
      "operations": [
        {"unique_id": "bedroom_1_tv", "action": "use"},
        {"unique_id": "bedroom_1_light", "action": "use"},
        {"unique_id": "member_1_phone", "action": "charge_home"}
      ]
    },
    {
      "time": "22:45-23:15",
      "location": "Bathroom",
      "activity": "Night-time hygiene routine, brushing teeth and washing",
      "operations": [
        {"unique_id": "bathroom_light", "action": "use"}
      ]
    },
    {
      "time": "23:15-24:00",
      "location": "Bedroom 1",
      "activity": "Reading briefly and sleeping",
      "operations": [
        {"unique_id": "bedroom_1_desklamp", "action": "use"},
        {"unique_id": "bedroom_1_tv", "action": "idle"},
        {"unique_id": "bedroom_1_light", "action": "idle"}
      ]
    }
  ]
}
```

