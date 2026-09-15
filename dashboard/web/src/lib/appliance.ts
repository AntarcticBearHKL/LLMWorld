/**
 * 电器状态推导。
 *
 * 契约里的 ApplianceInterval 只有 watts / action，没有"待机 vs 使用"标记，
 * 因此状态是展示层推导：常开设备恒为 baseload；有显式 action 或功率高于
 * 待机功率即为 active；功率为 0 为 off；其余为 standby。
 * 规则集中在这里一处，平面图 / 快照 / 电器列表共用。
 */

import type { ApplianceDay, ApplianceInfo, ApplianceInterval } from "@/api/types"

export type ApplianceState = "active" | "baseload" | "standby" | "off"

export const APPLIANCE_STATE_LABELS: Record<ApplianceState, string> = {
  active: "使用中",
  baseload: "常开",
  standby: "待机",
  off: "关闭",
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

/** 是否真的在耗电（用于"哪些电器在用"）。 */
export function isRunning(state: ApplianceState): boolean {
  return state === "active" || state === "baseload"
}

/** 把区间展开成 1440 点功率数组（图表堆叠用）。 */
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

/** 电器归属的空间：房间设备取房间名，个人设备取"某某的个人设备"。 */
export function roomOf(info: ApplianceInfo): string {
  if (info.room !== null && info.room.length > 0) return info.room
  if (info.owner !== null && info.owner.length > 0) return `${info.owner} · 个人设备`
  return "其他"
}
