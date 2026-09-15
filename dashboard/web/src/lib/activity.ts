/**
 * Activity category inference.
 *
 * The ActivitySegment contract has no category field, so the category is a
 * presentation-layer inference: first use location to decide whether the member
 * is home, then classify by keywords in the activity text.
 * The mapping lives here in one place; anything unmatched falls back to leisure.
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
  sleep: "Sleep",
  meal: "Meal",
  chore: "Chores",
  focus: "Focus",
  leisure: "Leisure",
  away: "Away",
}

export const CATEGORY_DESCRIPTIONS: Record<ActivityCategory, string> = {
  sleep: "Sleep and resting in bed",
  meal: "Eating, drinking, coffee breaks",
  chore: "Cooking, cleaning, laundry, shopping",
  focus: "Classes, lab work, writing, meetings",
  leisure: "TV, games, socialising, exercise, self-care",
  away: "Not inside the home",
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
