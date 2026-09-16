/**
 * Fixture registry.
 *
 * Static imports are deliberate rather than import.meta.glob: the JSON literal
 * types are structurally matched against the api/types.ts contract, so a fixture
 * that drifts from models.py fails to compile. Glob drops the types and forces
 * assertions, which is exactly what we want to avoid.
 */
import type {
  ArtifactRef,
  BlockSummary,
  BuildPreview,
  BuildState,
  DayReplay,
  DistrictInfo,
  DistrictPreset,
  HouseStepStatus,
  HouseholdInfo,
  RoomInfo,
  RunInfo,
  RunMeta,
  RunSummary,
  Spacetime,
  StagePayload,
  WorldDayBlocks,
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
import spacetimesJson from "@/mocks/spacetimes.json"
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
export const mockRunSummaries: RunSummary[] = mockRuns.map((item) => ({
  run: item.run,
  date_count: item.dates.length,
  house_count: item.houses.length,
  member_count: item.member_count,
  has_baseline: item.has_baseline,
  has_analysis: item.has_analysis,
  latest_mtime: item.latest_mtime,
}))
export const mockRunMeta: RunMeta = asRunMeta(runMeta)
export const mockWorlds: WorldInfo[] = worldsJson
export const mockWorld: WorldInfo = worldJson
export const mockSpacetimes: Spacetime[] = spacetimesJson

export const mockSpacetimesFor = (world: string): Spacetime[] =>
  mockSpacetimes.filter((item) => item.world === world || item.name === world)

export function mockWorldDayBlocks(world: string, run: string, date: string): WorldDayBlocks {
  const info = mockWorlds.find((item) => item.world_id === world)
  const districts = info?.districts ?? []
  const replays = mockReplaysForDate(run, date)
  const houses = replays.map((replay) => replay.house)
  const total = replays.reduce((sum, replay) => sum + replay.metrics.total_kwh, 0)
  const peak = replays.reduce((max, replay) => Math.max(max, replay.metrics.peak_watts ?? 0), 0)
  const blocks: BlockSummary[] = districts.map((postcode) => {
    const scoped = postcode === info?.postcode ? houses : []
    return {
      postcode,
      houses: scoped,
      house_count: scoped.length,
      total_kwh: scoped.length > 0 ? Number(total.toFixed(3)) : 0,
      peak_watts: scoped.length > 0 ? Number(peak.toFixed(1)) : 0,
    }
  })
  return { world, run, date, blocks }
}

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

const MOCK_DISTRICT_DESCRIPTION =
  "A mixed residential district: low-rise detached and semi-detached housing, a young " +
  "student-heavy population clustered near the campus, a high rental share, and a settled " +
  "older cohort on the quieter streets. Households range from one-person rentals to " +
  "four-person families with two cars."

export const mockDistrictPresets: DistrictPreset[] = [
  {
    id: "clayton_3168",
    title: "Clayton 3168 (ABS census style)",
    description: "ABS-style district profile modelled on the Clayton 3168 census text.",
  },
  {
    id: "inner_city_highrise",
    title: "Inner-city high-rise",
    description: "Dense apartment district: high rental share, transient young professionals.",
  },
  {
    id: "outer_suburban_family",
    title: "Outer-suburban family",
    description: "Mortgage-belt district of detached family homes and long commutes.",
  },
]

export function mockBuildState(worldId: string, district: string | null): BuildState {
  const info = mockWorlds.find((item) => item.world_id === worldId)
  const exists = info !== undefined
  const name = district ?? info?.districts[0] ?? ""
  const scoped = info !== undefined && info.districts.includes(name) ? info.houses : []
  const described = scoped.length > 0
  const householdReason = described ? null : "no households yet; run 'district' first"
  const homeReason = described ? null : "no households yet; run 'household' first"
  const assembleReason = described ? null : "no households yet; run 'home' first"
  const houseStatuses = (done: boolean, blockedReason: string | null): HouseStepStatus[] =>
    scoped.map((house) => ({
      house,
      done,
      runnable: blockedReason === null,
      blocked_reason: blockedReason,
    }))

  return {
    world_id: worldId,
    world_dir: `mock://worlds/${worldId}`,
    exists,
    district: name,
    houses: scoped,
    steps: [
      {
        step: "district",
        scope: "district",
        done: described,
        runnable: exists,
        blocked_reason: exists ? null : "world directory is missing",
        houses: [],
      },
      {
        step: "household",
        scope: "district",
        done: described,
        runnable: described,
        blocked_reason: householdReason,
        houses: houseStatuses(described, householdReason),
      },
      {
        step: "home",
        scope: "house",
        done: described,
        runnable: described,
        blocked_reason: homeReason,
        houses: houseStatuses(described, homeReason),
      },
      {
        step: "assemble",
        scope: "house",
        done: false,
        runnable: described,
        blocked_reason: assembleReason,
        houses: houseStatuses(false, assembleReason),
      },
    ],
  }
}

export function mockBuildPreview(
  worldId: string,
  step: string,
  district: string | null,
  house: string | null,
): BuildPreview {
  const base = `output/worlds/${worldId}/${district ?? "primary"}`
  const label = house ?? "house_0001"
  const householdPath = `${base}/${label}/household.json`
  const reads: ArtifactRef[] = [{ path: `${base}/district.json`, exists: true, role: "input" }]
  const writes: ArtifactRef[] = []
  const overwrites: string[] = []

  if (step === "district") {
    writes.push({ path: `${base}/description.md`, exists: false, role: "output" })
  } else if (step === "household") {
    reads.push({ path: `${base}/description.md`, exists: true, role: "input" })
    writes.push({ path: householdPath, exists: false, role: "output" })
  } else {
    reads.push({ path: householdPath, exists: true, role: "input" })
    reads.push({ path: `${base}/${label}/personas.json`, exists: true, role: "input" })
    writes.push({ path: householdPath, exists: true, role: "output" })
    overwrites.push(householdPath)
  }

  return { world_id: worldId, step, district, house, reads, writes, overwrites }
}

export function mockDistrictsFor(world: string): DistrictInfo[] {
  const info = mockWorlds.find((item) => item.world_id === world)
  const houses = info?.houses ?? []
  return (info?.districts ?? []).map((name) => {
    const described = houses.length > 0
    return {
      name,
      description: described ? MOCK_DISTRICT_DESCRIPTION : "",
      house_count: houses.length,
      has_description: described,
    }
  })
}

export function mockDistrictHouseholds(
  world: string,
  district: string,
  house: string,
): HouseholdInfo | undefined {
  const info = mockWorlds.find((item) => item.world_id === world)
  if (info === undefined || !info.districts.includes(district)) return undefined
  return mockHouseholds[mockHouseholdKey(world, house)]
}

export const mockHouseholdKey = (run: string, house: string) => `${run}/${house}`

export const mockStageKey = (run: string, date: string, house: string, member: string) =>
  `${run}/${date}/${house}/${member}`

export const mockReplaysForDate = (run: string, date: string): DayReplay[] =>
  Object.entries(mockReplays)
    .filter(([key]) => key.startsWith(`${run}/${date}/`))
    .map(([, replay]) => replay)
