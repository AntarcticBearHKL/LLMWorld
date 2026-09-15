import type { AppliancePose, LightingState } from "./types"

export type EffectKind = "steam" | "airflow" | "screen" | "ring" | "drum" | "glow" | "none"

export const EFFECTS_DEFAULT_ENABLED = true

const contains = (label: string, needles: readonly string[]): boolean => {
  const key = label.toLowerCase()
  return needles.some((needle) => key.includes(needle))
}

const STEAM = ["kettle", "ricecooker", "oven", "toaster", "cooker", "microwave"]
const AIRFLOW = ["airconditioner", "fan", "rangehood", "dehumidifier", "spaceheater"]
const SCREEN = ["television", "tv", "monitor", "computer", "laptop", "gameconsole"]
const RING = ["inductioncooker", "induction"]
const DRUM = ["washingmachine", "dishwasher", "dryer", "clothesdryer"]
const LAMP = ["light", "lamp"]

export const effectFor = (
  pose: AppliancePose,
  lighting: LightingState,
): { kind: EffectKind; intensity: number } => {
  if (pose.state !== "active") return { kind: "none", intensity: 0 }
  const intensity = Math.min(1, Math.max(0.25, pose.watts / 2000))
  if (contains(pose.label, STEAM)) return { kind: "steam", intensity }
  if (contains(pose.label, AIRFLOW)) return { kind: "airflow", intensity }
  if (contains(pose.label, SCREEN)) return { kind: "screen", intensity }
  if (contains(pose.label, RING)) return { kind: "ring", intensity }
  if (contains(pose.label, DRUM)) return { kind: "drum", intensity }
  if (contains(pose.label, LAMP) && lighting.night >= 0.45) return { kind: "glow", intensity }
  return { kind: "none", intensity: 0 }
}

export const effectSlots = (kind: EffectKind): number => {
  if (kind === "steam") return 3
  if (kind === "airflow") return 2
  return 1
}
