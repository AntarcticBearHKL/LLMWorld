export const DAY_MINUTES = 1440

export const MINUTE_MS = 60_000

export const SPEED_PRESETS = [1, 4, 16] as const

export type SpeedPreset = (typeof SPEED_PRESETS)[number]

export const STEP_PRESETS = [1, 5, 10, 15, 30, 60] as const

export type StepPreset = (typeof STEP_PRESETS)[number]

export const MINUTES_PER_SECOND_AT_1X = 1

export const clampMinute = (value: number): number =>
  Math.min(DAY_MINUTES, Math.max(0, Math.round(value)))

export const snapToStep = (minute: number, step: number): number =>
  step > 0 ? clampMinute(Math.round(minute / step) * step) : clampMinute(minute)

export const stepIndex = (minute: number, step: number): number =>
  step > 0 ? Math.round(minute / step) : minute

export const stepCount = (step: number): number => (step > 0 ? Math.round(DAY_MINUTES / step) : 0)

export const formatHHMM = (minute: number): string => {
  const clamped = clampMinute(minute)
  const hours = Math.floor(clamped / 60)
  const minutes = clamped % 60
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`
}

export const formatMinutesAsDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60)
  const rest = Math.round(minutes % 60)
  if (hours === 0) return `${rest} min`
  if (rest === 0) return `${hours} h`
  return `${hours} h ${rest} min`
}

export const formatWatts = (watts: number): string =>
  watts >= 1000 ? `${(watts / 1000).toFixed(2)} kW` : `${Math.round(watts)} W`

export const formatKwh = (kwh: number): string => kwh.toFixed(2)

const localMidnightAnchor = (): Date => new Date(2000, 0, 1, 0, 0, 0, 0)

export const minuteToDate = (minute: number): Date =>
  new Date(localMidnightAnchor().getTime() + minute * MINUTE_MS)

export const dateToMinute = (date: Date): number =>
  Math.round((Number(date) - localMidnightAnchor().getTime()) / MINUTE_MS)

export const isWithin = (minute: number, start: number, end: number): boolean =>
  minute >= start && minute < end
