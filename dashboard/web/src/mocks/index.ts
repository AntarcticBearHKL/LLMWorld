/**
 * 夹具注册表。
 *
 * 这里刻意使用静态 import 而不是 import.meta.glob：JSON 的字面量类型会被
 * TypeScript 结构化比对到 api/types.ts 的契约类型上，夹具一旦偏离 models.py
 * 就编译失败。glob 会丢掉类型，只能靠断言，那正是我们要避免的。
 */
import type {
  DayReplay,
  HouseholdInfo,
  RoomInfo,
  RunInfo,
  RunMeta,
  StagePayload,
  WorldInfo,
} from "@/api/types"

import runMeta from "@/mocks/runs/world_838587/meta.json"
import runsJson from "@/mocks/runs.json"
import house1 from "@/mocks/households/world_838587/house_0001.json"
import house2 from "@/mocks/households/world_838587/house_0002.json"
import house3 from "@/mocks/households/world_838587/house_0003.json"
import replay1 from "@/mocks/replays/world_838587/2026-09-11/house_0001__baseline.json"
import replay2 from "@/mocks/replays/world_838587/2026-09-11/house_0002__baseline.json"
import replay3 from "@/mocks/replays/world_838587/2026-09-11/house_0003__baseline.json"
import replay1b from "@/mocks/replays/world_838587/2026-09-10/house_0001__baseline.json"
import replay2b from "@/mocks/replays/world_838587/2026-09-10/house_0002__baseline.json"
import replay3b from "@/mocks/replays/world_838587/2026-09-10/house_0003__baseline.json"
import stages1 from "@/mocks/stages/world_838587/2026-09-11/house_0001/Member_1.json"
import stages2 from "@/mocks/stages/world_838587/2026-09-11/house_0001/Member_2.json"
import stages3 from "@/mocks/stages/world_838587/2026-09-11/house_0001/Member_3.json"
import stages4 from "@/mocks/stages/world_838587/2026-09-11/house_0001/Member_4.json"
import worldJson from "@/mocks/worlds/world_838587.json"
import worldsJson from "@/mocks/worlds.json"

export const MOCK_RUN = "world_838587"
export const MOCK_REFERENCE_DATE = "2026-09-11"

const asRunInfo = (raw: {
  run: string
  dates: string[]
  houses: string[]
  member_count: number
  has_analysis: boolean
  latest_mtime: number | null
  has_baseline?: boolean
  policies?: string[]
}): RunInfo => ({
  run: raw.run,
  dates: raw.dates,
  houses: raw.houses,
  member_count: raw.member_count,
  has_analysis: raw.has_analysis,
  has_baseline: raw.has_baseline ?? true,
  policies: raw.policies ?? [],
  latest_mtime: raw.latest_mtime,
})

const asRunMeta = (raw: {
  run: string
  dates: string[]
  houses: string[]
  policies?: string[]
}): RunMeta => ({
  run: raw.run,
  dates: raw.dates,
  houses: raw.houses,
  policies: raw.policies ?? [],
})

export const mockRuns: RunInfo[] = runsJson.map(asRunInfo)
export const mockRunMeta: RunMeta = asRunMeta(runMeta)
export const mockWorlds: WorldInfo[] = worldsJson
export const mockWorld: WorldInfo = worldJson

type RawHouseholdInfo = Omit<HouseholdInfo, "room_meta"> & { room_meta?: RoomInfo[] }

type RawDayReplay = Omit<DayReplay, "household"> & { household: RawHouseholdInfo }

const asHouseholdInfo = (raw: RawHouseholdInfo): HouseholdInfo => ({
  ...raw,
  room_meta: raw.room_meta ?? raw.rooms.map((name) => ({ name, size: null })),
})

const asDayReplay = (raw: RawDayReplay): DayReplay => ({
  ...raw,
  household: asHouseholdInfo(raw.household),
})

export const mockHouseholds: Record<string, HouseholdInfo> = {
  "world_838587/house_0001": asHouseholdInfo(house1),
  "world_838587/house_0002": asHouseholdInfo(house2),
  "world_838587/house_0003": asHouseholdInfo(house3),
}

export const mockReplays: Record<string, DayReplay> = {
  "world_838587/2026-09-11/house_0001": asDayReplay(replay1),
  "world_838587/2026-09-11/house_0002": asDayReplay(replay2),
  "world_838587/2026-09-11/house_0003": asDayReplay(replay3),
  "world_838587/2026-09-10/house_0001": asDayReplay(replay1b),
  "world_838587/2026-09-10/house_0002": asDayReplay(replay2b),
  "world_838587/2026-09-10/house_0003": asDayReplay(replay3b),
}

export const mockStages: Record<string, StagePayload> = {
  "world_838587/2026-09-11/house_0001/Member 1": stages1,
  "world_838587/2026-09-11/house_0001/Member 2": stages2,
  "world_838587/2026-09-11/house_0001/Member 3": stages3,
  "world_838587/2026-09-11/house_0001/Member 4": stages4,
}

export const mockHouseholdKey = (run: string, house: string) => `${run}/${house}`

export const mockStageKey = (run: string, date: string, house: string, member: string) =>
  `${run}/${date}/${house}/${member}`

export const mockReplaysForDate = (run: string, date: string): DayReplay[] =>
  Object.entries(mockReplays)
    .filter(([key]) => key.startsWith(`${run}/${date}/`))
    .map(([, replay]) => replay)
