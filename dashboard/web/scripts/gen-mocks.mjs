/**
 * 生成 src/mocks/*.json 夹具。
 *
 * 为什么用生成器而不是手抄 1440 个数字：契约要求 total_watts（1440 点）、
 * appliances[].intervals、metrics 三者内部一致。手抄必然漂移，而后续里程碑的
 * 图表会交叉校验这三者。生成器让三者由同一份用电时刻表推导，改一个时刻表即可重算。
 *
 * 运行：node scripts/gen-mocks.mjs
 */
import { mkdirSync, writeFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const DAY = 1440
const HERE = dirname(fileURLToPath(import.meta.url))
const OUT = resolve(HERE, "..", "src", "mocks")

const hm = (clock) => {
  const [h, m] = clock.split(":").map(Number)
  return h * 60 + m
}

const hhmm = (minute) => {
  const m = ((minute % DAY) + DAY) % DAY
  return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`
}

const round = (n, digits = 3) => Number(n.toFixed(digits))

const RUN = "world_838587"
const REFERENCE_DATE = "2026-09-11"
const DATES = ["2026-09-10", REFERENCE_DATE]

/**
 * 夹具只真实编排了参考日 2026-09-11 的日程。另一天沿用同一套作息，
 * 只调整空调负荷与冰箱占空比相位（凉爽日空调半负荷），
 * 这样日期选择器有真实可切换的数据，而不是伪造一整套作息。
 */
const DATE_VARIANTS = {
  "2026-09-10": { acScale: 0.5, fridgePhase: 15, note: "凉爽日：空调半负荷、冰箱占空比相位不同" },
  [REFERENCE_DATE]: { acScale: 1, fridgePhase: 0, note: null },
}

/* ------------------------------------------------------------------ *
 * 成员日程
 * 活动文本来自模拟后端（英文），UI 外壳为中文——与真实系统一致。
 * ------------------------------------------------------------------ */

const house1Members = [
  {
    id: "Member 1",
    age: 24,
    gender: "male",
    occupation: "MSc Computer Science student",
    bedroom: "Bedroom 1",
    energy_awareness: "medium",
    big_five: { openness: 0.72, conscientiousness: 0.58, extraversion: 0.41, agreeableness: 0.66, neuroticism: 0.44 },
    persona:
      "Night-owl CS master's student from Chengdu. Cooks most evenings, keeps the desk lamp on late, forgets to switch off the kitchen light.",
    is_out: false,
    activities: [
      ["00:00", "07:30", "Bedroom 1", "Sleep", "Asleep in Bedroom 1."],
      ["07:30", "08:05", "Bathroom", "Shower and get dressed", null],
      ["08:05", "08:25", "Kitchen", "Breakfast", "Toast and instant coffee."],
      ["08:25", "09:00", "Out", "Commute to campus", "Bus 25 towards the university."],
      ["09:00", "12:30", "Campus", "Lecture: Distributed Systems", null],
      ["12:30", "13:15", "Campus", "Lunch at the canteen", null],
      ["13:15", "17:00", "Campus", "Lab work on the course project", null],
      ["17:00", "17:40", "Out", "Commute home", "Stops at the corner shop for vegetables."],
      ["17:40", "18:30", "Kitchen", "Cooking dinner", "Stir-fry with rice, hob on full power."],
      ["18:30", "19:15", "Kitchen", "Dinner with housemates", null],
      ["18:45", "19:05", "Kitchen", "Watching a video while eating", "Phone propped against the kettle."],
      ["19:15", "20:00", "Kitchen", "Washing up and tidying", "Loads the dishwasher."],
      ["20:00", "22:30", "Bedroom 1", "Coding coursework", "Two monitors, desk lamp on."],
      ["22:30", "23:00", "Bathroom", "Shower", null],
      ["23:00", "23:50", "Bedroom 1", "Scrolling on the phone", null],
      ["23:50", "24:00", "Bedroom 1", "Winding down", null],
    ],
    decisions: [
      [["17:40", "18:30", "Kitchen", "Cooking dinner"], [["kitchen_inductioncooker", "use"], ["kitchen_kettle", "use"]]],
      [["20:00", "22:30", "Bedroom 1", "Coding coursework"], [["member_1_computer", "use"], ["bedroom_1_light", "use"]]],
      [["22:30", "23:00", "Bathroom", "Shower"], [["bathroom_waterheater", "use"]]],
      [["23:00", "23:50", "Bedroom 1", "Scrolling on the phone"], [["member_1_phone_charger", "charge_home"]]],
    ],
  },
  {
    id: "Member 2",
    age: 23,
    gender: "female",
    occupation: "MSc Finance student, part-time intern",
    bedroom: "Bedroom 2",
    energy_awareness: "high",
    big_five: { openness: 0.55, conscientiousness: 0.81, extraversion: 0.63, agreeableness: 0.7, neuroticism: 0.35 },
    persona:
      "Early riser from Shanghai, runs before class and keeps a strict routine. Turns appliances off at the wall when she notices standby draw.",
    is_out: false,
    activities: [
      ["00:00", "06:45", "Bedroom 2", "Sleep", null],
      ["06:45", "07:15", "Out", "Morning run", "Loop around the park."],
      ["07:15", "07:45", "Bathroom", "Shower and hair", null],
      ["07:45", "08:10", "Kitchen", "Breakfast", "Oats, kettle for tea."],
      ["08:10", "08:50", "Out", "Commute to the office", null],
      ["08:50", "12:00", "Office", "Internship: valuation models", null],
      ["12:00", "13:00", "Out", "Lunch break", null],
      ["13:00", "17:30", "Office", "Internship: client deck", null],
      ["17:30", "18:20", "Out", "Commute home and grocery run", null],
      ["18:20", "19:00", "Kitchen", "Cooking dinner", null],
      ["19:00", "20:00", "Kitchen", "Dinner with housemates", null],
      ["20:00", "20:40", "Bedroom 2", "Reading for the seminar", null],
      ["20:40", "22:10", "Bedroom 2", "Video call with family", null],
      ["21:30", "22:10", "Bathroom", "Laundry", "One 40°C cycle, then hangs it up."],
      ["22:10", "23:30", "Bedroom 2", "Reading", null],
      ["22:30", "23:00", "Bedroom 2", "Listening to a podcast", "Overlaps with reading."],
      ["23:30", "24:00", "Bedroom 2", "Sleep", null],
    ],
    decisions: [
      [["07:15", "07:45", "Bathroom", "Shower and hair"], [["bathroom_waterheater", "use"], ["bathroom_hairdryer", "use"]]],
      [["18:20", "19:00", "Kitchen", "Cooking dinner"], [["kitchen_inductioncooker", "use"], ["kitchen_ricecooker", "run"]]],
      [["21:30", "22:10", "Bathroom", "Laundry"], [["bathroom_washingmachine", "run"]]],
      [["22:10", "23:30", "Bedroom 2", "Reading"], [["member_2_laptop", "use"], ["member_2_phone_charger", "charge_home"]]],
    ],
  },
  {
    id: "Member 3",
    age: 26,
    gender: "male",
    occupation: "PhD candidate, Materials Science",
    bedroom: "Bedroom 3",
    energy_awareness: "low",
    big_five: { openness: 0.78, conscientiousness: 0.74, extraversion: 0.29, agreeableness: 0.52, neuroticism: 0.48 },
    persona:
      "Third-year PhD from Wuhan. Works at the desk from morning to midnight and runs long simulations. Rarely thinks about what the meter is doing.",
    is_out: false,
    activities: [
      ["00:00", "02:30", "Bedroom 3", "Writing thesis chapter", "Late push before the supervisor meeting."],
      ["02:30", "09:30", "Bedroom 3", "Sleep", null],
      ["09:30", "10:00", "Kitchen", "Breakfast", null],
      ["10:00", "13:00", "Bedroom 3", "Writing thesis chapter", null],
      ["13:00", "13:40", "Kitchen", "Lunch", null],
      ["13:40", "17:00", "Bedroom 3", "Analysing simulation results", "Desktop pegged during the solver run."],
      ["17:00", "17:30", "Living Room", "Tea break", "Kettle on, sits on the sofa."],
      ["17:30", "18:30", "Gym", "Gym session", null],
      ["18:30", "19:20", "Kitchen", "Dinner", null],
      ["19:20", "23:00", "Bedroom 3", "Thesis writing", null],
      ["23:00", "23:40", "Bathroom", "Shower", null],
      ["23:40", "24:00", "Bedroom 3", "Reading", null],
    ],
    decisions: [
      [["00:00", "02:30", "Bedroom 3", "Writing thesis chapter"], [["member_3_desktop", "use"], ["bedroom_3_light", "use"]]],
      [["13:40", "17:00", "Bedroom 3", "Analysing simulation results"], [["member_3_desktop", "use"]]],
      [["19:20", "23:00", "Bedroom 3", "Thesis writing"], [["member_3_desktop", "use"], ["bedroom_3_light", "use"]]],
      [["23:00", "23:40", "Bathroom", "Shower"], [["bathroom_waterheater", "use"]]],
    ],
  },
  {
    id: "Member 4",
    age: 22,
    gender: "female",
    occupation: "BA Design student",
    bedroom: "Bedroom 4",
    energy_awareness: "medium",
    big_five: { openness: 0.86, conscientiousness: 0.42, extraversion: 0.74, agreeableness: 0.61, neuroticism: 0.53 },
    persona:
      "Second-year design student from Guangzhou. Studio deadlines mean irregular hours; watches TV in the living room and leaves the tablet charging overnight.",
    is_out: false,
    activities: [
      ["00:00", "01:20", "Living Room", "Gaming", "Console on the shared TV."],
      ["01:20", "10:00", "Bedroom 4", "Sleep", "Sleeps through the morning."],
      ["10:00", "10:30", "Kitchen", "Breakfast", null],
      ["10:30", "12:30", "Bedroom 4", "Studio work: poster layout", null],
      ["12:30", "13:10", "Kitchen", "Lunch", null],
      ["13:10", "16:30", "Studio", "Studio class", null],
      ["16:30", "17:05", "Out", "Commute home", null],
      ["17:05", "17:20", "Bathroom", "Shower", null],
      ["17:20", "17:50", "Bathroom", "Laundry and chores", "Washes a mixed load."],
      ["17:50", "18:00", "Bedroom 4", "Changing", null],
      ["18:00", "19:00", "Kitchen", "Dinner", "Microwaves leftovers."],
      ["19:00", "20:30", "Bedroom 4", "Group project call", null],
      ["20:30", "21:15", "Living Room", "Watching TV", null],
      ["20:35", "21:00", "Living Room", "Texting friends", "Overlaps with the TV."],
      ["21:15", "22:00", "Kitchen", "Washing up", null],
      ["22:00", "23:30", "Bedroom 4", "Drawing", "Tablet plugged in on the desk."],
      ["23:30", "24:00", "Bedroom 4", "Winding down", null],
    ],
    decisions: [
      [["00:00", "01:20", "Living Room", "Gaming"], [["living_room_tv", "use"], ["living_room_light", "use"]]],
      [["17:05", "17:20", "Bathroom", "Shower"], [["bathroom_waterheater", "use"]]],
      [["17:20", "17:50", "Bathroom", "Laundry and chores"], [["bathroom_washingmachine", "run"]]],
      [["20:30", "21:15", "Living Room", "Watching TV"], [["living_room_tv", "use"], ["living_room_light", "use"]]],
      [["22:00", "23:30", "Bedroom 4", "Drawing"], [["member_4_tablet", "charge_home"], ["bedroom_4_light", "use"]]],
    ],
  },
]

const house2Members = [
  {
    id: "Member 1",
    age: 29,
    gender: "female",
    occupation: "Marketing manager",
    bedroom: "Bedroom",
    energy_awareness: "medium",
    big_five: { openness: 0.64, conscientiousness: 0.7, extraversion: 0.58, agreeableness: 0.62, neuroticism: 0.4 },
    persona: "Works from home two days a week and keeps the study warm in the evening.",
    is_out: false,
    activities: [
      ["00:00", "07:00", "Bedroom", "Sleep", null],
      ["07:00", "07:30", "Bathroom", "Shower", null],
      ["07:30", "08:10", "Kitchen", "Breakfast", null],
      ["08:10", "09:00", "Out", "Commute to the office", null],
      ["09:00", "18:00", "Office", "Work", null],
      ["18:00", "18:40", "Out", "Commute home", null],
      ["18:40", "19:30", "Kitchen", "Cooking dinner", null],
      ["19:30", "21:00", "Living Room", "Dinner and TV", null],
      ["21:00", "22:30", "Study", "Catching up on email", null],
      ["22:30", "24:00", "Bedroom", "Reading and sleep", null],
    ],
    decisions: [
      [["18:40", "19:30", "Kitchen", "Cooking dinner"], [["kitchen_oven", "use"], ["kitchen_inductioncooker", "use"]]],
      [["19:30", "21:00", "Living Room", "Dinner and TV"], [["living_room_tv", "use"], ["living_room_airconditioner", "use"]]],
      [["21:00", "22:30", "Study", "Catching up on email"], [["study_desk_lamp", "use"], ["member_1_laptop", "use"]]],
    ],
  },
  {
    id: "Member 2",
    age: 31,
    gender: "male",
    occupation: "Civil engineer",
    bedroom: "Bedroom",
    energy_awareness: "low",
    big_five: { openness: 0.48, conscientiousness: 0.66, extraversion: 0.55, agreeableness: 0.72, neuroticism: 0.37 },
    persona: "Commutes by car, showers late, and charges an electric bike in the hallway.",
    is_out: false,
    activities: [
      ["00:00", "06:40", "Bedroom", "Sleep", null],
      ["06:40", "07:10", "Kitchen", "Breakfast", null],
      ["07:10", "08:00", "Out", "Drive to site", null],
      ["08:00", "17:30", "Out", "Site work", null],
      ["17:30", "18:20", "Out", "Drive home", null],
      ["18:20", "19:00", "Bathroom", "Shower", null],
      ["19:00", "20:00", "Kitchen", "Dinner", null],
      ["20:00", "22:00", "Living Room", "TV and phone", null],
      ["22:00", "22:40", "Hallway", "Charging the e-bike", null],
      ["22:40", "24:00", "Bedroom", "Sleep", null],
    ],
    decisions: [
      [["18:20", "19:00", "Bathroom", "Shower"], [["bathroom_waterheater", "use"]]],
      [["20:00", "22:00", "Living Room", "TV and phone"], [["living_room_tv", "use"]]],
      [["22:00", "22:40", "Hallway", "Charging the e-bike"], [["hallway_ebike_charger", "charge_home"]]],
    ],
  },
]

const house3Members = [
  {
    id: "Member 1",
    age: 68,
    gender: "female",
    occupation: "Retired teacher",
    bedroom: "Bedroom",
    energy_awareness: "high",
    big_five: { openness: 0.6, conscientiousness: 0.79, extraversion: 0.5, agreeableness: 0.8, neuroticism: 0.42 },
    persona: "Home most of the day, cooks three proper meals and runs the heating on a timer.",
    is_out: false,
    activities: [
      ["00:00", "06:30", "Bedroom", "Sleep", null],
      ["06:30", "07:15", "Kitchen", "Breakfast and radio", null],
      ["07:15", "09:00", "Living Room", "Housework and tidying", null],
      ["09:00", "11:30", "Living Room", "Reading", null],
      ["11:30", "13:00", "Kitchen", "Cooking lunch", null],
      ["13:00", "15:00", "Bedroom", "Nap", null],
      ["15:00", "17:00", "Living Room", "Watching television", null],
      ["17:00", "18:30", "Kitchen", "Cooking dinner", null],
      ["18:30", "20:30", "Living Room", "Television", null],
      ["20:30", "22:00", "Bathroom", "Bath", null],
      ["22:00", "24:00", "Bedroom", "Sleep", null],
    ],
    decisions: [
      [["07:15", "09:00", "Living Room", "Housework and tidying"], [["living_room_vacuum", "use"], ["bathroom_washingmachine", "run"]]],
      [["11:30", "13:00", "Kitchen", "Cooking lunch"], [["kitchen_oven", "use"]]],
      [["20:30", "22:00", "Bathroom", "Bath"], [["bathroom_waterheater", "use"]]],
    ],
  },
  {
    id: "Member 2",
    age: 71,
    gender: "male",
    occupation: "Retired",
    bedroom: "Bedroom",
    energy_awareness: "medium",
    big_five: { openness: 0.52, conscientiousness: 0.68, extraversion: 0.44, agreeableness: 0.76, neuroticism: 0.45 },
    persona: "Watches sport in the afternoon and keeps the hallway light on all evening.",
    is_out: false,
    activities: [
      ["00:00", "07:00", "Bedroom", "Sleep", null],
      ["07:00", "07:45", "Kitchen", "Breakfast", null],
      ["07:45", "09:30", "Out", "Walk to the shops", null],
      ["09:30", "12:00", "Living Room", "Newspaper and radio", null],
      ["12:00", "13:30", "Kitchen", "Lunch", null],
      ["13:30", "17:00", "Living Room", "Sport on television", null],
      ["17:00", "18:30", "Living Room", "Reading", null],
      ["18:30", "20:30", "Kitchen", "Dinner", null],
      ["20:30", "22:00", "Living Room", "Television", null],
      ["22:00", "24:00", "Bedroom", "Sleep", null],
    ],
    decisions: [
      [["09:30", "12:00", "Living Room", "Newspaper and radio"], [["living_room_light", "use"]]],
      [["13:30", "17:00", "Living Room", "Sport on television"], [["living_room_tv", "use"], ["living_room_heater", "use"]]],
      [["20:30", "22:00", "Living Room", "Television"], [["living_room_tv", "use"], ["living_room_heater", "use"]]],
    ],
  },
]

/* ------------------------------------------------------------------ *
 * 用电时刻表：每台电器一段或多段 [start, end, watts, action]
 * watts 省略时取额定功率；分段可变功率用于表达变频/占空比。
 * ------------------------------------------------------------------ */

const fridgeDutyCycle = ({ on, period, watts }, phase) => {
  const segments = []
  for (let t = phase; t < DAY; t += period) {
    segments.push([t, Math.min(t + on, DAY), watts, "run"])
  }
  return segments
}

const house1Appliances = [
  {
    unique_id: "kitchen_refrigerator",
    name: "Refrigerator",
    type: "always_on",
    brand: "Hisense",
    room: "Kitchen",
    owner: null,
    power_watts: 150,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["run"],
    segments: [],
    dutyCycle: { on: 20, period: 60, watts: 150 },
  },
  {
    unique_id: "kitchen_inductioncooker",
    name: "Induction Cooker",
    type: "on_demand",
    brand: "Midea",
    room: "Kitchen",
    owner: null,
    power_watts: 2000,
    standby_watts: 1.5,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[1060, 1085, 2000, "use"], [1102, 1120, 2000, "use"], [1190, 1200, 1500, "use"]],
  },
  {
    unique_id: "kitchen_kettle",
    name: "Electric Kettle",
    type: "on_demand",
    brand: "Xiaomi",
    room: "Kitchen",
    owner: null,
    power_watts: 1800,
    standby_watts: 0.8,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[425, 430, 1800, "use"], [1102, 1110, 1800, "use"]],
  },
  {
    unique_id: "kitchen_microwave",
    name: "Microwave",
    type: "on_demand",
    brand: "Galanz",
    room: "Kitchen",
    owner: null,
    power_watts: 1200,
    standby_watts: 2.0,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[485, 491, 1200, "use"], [1085, 1091, 1200, "use"]],
  },
  {
    unique_id: "kitchen_ricecooker",
    name: "Rice Cooker",
    type: "cycle",
    brand: "Bear",
    room: "Kitchen",
    owner: null,
    power_watts: 500,
    standby_watts: 1.2,
    is_exclusive: false,
    available_actions: ["run", "idle"],
    segments: [[1100, 1120, 500, "run"], [1120, 1135, 60, "run"]],
  },
  {
    unique_id: "kitchen_dishwasher",
    name: "Dishwasher",
    type: "cycle",
    brand: "Bosch",
    room: "Kitchen",
    owner: null,
    power_watts: 1300,
    standby_watts: 0.5,
    is_exclusive: true,
    available_actions: ["run", "idle"],
    segments: [[1200, 1215, 1300, "run"], [1215, 1235, 180, "run"]],
  },
  {
    unique_id: "living_room_airconditioner",
    name: "Living Room Air Conditioner",
    type: "on_demand",
    brand: "Gree",
    room: "Living Room",
    owner: null,
    power_watts: 2200,
    standby_watts: 3.0,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    variantScale: "acScale",
    segments: [
      [1050, 1060, 2200, "use"],
      [1080, 1100, 2200, "use"],
      [1120, 1140, 2200, "use"],
      [1145, 1160, 2200, "use"],
      [1195, 1210, 2200, "use"],
      [1245, 1265, 2200, "use"],
      [1325, 1345, 2200, "use"],
    ],
  },
  {
    unique_id: "living_room_tv",
    name: "Living Room TV",
    type: "on_demand",
    brand: "TCL",
    room: "Living Room",
    owner: null,
    power_watts: 120,
    standby_watts: 0.4,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[0, 80, 120, "use"], [1230, 1300, 120, "use"]],
  },
  {
    unique_id: "living_room_vacuum",
    name: "Vacuum Cleaner",
    type: "on_demand",
    brand: "Dyson",
    room: "Living Room",
    owner: null,
    power_watts: 900,
    standby_watts: 0,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[1225, 1240, 900, "use"]],
  },
  {
    unique_id: "living_room_light",
    name: "Living Room Light",
    type: "on_demand",
    brand: null,
    room: "Living Room",
    owner: null,
    power_watts: 40,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[0, 80, 40, "use"], [390, 450, 40, "use"], [1020, 1410, 40, "use"]],
  },
  {
    unique_id: "bathroom_waterheater",
    name: "Bathroom Water Heater",
    type: "on_demand",
    brand: "A.O. Smith",
    room: "Bathroom",
    owner: null,
    power_watts: 3000,
    standby_watts: 2.5,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[430, 448, 3000, "use"], [1025, 1043, 3000, "use"], [1348, 1366, 3000, "use"], [1376, 1394, 3000, "use"]],
  },
  {
    unique_id: "bathroom_hairdryer",
    name: "Hair Dryer",
    type: "on_demand",
    brand: "Panasonic",
    room: "Bathroom",
    owner: null,
    power_watts: 1600,
    standby_watts: 0,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[450, 458, 1600, "use"], [1368, 1374, 1600, "use"]],
  },
  {
    unique_id: "bathroom_washingmachine",
    name: "Washing Machine",
    type: "cycle",
    brand: "LG",
    room: "Bathroom",
    owner: null,
    power_watts: 2000,
    standby_watts: 0.6,
    is_exclusive: true,
    available_actions: ["run", "idle"],
    segments: [[1045, 1058, 2000, "run"], [1290, 1305, 2000, "run"], [1305, 1315, 250, "run"]],
  },
  {
    unique_id: "bathroom_light",
    name: "Bathroom Light",
    type: "on_demand",
    brand: null,
    room: "Bathroom",
    owner: null,
    power_watts: 24,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[438, 470, 24, "use"], [1025, 1070, 24, "use"], [1348, 1400, 24, "use"]],
  },
  {
    unique_id: "hallway_light",
    name: "Hallway Light",
    type: "on_demand",
    brand: null,
    room: "Hallway",
    owner: null,
    power_watts: 18,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[0, 30, 18, "use"], [360, 510, 18, "use"], [1020, 1440, 18, "use"]],
  },
  {
    unique_id: "bedroom_1_light",
    name: "Bedroom 1 Light",
    type: "on_demand",
    brand: null,
    room: "Bedroom 1",
    owner: "Member 1",
    power_watts: 12,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[450, 505, 12, "use"], [1200, 1430, 12, "use"]],
  },
  {
    unique_id: "bedroom_2_light",
    name: "Bedroom 2 Light",
    type: "on_demand",
    brand: null,
    room: "Bedroom 2",
    owner: "Member 2",
    power_watts: 12,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[405, 430, 12, "use"], [435, 465, 12, "use"], [1250, 1410, 12, "use"]],
  },
  {
    unique_id: "bedroom_3_light",
    name: "Bedroom 3 Light",
    type: "on_demand",
    brand: null,
    room: "Bedroom 3",
    owner: "Member 3",
    power_watts: 12,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[0, 150, 12, "use"], [570, 1050, 12, "use"], [1110, 1380, 12, "use"]],
  },
  {
    unique_id: "bedroom_4_light",
    name: "Bedroom 4 Light",
    type: "on_demand",
    brand: null,
    room: "Bedroom 4",
    owner: "Member 4",
    power_watts: 12,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[0, 80, 12, "use"], [600, 660, 12, "use"], [1140, 1320, 12, "use"]],
  },
  {
    unique_id: "member_1_computer",
    name: "Member 1 Desktop",
    type: "on_demand",
    brand: "Lenovo",
    room: null,
    owner: "Member 1",
    power_watts: 180,
    standby_watts: 1.5,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[470, 505, 180, "use"], [1200, 1290, 180, "use"], [1290, 1350, 110, "use"]],
  },
  {
    unique_id: "member_2_laptop",
    name: "Member 2 Laptop",
    type: "on_demand",
    brand: "Apple",
    room: null,
    owner: "Member 2",
    power_watts: 90,
    standby_watts: 0.8,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[400, 420, 90, "use"], [1240, 1330, 90, "use"]],
  },
  {
    unique_id: "member_3_desktop",
    name: "Member 3 Workstation",
    type: "on_demand",
    brand: "Dell",
    room: null,
    owner: "Member 3",
    power_watts: 320,
    standby_watts: 2.0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [
      [0, 150, 120, "use"],
      [570, 600, 120, "use"],
      [640, 700, 120, "use"],
      [700, 760, 320, "use"],
      [760, 1050, 120, "use"],
      [1110, 1380, 120, "use"],
    ],
  },
  {
    unique_id: "member_4_tablet",
    name: "Member 4 Tablet",
    type: "charging",
    brand: "Apple",
    room: null,
    owner: "Member 4",
    power_watts: 30,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["charge_home", "charge_external"],
    segments: [[0, 70, 30, "charge_home"], [1320, 1360, 30, "charge_home"]],
  },
  {
    unique_id: "member_1_phone_charger",
    name: "Member 1 Phone Charger",
    type: "charging",
    brand: "Anker",
    room: null,
    owner: "Member 1",
    power_watts: 12,
    standby_watts: 0.2,
    is_exclusive: false,
    available_actions: ["charge_home", "charge_external"],
    segments: [[420, 450, 12, "charge_home"], [1410, 1440, 12, "charge_home"]],
  },
  {
    unique_id: "member_2_phone_charger",
    name: "Member 2 Phone Charger",
    type: "charging",
    brand: "Anker",
    room: null,
    owner: "Member 2",
    power_watts: 12,
    standby_watts: 0.2,
    is_exclusive: false,
    available_actions: ["charge_home", "charge_external"],
    segments: [[1390, 1420, 12, "charge_home"]],
  },
  {
    unique_id: "member_4_phone_charger",
    name: "Member 4 Phone Charger",
    type: "charging",
    brand: "Baseus",
    room: null,
    owner: "Member 4",
    power_watts: 12,
    standby_watts: 0.2,
    is_exclusive: false,
    available_actions: ["charge_home", "charge_external"],
    segments: [[0, 40, 12, "charge_home"], [1350, 1400, 12, "charge_home"]],
  },
]

const house2Appliances = [
  {
    unique_id: "kitchen_refrigerator",
    name: "Refrigerator",
    type: "always_on",
    brand: "Samsung",
    room: "Kitchen",
    owner: null,
    power_watts: 140,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["run"],
    segments: [],
    dutyCycle: { on: 20, period: 60, watts: 150 },
  },
  {
    unique_id: "kitchen_inductioncooker",
    name: "Induction Cooker",
    type: "on_demand",
    brand: "Bosch",
    room: "Kitchen",
    owner: null,
    power_watts: 2000,
    standby_watts: 1.5,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[1125, 1150, 2000, "use"]],
  },
  {
    unique_id: "kitchen_oven",
    name: "Built-in Oven",
    type: "cycle",
    brand: "Bosch",
    room: "Kitchen",
    owner: null,
    power_watts: 2400,
    standby_watts: 2.0,
    is_exclusive: true,
    available_actions: ["run", "idle"],
    segments: [[1125, 1145, 2400, "run"], [1145, 1165, 900, "run"]],
  },
  {
    unique_id: "living_room_tv",
    name: "Living Room TV",
    type: "on_demand",
    brand: "Sony",
    room: "Living Room",
    owner: null,
    power_watts: 110,
    standby_watts: 0.4,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[1170, 1260, 110, "use"], [1230, 1320, 110, "use"]],
  },
  {
    unique_id: "living_room_airconditioner",
    name: "Living Room Air Conditioner",
    type: "on_demand",
    brand: "Daikin",
    room: "Living Room",
    owner: null,
    power_watts: 2100,
    standby_watts: 3.0,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    variantScale: "acScale",
    segments: [[1170, 1200, 2100, "use"], [1230, 1260, 2100, "use"]],
  },
  {
    unique_id: "bathroom_waterheater",
    name: "Bathroom Water Heater",
    type: "on_demand",
    brand: "Rheem",
    room: "Bathroom",
    owner: null,
    power_watts: 2800,
    standby_watts: 2.5,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[420, 438, 2800, "use"], [1100, 1118, 2800, "use"]],
  },
  {
    unique_id: "study_desk_lamp",
    name: "Study Desk Lamp",
    type: "on_demand",
    brand: null,
    room: "Study",
    owner: "Member 1",
    power_watts: 9,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[1260, 1350, 9, "use"]],
  },
  {
    unique_id: "member_1_laptop",
    name: "Member 1 Laptop",
    type: "on_demand",
    brand: "Apple",
    room: null,
    owner: "Member 1",
    power_watts: 65,
    standby_watts: 0.6,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[1260, 1350, 65, "use"]],
  },
  {
    unique_id: "hallway_ebike_charger",
    name: "E-Bike Charger",
    type: "charging",
    brand: "Bosch",
    room: "Hallway",
    owner: "Member 2",
    power_watts: 240,
    standby_watts: 0.5,
    is_exclusive: true,
    available_actions: ["charge_home", "charge_external"],
    segments: [[1320, 1360, 240, "charge_home"]],
  },
]

const house3Appliances = [
  {
    unique_id: "kitchen_refrigerator",
    name: "Refrigerator",
    type: "always_on",
    brand: "Whirlpool",
    room: "Kitchen",
    owner: null,
    power_watts: 130,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["run"],
    segments: [],
    dutyCycle: { on: 20, period: 60, watts: 150 },
  },
  {
    unique_id: "kitchen_oven",
    name: "Built-in Oven",
    type: "cycle",
    brand: "Siemens",
    room: "Kitchen",
    owner: null,
    power_watts: 2300,
    standby_watts: 2.0,
    is_exclusive: true,
    available_actions: ["run", "idle"],
    segments: [[700, 730, 2300, "run"], [730, 780, 850, "run"], [1050, 1080, 2300, "run"], [1080, 1110, 850, "run"]],
  },
  {
    unique_id: "living_room_tv",
    name: "Living Room TV",
    type: "on_demand",
    brand: "Panasonic",
    room: "Living Room",
    owner: null,
    power_watts: 100,
    standby_watts: 0.4,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[900, 1020, 100, "use"], [1110, 1260, 100, "use"], [1230, 1320, 100, "use"]],
  },
  {
    unique_id: "living_room_heater",
    name: "Living Room Heater",
    type: "on_demand",
    brand: "Dimplex",
    room: "Living Room",
    owner: null,
    power_watts: 1200,
    standby_watts: 0,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[810, 960, 1200, "use"], [1230, 1290, 1200, "use"]],
  },
  {
    unique_id: "living_room_light",
    name: "Living Room Light",
    type: "on_demand",
    brand: null,
    room: "Living Room",
    owner: null,
    power_watts: 36,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[435, 480, 36, "use"], [570, 600, 36, "use"], [1020, 1380, 36, "use"]],
  },
  {
    unique_id: "living_room_vacuum",
    name: "Vacuum Cleaner",
    type: "on_demand",
    brand: "Miele",
    room: "Living Room",
    owner: null,
    power_watts: 800,
    standby_watts: 0,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[450, 470, 800, "use"]],
  },
  {
    unique_id: "bathroom_waterheater",
    name: "Bathroom Water Heater",
    type: "on_demand",
    brand: "Vaillant",
    room: "Bathroom",
    owner: null,
    power_watts: 2600,
    standby_watts: 2.5,
    is_exclusive: true,
    available_actions: ["use", "idle"],
    segments: [[1230, 1265, 2600, "use"]],
  },
  {
    unique_id: "bathroom_washingmachine",
    name: "Washing Machine",
    type: "cycle",
    brand: "Bosch",
    room: "Bathroom",
    owner: null,
    power_watts: 1900,
    standby_watts: 0.6,
    is_exclusive: true,
    available_actions: ["run", "idle"],
    segments: [[465, 480, 1900, "run"], [480, 492, 240, "run"]],
  },
  {
    unique_id: "hallway_light",
    name: "Hallway Light",
    type: "on_demand",
    brand: null,
    room: "Hallway",
    owner: null,
    power_watts: 15,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[390, 480, 15, "use"], [1020, 1380, 15, "use"]],
  },
  {
    unique_id: "bedroom_light",
    name: "Bedroom Light",
    type: "on_demand",
    brand: null,
    room: "Bedroom",
    owner: null,
    power_watts: 14,
    standby_watts: 0,
    is_exclusive: false,
    available_actions: ["use", "idle"],
    segments: [[390, 450, 14, "use"], [1080, 1320, 14, "use"]],
  },
]

const houses = [
  {
    house: "house_0001",
    household_type: "International Student Share House",
    season: "autumn",
    home_name: "Maple Street 12",
    home_type: "Terraced house",
    home_size: 128,
    story:
      "Four postgraduate students from different cities share a rented terraced house near the university. Cooking, laundry and hot water are the big shared loads; the living room air conditioner runs on warm evenings.",
    rooms: ["Bedroom 1", "Bedroom 2", "Bedroom 3", "Bedroom 4", "Kitchen", "Bathroom", "Living Room", "Hallway"],
    members: house1Members,
    appliances: house1Appliances,
  },
  {
    house: "house_0002",
    household_type: "Dual-Income Couple, No Children",
    season: "autumn",
    home_name: "Maple Street 14",
    home_type: "Semi-detached house",
    home_size: 96,
    story:
      "A professional couple who both work full time. Load is concentrated in a short evening window: oven, air conditioner and the e-bike charger.",
    rooms: ["Bedroom", "Kitchen", "Bathroom", "Living Room", "Study", "Hallway"],
    members: house2Members,
    appliances: house2Appliances,
  },
  {
    house: "house_0003",
    household_type: "Retired Couple",
    season: "autumn",
    home_name: "Maple Street 16",
    home_type: "Bungalow",
    home_size: 84,
    story:
      "A retired couple at home through the day. The electric heater carries most of the winter load; cooking happens three times a day on a predictable schedule.",
    rooms: ["Bedroom", "Kitchen", "Bathroom", "Living Room", "Hallway"],
    members: house3Members,
    appliances: house3Appliances,
  },
]

/* ------------------------------------------------------------------ *
 * 派生计算：由时刻表推导 total_watts / intervals / metrics
 * ------------------------------------------------------------------ */

const buildApplianceDay = (appliance, variant) => {
  const perMinute = new Array(DAY).fill(0)
  const intervals = []

  const source = appliance.dutyCycle
    ? fridgeDutyCycle(appliance.dutyCycle, variant.fridgePhase)
    : appliance.segments
  const loadScale = appliance.variantScale === "acScale" ? variant.acScale : 1

  for (const [start, end, wattsRaw, action] of source) {
    const base = wattsRaw ?? appliance.power_watts
    const watts = round(base * loadScale, 1)
    if (watts <= 0) continue
    for (let t = start; t < end; t += 1) perMinute[t] += watts
    intervals.push({ start, end, watts, action: action ?? null })
  }

  intervals.sort((a, b) => a.start - b.start)

  let wattMinutes = 0
  let onMinutes = 0
  let peak = 0
  for (const w of perMinute) {
    wattMinutes += w
    if (w > 0) onMinutes += 1
    if (w > peak) peak = w
  }

  return {
    perMinute,
    day: {
      unique_id: appliance.unique_id,
      info: {
        unique_id: appliance.unique_id,
        name: appliance.name,
        type: appliance.type,
        brand: appliance.brand,
        room: appliance.room,
        owner: appliance.owner,
        power_watts: appliance.power_watts,
        standby_watts: appliance.standby_watts,
        is_exclusive: appliance.is_exclusive,
        available_actions: appliance.available_actions,
      },
      energy_kwh: round(wattMinutes / 60000, 3),
      peak_watts: peak,
      on_minutes: onMinutes,
      intervals,
    },
  }
}

const buildReplay = (houseSpec, date, policy) => {
  const variant = DATE_VARIANTS[date]
  const built = houseSpec.appliances.map((a) => buildApplianceDay(a, variant))
  const totalWatts = new Array(DAY).fill(0)
  for (const b of built) {
    for (let t = 0; t < DAY; t += 1) totalWatts[t] += b.perMinute[t]
  }

  let sumWatts = 0
  let peakWatts = 0
  let peakMinute = 0
  for (let t = 0; t < DAY; t += 1) {
    const w = totalWatts[t]
    sumWatts += w
    if (w > peakWatts) {
      peakWatts = w
      peakMinute = t
    }
  }

  const windowKwh = (from, to) => {
    let acc = 0
    for (let t = from; t < to; t += 1) acc += totalWatts[t]
    return acc / 60000
  }

  let bestWindow = 0
  for (let t = 0; t + 60 <= DAY; t += 1) {
    const kwh = windowKwh(t, t + 60)
    if (kwh > bestWindow) bestWindow = kwh
  }

  const members = houseSpec.members.map((m) => ({
    id: m.id,
    info: {
      id: m.id,
      age: m.age,
      gender: m.gender,
      occupation: m.occupation,
      bedroom: m.bedroom,
      energy_awareness: m.energy_awareness,
      big_five: m.big_five,
      persona: m.persona,
      is_out: m.is_out,
    },
    activities: m.activities.map(([from, to, location, activity, desc]) => ({
      start: hm(from),
      end: hm(to),
      time: hhmm(hm(from)),
      location,
      activity,
      desc: desc ?? null,
    })),
    decisions: m.decisions.map(([[from, to, location, activity], operations]) => ({
      start: hm(from),
      end: hm(to),
      time: hhmm(hm(from)),
      location,
      activity,
      operations: operations.map(([unique_id, action]) => ({ unique_id, action })),
    })),
  }))

  const totalKwh = sumWatts / 60000

  return {
    run: RUN,
    date,
    house: houseSpec.house,
    policy,
    household: {
      run: RUN,
      house: houseSpec.house,
      household_type: houseSpec.household_type,
      season: houseSpec.season,
      story: houseSpec.story,
      home_name: houseSpec.home_name,
      home_type: houseSpec.home_type,
      home_size: houseSpec.home_size,
      rooms: houseSpec.rooms,
      members: members.map((m) => m.info),
      appliances: built.map((b) => b.day.info),
    },
    members,
    appliances: built.map((b) => b.day),
    total_watts: totalWatts.map((w) => round(w, 1)),
    metrics: {
      total_kwh: round(totalKwh, 3),
      peak_watts: round(peakWatts, 1),
      peak_minute: peakMinute,
      peak_window_kwh: round(bestWindow, 3),
      evening_kwh: round(windowKwh(1020, 1320), 3),
      load_factor: round(sumWatts / DAY / peakWatts, 4),
    },
    warnings: variant.note ? [`mock 夹具：${variant.note}，作息与参考日相同。`] : [],
  }
}

const buildStages = (replay, memberId) => {
  const member = replay.members.find((m) => m.id === memberId)
  const decision = member.decisions[0]
  const appliances = replay.household.appliances

  const operations = decision.operations.map((op) => {
    const info = appliances.find((a) => a.unique_id === op.unique_id)
    return {
      unique_id: op.unique_id,
      name: info?.name ?? op.unique_id,
      action: op.action,
      power_watts: info?.power_watts ?? 0,
      room: info?.room ?? null,
    }
  })

  return {
    member: memberId,
    s1: {
      prompt_id: "s1_activity",
      window: { start: decision.start, end: decision.end, time: decision.time },
      context: {
        household_type: replay.household.household_type,
        season: replay.household.season,
        rooms: replay.household.rooms,
        weather: { condition: "partly cloudy", temp_c: 19, wind_kph: 11 },
      },
      persona: member.info.persona,
      output: { location: decision.location, activity: decision.activity },
    },
    s2: {
      prompt_id: "s2_operations",
      candidates: appliances.map((a) => ({
        unique_id: a.unique_id,
        name: a.name,
        type: a.type,
        room: a.room,
        power_watts: a.power_watts,
      })),
      output: { operations },
    },
    s3: {
      prompt_id: "s3_duration",
      output: {
        segments: [
          {
            start: decision.start,
            end: decision.end,
            location: decision.location,
            activity: decision.activity,
            operations: decision.operations,
          },
        ],
      },
    },
    s4: {
      prompt_id: "s4_validate",
      checks: [
        { rule: "appliance_available", passed: true, detail: "all chosen appliances are in the household inventory" },
        { rule: "no_room_conflict", passed: true, detail: "no exclusive appliance double-booked" },
        { rule: "power_within_capacity", passed: true, detail: "peak draw stays under the 63 A main fuse" },
      ],
      output: { accepted: true, repairs: [] },
    },
    s4_raw: {
      raw_text: JSON.stringify({ accepted: true, segments: decision.operations.length }),
      model: "gpt-4.1-mini",
      tokens: 418,
    },
    report: {
      summary: `${memberId} — ${decision.activity} in the ${decision.location} from ${hhmm(decision.start)} to ${hhmm(decision.end)}.`,
      appliance_count: decision.operations.length,
      energy_note: "Duration chosen to match the persona's typical routine.",
    },
    logs: {
      s1: [
        "# Stage 1 — Activity planning",
        "",
        `Input window: ${hhmm(decision.start)} → ${hhmm(decision.end)} (${decision.time})`,
        `Persona: ${member.info.persona}`,
        "",
        "Output:",
        "```json",
        JSON.stringify({ location: decision.location, activity: decision.activity }, null, 2),
        "```",
      ].join("\n"),
      s2: [
        "# Stage 2 — Appliance selection",
        "",
        `Candidate inventory: ${appliances.length} appliances.`,
        "",
        "```json",
        JSON.stringify(operations, null, 2),
        "```",
      ].join("\n"),
      s3: ["# Stage 3 — Duration shaping", "", "Single contiguous segment produced.", ""].join("\n"),
      s4: ["# Stage 4 — Validation", "", "All rules passed, no repair needed.", ""].join("\n"),
    },
  }
}

/* ------------------------------------------------------------------ *
 * 写出
 * ------------------------------------------------------------------ */

const write = (relPath, value) => {
  const target = resolve(OUT, relPath)
  mkdirSync(dirname(target), { recursive: true })
  writeFileSync(target, `${JSON.stringify(value, null, 2)}\n`, "utf8")
  return target
}

const replayByHouse = new Map()
const replayByKey = new Map()
for (const spec of houses) {
  for (const date of DATES) {
    const replay = buildReplay(spec, date, "baseline")
    replayByKey.set(`${spec.house}__${date}`, replay)
    if (date === REFERENCE_DATE) replayByHouse.set(spec.house, replay)
  }
}

const runs = [
  {
    run: RUN,
    dates: DATES,
    houses: houses.map((h) => h.house),
    member_count: houses[0].members.length,
    has_analysis: true,
    latest_mtime: 1789324800,
  },
]

const world = {
  world_id: RUN,
  postcode: "NE1 7RU",
  houses: houses.map((h) => h.house),
  has_events: false,
  latest_mtime: 1789324800,
}

write("runs.json", runs)
write(`runs/${RUN}/meta.json`, runs[0])
write("worlds.json", [world])
write(`worlds/${RUN}.json`, world)
for (const spec of houses) {
  for (const date of DATES) {
    write(`households/${RUN}/${spec.house}.json`, replayByKey.get(`${spec.house}__${REFERENCE_DATE}`).household)
    write(`replays/${RUN}/${date}/${spec.house}__baseline.json`, replayByKey.get(`${spec.house}__${date}`))
  }
}

/**
 * stages/ 只写消费者真正导入的 house：src/mocks/index.ts 静态导入的是参考日
 * house_0001 的 Member_1..4。此前对每栋 house 都生成 stage 文件，house_0002/0003
 * 的四个文件没有任何引用，是死文件（DESIGN.md §29.4）。生成器的产出必须与消费者
 * 一致；新增 house 的 stage 消费者时，同步把 house 加进这里。
 */
const STAGE_HOUSES = ["house_0001"]
for (const spec of houses.filter((h) => STAGE_HOUSES.includes(h.house))) {
  const replay = replayByHouse.get(spec.house)
  for (const m of replay.members) {
    write(`stages/${RUN}/${REFERENCE_DATE}/${spec.house}/${m.id.replace(/\s+/g, "_")}.json`, buildStages(replay, m.id))
  }
}

const summary = []
for (const date of DATES) {
  for (const spec of houses) {
    const r = replayByKey.get(`${spec.house}__${date}`)
    summary.push(
      `  ${date}  ${r.house.padEnd(12)} ${String(r.metrics.total_kwh).padStart(7)} kWh  peak ${String(r.metrics.peak_watts).padStart(6)} W @ ${hhmm(r.metrics.peak_minute)}`,
    )
  }
}

process.stdout.write(
  [
    `wrote mocks to ${OUT}`,
    `houses: ${houses.length}  dates: ${DATES.join(", ")}`,
    `reference day (${REFERENCE_DATE}) total: ${replayByHouse.get("house_0001").metrics.total_kwh} kWh`,
    ...summary,
    "",
  ].join("\n"),
)
