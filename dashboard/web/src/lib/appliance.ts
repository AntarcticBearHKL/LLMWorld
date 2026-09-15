/**
 * Appliance state inference.
 *
 * The ApplianceInterval contract only carries watts / action, with no
 * "standby vs in use" marker, so the state is a presentation-layer inference:
 * always_on devices are always baseload; an explicit action or wattage above
 * standby is active; zero watts is off; anything else is standby.
 * The rules live here in one place and are shared by the floor plan, snapshot
 * and appliance list.
 */

import type { ApplianceDay, ApplianceInfo, ApplianceInterval } from "@/api/types"

export type ApplianceState = "active" | "baseload" | "standby" | "off"

export const APPLIANCE_STATE_LABELS: Record<ApplianceState, string> = {
  active: "In use",
  baseload: "Always on",
  standby: "Standby",
  off: "Off",
}

const EPSILON = 1e-6

export function intervalAt(appliance: ApplianceDay, minute: number): ApplianceInterval | undefined {
  return appliance.intervals.find((interval) => minute >= interval.start && minute < interval.end)
}

export function stateOf(
  info: ApplianceInfo,
  interval: ApplianceInterval | undefined,
): ApplianceState {
  if (interval === undefined) return "off"
  if (info.type === "always_on") return "baseload"
  if (interval.action !== null) return "active"
  if (interval.watts > info.standby_watts + EPSILON) return "active"
  if (interval.watts <= EPSILON) return "off"
  return "standby"
}

export function stateAt(appliance: ApplianceDay, minute: number): ApplianceState {
  return stateOf(appliance.info, intervalAt(appliance, minute))
}

export function wattsAt(appliance: ApplianceDay, minute: number): number {
  return intervalAt(appliance, minute)?.watts ?? 0
}

/** True when the appliance actually draws power (used for "which appliances are on"). */
export function isRunning(state: ApplianceState): boolean {
  return state === "active" || state === "baseload"
}

/** Expand the intervals into a 1440-point wattage array (used for chart stacking). */
export function minutesOf(appliance: ApplianceDay): number[] {
  const out = new Array<number>(1440).fill(0)
  for (const interval of appliance.intervals) {
    const end = Math.min(1440, interval.end)
    for (let minute = Math.max(0, interval.start); minute < end; minute += 1) {
      out[minute] = interval.watts
    }
  }
  return out
}

/** Room an appliance belongs to: named room, or "<owner> · personal device" for personal items. */
export function roomOf(info: ApplianceInfo): string {
  if (info.room !== null && info.room.length > 0) return info.room
  if (info.owner !== null && info.owner.length > 0) return `${info.owner} · personal device`
  return "Other"
}
