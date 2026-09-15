/**
 * 活动分类推导。
 *
 * 契约里的 ActivitySegment 没有 category 字段，因此分类是展示层推导：
 * 先看 location 判断"是否在家"，再按活动文本关键词归类。
 * 映射集中在这里一处，未命中一律归入 leisure。
 */

export const ACTIVITY_CATEGORIES = [
  "sleep",
  "meal",
  "chore",
  "focus",
  "leisure",
  "away",
] as const

export type ActivityCategory = (typeof ACTIVITY_CATEGORIES)[number]

export const CATEGORY_LABELS: Record<ActivityCategory, string> = {
  sleep: "睡眠",
  meal: "用餐",
  chore: "家务",
  focus: "学习工作",
  leisure: "休闲自理",
  away: "外出",
}

export const CATEGORY_DESCRIPTIONS: Record<ActivityCategory, string> = {
  sleep: "睡眠与卧床休息",
  meal: "吃饭、喝东西、茶歇",
  chore: "做饭、清洁、洗衣、采购",
  focus: "上课、实验、写作、会议",
  leisure: "电视、游戏、社交、运动、洗漱",
  away: "不在住宅内",
}

const OUT_LOCATION_KEYWORDS = [
  "out",
  "outside",
  "away",
  "campus",
  "university",
  "office",
  "studio",
  "gym",
  "supermarket",
  "shop",
  "street",
  "transit",
  "commute",
]

const KEYWORD_RULES: ReadonlyArray<readonly [ActivityCategory, readonly string[]]> = [
  ["sleep", ["sleep", "nap", "asleep", "bedtime", "resting", "lie down", "dozing"]],
  [
    "meal",
    ["breakfast", "lunch", "dinner", "brunch", "supper", "meal", "eat", "snack", "coffee", "tea", "drink"],
  ],
  [
    "chore",
    [
      "cook",
      "baking",
      "dish",
      "clean",
      "tidy",
      "laundry",
      "wash the",
      "washing",
      "vacuum",
      "grocery",
      "groceries",
      "iron",
      "trash",
      "rubbish",
      "recycl",
      "chores",
      "washing up",
    ],
  ],
  [
    "focus",
    [
      "study",
      "studying",
      "work",
      "working",
      "lecture",
      "seminar",
      "class",
      "lab",
      "thesis",
      "writ",
      "coding",
      "code",
      "project",
      "assignment",
      "exam",
      "research",
      "meeting",
      "internship",
      "email",
      "analys",
      "reading paper",
      "presentation",
    ],
  ],
  [
    "leisure",
    [
      "tv",
      "television",
      "gaming",
      "game",
      "movie",
      "music",
      "podcast",
      "social",
      "chat",
      "texting",
      "scrolling",
      "phone",
      "reading",
      "read",
      "draw",
      "hobby",
      "relax",
      "winding down",
      "shower",
      "bath",
      "wash up",
      "get dressed",
      "changing",
      "grooming",
      "hair",
      "gym session",
      "exercise",
      "run",
      "walk",
    ],
  ],
]

export function categorizeActivity(activity: string, location: string): ActivityCategory {
  const haystack = activity.toLowerCase()
  const place = location.toLowerCase()
  const isAway = OUT_LOCATION_KEYWORDS.some((keyword) => place.includes(keyword))

  if (haystack.includes("sleep") || haystack.includes("nap")) return "sleep"

  for (const [category, keywords] of KEYWORD_RULES) {
    if (keywords.some((keyword) => haystack.includes(keyword))) {
      if (category === "leisure" && isAway) return "away"
      if (category === "meal" && isAway) return "away"
      if (category === "focus" && isAway) return "away"
      return category
    }
  }

  return isAway ? "away" : "leisure"
}
