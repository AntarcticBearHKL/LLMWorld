/**
 * Typed API client.
 *
 * Components only ever call the functions here — mock and real backend are
 * switched inside, so the component layer never knows where data comes from.
 * Switch: VITE_USE_MOCK.
 */
import type {
  BuildPreview,
  BuildState,
  BuildStep,
  DayReplay,
  DistrictCreateRequest,
  DistrictCreateResult,
  DistrictDeleteResult,
  DistrictInfo,
  DistrictPreset,
  HouseholdInfo,
  JobCreateResult,
  JobEstimate,
  JobInfo,
  JobRequest,
  LLMCallDetail,
  LLMCallList,
  RunInfo,
  RunMeta,
  RunSummary,
  Settings,
  SettingsUpdate,
  Snapshot,
  SnapshotHouse,
  Spacetime,
  SpacetimeCreate,
  SpacetimeDeleteResult,
  StagePayload,
  WorldCloneRequest,
  WorldCloneResult,
  WorldCreateRequest,
  WorldCreateResult,
  WorldDayBlocks,
  WorldDeleteResult,
  WorldInfo,
} from "@/api/types"
import {
  mockBuildPreview,
  mockBuildState,
  mockDistrictHouseholds,
  mockDistrictPresets,
  mockDistrictsFor,
  mockHouseholdKey,
  mockHouseholds,
  mockReplays,
  mockReplaysForDate,
  mockRunMeta,
  mockRuns,
  mockRunSummaries,
  mockSpacetimesFor,
  mockStageKey,
  mockStages,
  mockWorldDayBlocks,
  mockWorlds,
} from "@/mocks"

const runtimeBase = (): string | undefined => {
  if (typeof window === "undefined") return undefined
  const value = (window as { __API_BASE__?: unknown }).__API_BASE__
  return typeof value === "string" && value.length > 0 ? value : undefined
}

export const API_BASE = runtimeBase() ?? import.meta.env.VITE_API_BASE ?? "/api"

export const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? "1") !== "0"

export class ApiError extends Error {
  readonly status: number
  readonly url: string

  constructor(url: string, status: number, detail: string) {
    super(detail)
    this.name = "ApiError"
    this.status = status
    this.url = url
  }
}

const buildUrl = (path: string, query?: Record<string, string | number | undefined>) => {
  const url = `${API_BASE}${path}`
  if (!query) return url
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined) params.set(key, String(value))
  }
  const qs = params.toString()
  return qs ? `${url}?${qs}` : url
}

async function request<T>(path: string, query?: Record<string, string | number | undefined>): Promise<T> {
  const url = buildUrl(path, query)
  const response = await fetch(url, { headers: { accept: "application/json" } })
  if (!response.ok) {
    const body = await response.text().catch(() => "")
    throw new ApiError(url, response.status, body || `Request failed (HTTP ${response.status})`)
  }
  return (await response.json()) as T
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const url = buildUrl(path)
  const response = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    const body = await response.text().catch(() => "")
    throw new ApiError(url, response.status, body || `Submit failed (HTTP ${response.status})`)
  }
  return (await response.json()) as T
}

async function putJson<T>(path: string, payload: unknown): Promise<T> {
  const url = buildUrl(path)
  const response = await fetch(url, {
    method: "PUT",
    headers: { "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    const body = await response.text().catch(() => "")
    throw new ApiError(url, response.status, body || `Save failed (HTTP ${response.status})`)
  }
  return (await response.json()) as T
}

async function deleteJson<T>(path: string): Promise<T> {
  const url = buildUrl(path)
  const response = await fetch(url, { method: "DELETE", headers: { accept: "application/json" } })
  if (!response.ok) {
    const body = await response.text().catch(() => "")
    throw new ApiError(url, response.status, body || `Delete failed (HTTP ${response.status})`)
  }
  return (await response.json()) as T
}

const delay = <T>(value: T): Promise<T> =>
  new Promise((resolve) => {
    setTimeout(() => resolve(value), 0)
  })

/* ------------------------------------------------------------------ *
 * Index
 * ------------------------------------------------------------------ */

export function listRuns(): Promise<RunInfo[]> {
  if (USE_MOCK) return delay(mockRuns)
  return request<RunInfo[]>("/runs")
}

export function listRunSummaries(query = "", limit?: number): Promise<RunSummary[]> {
  if (USE_MOCK) {
    const needle = query.trim().toLowerCase()
    const matched =
      needle.length === 0
        ? mockRunSummaries
        : mockRunSummaries.filter((item) => item.run.toLowerCase().includes(needle))
    return delay(limit !== undefined && limit > 0 ? matched.slice(0, limit) : matched)
  }
  return request<RunSummary[]>("/runs/summary", { q: query || undefined, limit })
}

export function getDefaultRun(): Promise<RunSummary> {
  if (USE_MOCK) {
    const first = mockRunSummaries[0]
    if (first === undefined) {
      return Promise.reject(new ApiError("mock:/runs/default", 404, "mock has no playable run"))
    }
    return delay(first)
  }
  return request<RunSummary>("/runs/default")
}

export function getRunMeta(run: string): Promise<RunMeta> {
  if (USE_MOCK) return delay(mockRunMeta)
  return request<RunMeta>(`/runs/${encodeURIComponent(run)}/meta`)
}

export function listWorlds(): Promise<WorldInfo[]> {
  if (USE_MOCK) return delay(mockWorlds)
  return request<WorldInfo[]>("/worlds")
}

export function getWorld(world: string): Promise<WorldInfo> {
  if (USE_MOCK) {
    const found = mockWorlds.find((item) => item.world_id === world)
    if (found === undefined) {
      return Promise.reject(new ApiError(`mock:/worlds/${world}`, 404, `mock data has no world ${world}`))
    }
    return delay(found)
  }
  return request<WorldInfo>(`/worlds/${encodeURIComponent(world)}`)
}

/* ------------------------------------------------------------------ *
 * World lifecycle + step-by-step build
 * ------------------------------------------------------------------ */

export function createWorld(payload: WorldCreateRequest): Promise<WorldCreateResult> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError("mock:/worlds", 501, "Mock mode does not create worlds; set VITE_USE_MOCK=0"),
    )
  }
  return postJson<WorldCreateResult>("/worlds", payload)
}

export function deleteWorld(world: string): Promise<WorldDeleteResult> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError(`mock:/worlds/${world}`, 501, "Mock mode does not delete worlds; set VITE_USE_MOCK=0"),
    )
  }
  return deleteJson<WorldDeleteResult>(`/worlds/${encodeURIComponent(world)}`)
}

export function cloneWorld(world: string, payload: WorldCloneRequest): Promise<WorldCloneResult> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError(
        `mock:/worlds/${world}/clone`,
        501,
        "Mock mode does not clone worlds; set VITE_USE_MOCK=0",
      ),
    )
  }
  return postJson<WorldCloneResult>(`/worlds/${encodeURIComponent(world)}/clone`, payload)
}

export function listWorldDistricts(world: string): Promise<DistrictInfo[]> {
  if (USE_MOCK) return delay(mockDistrictsFor(world))
  return request<DistrictInfo[]>(`/worlds/${encodeURIComponent(world)}/districts`)
}

export function createWorldDistrict(
  world: string,
  payload: DistrictCreateRequest,
): Promise<DistrictCreateResult> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError(
        `mock:/worlds/${world}/districts`,
        501,
        "Mock mode does not create districts; set VITE_USE_MOCK=0",
      ),
    )
  }
  return postJson<DistrictCreateResult>(`/worlds/${encodeURIComponent(world)}/districts`, payload)
}

export function deleteWorldDistrict(world: string, district: string): Promise<DistrictDeleteResult> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError(
        `mock:/worlds/${world}/districts/${district}`,
        501,
        "Mock mode does not delete districts; set VITE_USE_MOCK=0",
      ),
    )
  }
  return deleteJson<DistrictDeleteResult>(
    `/worlds/${encodeURIComponent(world)}/districts/${encodeURIComponent(district)}`,
  )
}

export function listDistrictPresets(): Promise<DistrictPreset[]> {
  if (USE_MOCK) return delay(mockDistrictPresets)
  return request<DistrictPreset[]>("/district-presets")
}

export function getDistrictHousehold(
  world: string,
  district: string,
  house: string,
): Promise<HouseholdInfo> {
  if (USE_MOCK) {
    const found = mockDistrictHouseholds(world, district, house)
    if (found === undefined) {
      return Promise.reject(
        new ApiError(
          `mock:${world}/${district}/${house}`,
          404,
          `mock data has no ${house} in ${district}`,
        ),
      )
    }
    return delay(found)
  }
  return request<HouseholdInfo>(
    `/worlds/${encodeURIComponent(world)}/districts/${encodeURIComponent(district)}/houses/${encodeURIComponent(house)}`,
  )
}

export function getBuildState(world: string, district?: string): Promise<BuildState> {
  if (USE_MOCK) return delay(mockBuildState(world, district ?? null))
  return request<BuildState>(`/worlds/${encodeURIComponent(world)}/build`, { district })
}

export function getBuildPreview(
  world: string,
  step: BuildStep,
  district?: string,
  house?: string,
): Promise<BuildPreview> {
  if (USE_MOCK) return delay(mockBuildPreview(world, step, district ?? null, house ?? null))
  return request<BuildPreview>(
    `/worlds/${encodeURIComponent(world)}/build/steps/${encodeURIComponent(step)}/preview`,
    { district, house },
  )
}

export function getSpacetimes(world: string): Promise<Spacetime[]> {
  if (USE_MOCK) return delay(mockSpacetimesFor(world))
  return request<Spacetime[]>(`/worlds/${encodeURIComponent(world)}/spacetimes`)
}

export function createSpacetime(world: string, payload: SpacetimeCreate): Promise<Spacetime> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError(
        `mock:/worlds/${world}/spacetimes`,
        501,
        "Mock mode does not create scenarios; set VITE_USE_MOCK=0",
      ),
    )
  }
  return postJson<Spacetime>(`/worlds/${encodeURIComponent(world)}/spacetimes`, payload)
}

export function deleteSpacetime(name: string): Promise<SpacetimeDeleteResult> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError(
        `mock:/spacetimes/${name}`,
        501,
        "Mock mode does not delete scenarios; set VITE_USE_MOCK=0",
      ),
    )
  }
  return deleteJson<SpacetimeDeleteResult>(`/spacetimes/${encodeURIComponent(name)}`)
}

export function getWorldDayBlocks(
  world: string,
  run: string,
  date: string,
  policy: string,
): Promise<WorldDayBlocks> {
  if (USE_MOCK) return delay(mockWorldDayBlocks(world, run, date))
  return request<WorldDayBlocks>(
    `/worlds/${encodeURIComponent(world)}/runs/${encodeURIComponent(run)}/days/${encodeURIComponent(date)}/blocks`,
    { policy },
  )
}

/* ------------------------------------------------------------------ *
 * Household metadata
 * ------------------------------------------------------------------ */

export function getHousehold(run: string, house: string): Promise<HouseholdInfo> {
  if (USE_MOCK) {
    const found = mockHouseholds[mockHouseholdKey(run, house)]
    if (!found) return Promise.reject(new ApiError(`mock:${run}/${house}`, 404, `mock data has no ${house}`))
    return delay(found)
  }
  return request<HouseholdInfo>(`/worlds/${encodeURIComponent(run)}/houses/${encodeURIComponent(house)}`)
}

/* ------------------------------------------------------------------ *
 * Replay
 * ------------------------------------------------------------------ */

export function getDayReplay(
  run: string,
  date: string,
  house: string,
  policy: string,
): Promise<DayReplay> {
  if (USE_MOCK) {
    const found = mockReplays[`${run}/${date}/${house}`]
    if (!found) {
      return Promise.reject(
        new ApiError(`mock:${run}/${date}/${house}`, 404, `mock data has no replay for ${date} / ${house}`),
      )
    }
    return delay(found)
  }
  return request<DayReplay>(
    `/runs/${encodeURIComponent(run)}/days/${encodeURIComponent(date)}/houses/${encodeURIComponent(house)}`,
    { policy },
  )
}

const wattsAt = (replay: DayReplay, minute: number): number => {
  const value = replay.total_watts[minute]
  return typeof value === "number" ? value : 0
}

/**
 * Derive the snapshot in mock mode from the stored per-house replays, so it
 * shares its source with total_watts / intervals and cannot disagree with the curves.
 */
export function getSnapshot(
  run: string,
  date: string,
  minute: number,
  policy: string,
): Promise<Snapshot> {
  if (USE_MOCK) {
    const replays = mockReplaysForDate(run, date)
    const houses: SnapshotHouse[] = replays.map((replay) => {
      const live = replay.appliances
        .map((appliance) => ({
          appliance,
          interval: appliance.intervals.find((i) => minute >= i.start && minute < i.end),
        }))
        .filter((entry) => entry.interval !== undefined)

      const people = replay.members.map((member) => {
        const segment = member.activities.find((a) => minute >= a.start && minute < a.end)
        return {
          member: member.id,
          location: segment?.location ?? "Out",
          activity: segment?.activity ?? "Away from home",
          powered: live
            .filter((entry) => entry.appliance.info.owner === member.id)
            .map((entry) => entry.appliance.unique_id),
        }
      })

      const powered = live.map(({ appliance, interval }) => ({
        unique_id: appliance.unique_id,
        name: appliance.info.name,
        room: appliance.info.room,
        owner: appliance.info.owner,
        watts: interval?.watts ?? 0,
        action: interval?.action ?? null,
      }))

      return {
        house: replay.house,
        household_type: replay.household.household_type,
        total_watts: wattsAt(replay, minute),
        people,
        powered,
      }
    })
    return delay({ run, date, minute, policy, houses })
  }
  return request<Snapshot>("/replay", { run, date, minute, policy })
}

/* ------------------------------------------------------------------ *
 * Decision pipeline
 * ------------------------------------------------------------------ */

export function getStages(
  run: string,
  date: string,
  house: string,
  member: string,
): Promise<StagePayload> {
  if (USE_MOCK) {
    const found = mockStages[mockStageKey(run, date, house, member)]
    if (!found) {
      return Promise.reject(new ApiError(`mock:${member}`, 404, `mock data has no pipeline records for ${member}`))
    }
    return delay(found)
  }
  return request<StagePayload>(
    `/runs/${encodeURIComponent(run)}/days/${encodeURIComponent(date)}/houses/${encodeURIComponent(house)}/stages/${encodeURIComponent(member)}`,
  )
}

/* ------------------------------------------------------------------ *
 * Jobs
 * ------------------------------------------------------------------ */

export function listJobs(): Promise<JobInfo[]> {
  if (USE_MOCK) return delay([])
  return request<JobInfo[]>("/jobs")
}

export function estimateJob(payload: JobRequest): Promise<JobEstimate> {
  if (USE_MOCK) {
    return delay({ kind: payload.kind, estimated_calls: 0, detail: "mock mode makes no real calls" })
  }
  return postJson<JobEstimate>("/jobs/estimate", payload)
}

export function createJob(payload: JobRequest): Promise<JobCreateResult> {
  if (USE_MOCK) {
    return Promise.reject(new ApiError("mock:/jobs", 501, "Mock mode does not submit jobs; set VITE_USE_MOCK=0"))
  }
  return postJson<JobCreateResult>("/jobs", payload)
}

export function jobStreamUrl(jobId: string): string {
  return buildUrl(`/jobs/${encodeURIComponent(jobId)}/stream`)
}

export function listJobLlmCalls(jobId: string, offset = 0, limit = 500): Promise<LLMCallList> {
  if (USE_MOCK) {
    return delay({ job_id: jobId, world: null, step: null, exists: false, total: 0, calls: [] })
  }
  return request<LLMCallList>(`/jobs/${encodeURIComponent(jobId)}/llm-calls`, { offset, limit })
}

export function getJobLlmCall(jobId: string, callId: string): Promise<LLMCallDetail> {
  if (USE_MOCK) {
    return Promise.reject(new ApiError(`mock:${callId}`, 404, "mock mode has no LLM call records"))
  }
  return request<LLMCallDetail>(
    `/jobs/${encodeURIComponent(jobId)}/llm-calls/${encodeURIComponent(callId)}`,
  )
}

export function cancelJob(jobId: string): Promise<JobInfo> {
  if (USE_MOCK) {
    return Promise.reject(new ApiError("mock:/jobs", 501, "mock mode cannot cancel jobs"))
  }
  return postJson<JobInfo>(`/jobs/${encodeURIComponent(jobId)}/cancel`, {})
}

/* ------------------------------------------------------------------ *
 * Runtime settings
 * ------------------------------------------------------------------ */

/** Matches the defaults in dashboard/backend/settings.py: shared by mock reads and "restore defaults". */
export const DEFAULT_SETTINGS: Settings = {
  model: "deepseek-v4-flash",
  temperature: 1,
  max_tokens: 64000,
  request_timeout_seconds: 600,
  max_retries: 3,
  retry_backoff_seconds: 2,
}

export function getSettings(): Promise<Settings> {
  if (USE_MOCK) return delay({ ...DEFAULT_SETTINGS })
  return request<Settings>("/settings")
}

export function updateSettings(patch: SettingsUpdate): Promise<Settings> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError("mock:/settings", 501, "Mock mode does not save settings; set VITE_USE_MOCK=0"),
    )
  }
  return putJson<Settings>("/settings", patch)
}
