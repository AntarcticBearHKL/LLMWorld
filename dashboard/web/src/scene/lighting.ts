import type { LightingState } from './types.ts'
import { PEAK_WINDOW_END, PEAK_WINDOW_START } from './types.ts'

const MINUTES_PER_DAY = 1440
const DAWN_START_MINUTE = 240
const DAWN_END_MINUTE = 420
const DUSK_START_MINUTE = 1050
const DUSK_END_MINUTE = 1230
const LAMP_NIGHT_THRESHOLD = 0.45
const NIGHT_TINT_ALPHA = 0.55

interface Rgba {
  r: number
  g: number
  b: number
  a: number
}

interface TintStop extends Rgba {
  minute: number
}

const DEEP_NIGHT_TINT: TintStop = { minute: 0, r: 12, g: 20, b: 48, a: NIGHT_TINT_ALPHA }

const TINT_STOPS: readonly TintStop[] = [
  DEEP_NIGHT_TINT,
  { minute: 270, r: 12, g: 20, b: 48, a: NIGHT_TINT_ALPHA },
  { minute: 390, r: 64, g: 104, b: 176, a: 0.3 },
  { minute: 510, r: 255, g: 214, b: 170, a: 0.1 },
  { minute: 720, r: 255, g: 255, b: 255, a: 0 },
  { minute: 990, r: 255, g: 226, b: 178, a: 0.06 },
  { minute: 1140, r: 255, g: 138, b: 64, a: 0.32 },
  { minute: 1230, r: 12, g: 20, b: 48, a: NIGHT_TINT_ALPHA },
  { minute: MINUTES_PER_DAY, r: 12, g: 20, b: 48, a: NIGHT_TINT_ALPHA },
]

function clamp01(value: number): number {
  if (value < 0) return 0
  if (value > 1) return 1
  return value
}

function smoothstep(value: number): number {
  const t = clamp01(value)
  return t * t * (3 - 2 * t)
}

function normalizeMinute(minute: number): number {
  if (!Number.isFinite(minute)) return 0
  const wrapped = minute % MINUTES_PER_DAY
  return wrapped < 0 ? wrapped + MINUTES_PER_DAY : wrapped
}

function mix(from: number, to: number, t: number): number {
  return from + (to - from) * t
}

export function nightLevel(minute: number): number {
  const m = normalizeMinute(minute)
  if (m < DAWN_START_MINUTE) return 1
  if (m < DAWN_END_MINUTE) {
    return 1 - smoothstep((m - DAWN_START_MINUTE) / (DAWN_END_MINUTE - DAWN_START_MINUTE))
  }
  if (m < DUSK_START_MINUTE) return 0
  if (m < DUSK_END_MINUTE) {
    return smoothstep((m - DUSK_START_MINUTE) / (DUSK_END_MINUTE - DUSK_START_MINUTE))
  }
  return 1
}

function sampleTintPalette(minute: number): Rgba {
  let previous = DEEP_NIGHT_TINT
  for (const stop of TINT_STOPS) {
    if (minute < stop.minute) {
      const span = stop.minute - previous.minute
      const t = span > 0 ? (minute - previous.minute) / span : 1
      return {
        r: mix(previous.r, stop.r, t),
        g: mix(previous.g, stop.g, t),
        b: mix(previous.b, stop.b, t),
        a: mix(previous.a, stop.a, t),
      }
    }
    previous = stop
  }
  return previous
}

function formatAlpha(alpha: number): string {
  return String(Math.round(clamp01(alpha) * 1000) / 1000)
}

export function interpolateTint(night: number, minute: number): string {
  const base = sampleTintPalette(normalizeMinute(minute))
  const alpha = clamp01(Math.max(base.a, clamp01(night) * NIGHT_TINT_ALPHA))
  return `rgba(${Math.round(base.r)}, ${Math.round(base.g)}, ${Math.round(base.b)}, ${formatAlpha(alpha)})`
}

function unionRooms(occupiedRooms: readonly string[], litRooms: readonly string[]): string[] {
  const rooms: string[] = []
  const seen = new Set<string>()
  for (const room of occupiedRooms) {
    if (!seen.has(room)) {
      seen.add(room)
      rooms.push(room)
    }
  }
  for (const room of litRooms) {
    if (!seen.has(room)) {
      seen.add(room)
      rooms.push(room)
    }
  }
  return rooms
}

export function lightingFor(
  minute: number,
  occupiedRooms: readonly string[],
  litRooms: readonly string[] = [],
): LightingState {
  const normalized = normalizeMinute(minute)
  const night = nightLevel(normalized)
  return {
    night,
    tint: interpolateTint(night, normalized),
    peakWindow: normalized >= PEAK_WINDOW_START && normalized < PEAK_WINDOW_END,
    lampRooms: night >= LAMP_NIGHT_THRESHOLD ? unionRooms(occupiedRooms, litRooms) : [],
  }
}
