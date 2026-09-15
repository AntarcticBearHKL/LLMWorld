import type { RoomRect } from "./types"
import { APPLIANCE_SLOTS_PER_ROOM, ROOM_GAP } from "./types"

const GLYPHS: ReadonlyArray<readonly [string, string]> = [
  ["airconditioner", "空"],
  ["refrigerator", "冰"],
  ["freezer", "冻"],
  ["washingmachine", "洗"],
  ["clothesdryer", "烘"],
  ["dishwasher", "碗"],
  ["television", "视"],
  ["tv", "视"],
  ["monitor", "屏"],
  ["computer", "电"],
  ["laptop", "电"],
  ["phone", "机"],
  ["light", "灯"],
  ["lamp", "灯"],
  ["inductioncooker", "灶"],
  ["oven", "烤"],
  ["microwave", "微"],
  ["kettle", "壶"],
  ["toaster", "司"],
  ["ricecooker", "饭"],
  ["rangehood", "烟"],
  ["fan", "扇"],
  ["spaceheater", "暖"],
  ["waterheater", "热"],
  ["dehumidifier", "除"],
  ["vacuumcleaner", "吸"],
  ["router", "网"],
  ["gameconsole", "游"],
  ["electricvehicle", "车"],
  ["ebike", "车"],
]

const normalize = (value: string): string => value.toLowerCase().replace(/[\s_-]+/g, "")

export const applianceGlyph = (label: string, type: string): string => {
  const key = normalize(label)
  for (const [needle, glyph] of GLYPHS) {
    if (key.includes(needle)) return glyph
  }
  const fallbackKey = normalize(type)
  for (const [needle, glyph] of GLYPHS) {
    if (fallbackKey.includes(needle)) return glyph
  }
  return label.slice(0, 1)
}

export type ToneKey = "energy" | "brand" | "fgMuted" | "fgSubtle" | "borderStrong" | "bg"

export const applianceToneKey = (
  state: "active" | "baseload" | "standby" | "off",
  cycling: boolean,
): ToneKey => {
  if (state === "active") return cycling ? "brand" : "energy"
  if (state === "baseload") return "fgMuted"
  if (state === "standby") return "fgSubtle"
  return "borderStrong"
}

export const applianceGlyphToneKey = (
  state: "active" | "baseload" | "standby" | "off",
): ToneKey => (state === "active" || state === "baseload" ? "bg" : "fgSubtle")

export const appliancePulseName = (
  state: "active" | "baseload" | "standby" | "off",
  cycling: boolean,
): string => {
  if (state !== "active") return ""
  return cycling ? "pulse-cycling" : "pulse-active"
}

export const applianceSlot = (index: number, rect: RoomRect): { x: number; y: number } => {
  const cols = 3
  const rows = Math.max(1, Math.ceil(APPLIANCE_SLOTS_PER_ROOM / cols))
  const pad = Math.max(ROOM_GAP + 8, 12)
  const topPad = pad + 20
  const innerW = Math.max(1, rect.w - pad * 2)
  const innerH = Math.max(1, rect.h - topPad - pad)
  const col = Math.min(cols - 1, index % cols)
  const row = Math.min(rows - 1, Math.floor(index / cols))
  return {
    x: rect.x + pad + ((col + 0.5) / cols) * innerW,
    y: rect.y + topPad + ((row + 0.5) / rows) * innerH,
  }
}
