/**
 * 类型化 API 客户端。
 *
 * 组件永远只调用这里的函数——mock 与真实后端在函数内部切换，
 * 组件层不需要知道数据来自哪里。切换开关：VITE_USE_MOCK。
 */
import type {
  BuildPreview,
  BuildState,
  BuildStep,
  DayReplay,
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
  Snapshot,
  SnapshotHouse,
  StagePayload,
  WorldCreateRequest,
  WorldCreateResult,
  WorldDeleteResult,
  WorldInfo,
} from "@/api/types"
import {
  mockBuildPreview,
  mockBuildState,
  mockHouseholdKey,
  mockHouseholds,
  mockReplays,
  mockReplaysForDate,
  mockRunMeta,
  mockRuns,
  mockRunSummaries,
  mockStageKey,
  mockStages,
  mockWorld,
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
    throw new ApiError(url, response.status, body || `请求失败（HTTP ${response.status}）`)
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
    throw new ApiError(url, response.status, body || `提交失败（HTTP ${response.status}）`)
  }
  return (await response.json()) as T
}

async function deleteJson<T>(path: string): Promise<T> {
  const url = buildUrl(path)
  const response = await fetch(url, { method: "DELETE", headers: { accept: "application/json" } })
  if (!response.ok) {
    const body = await response.text().catch(() => "")
    throw new ApiError(url, response.status, body || `删除失败（HTTP ${response.status}）`)
  }
  return (await response.json()) as T
}

const delay = <T>(value: T): Promise<T> =>
  new Promise((resolve) => {
    setTimeout(() => resolve(value), 0)
  })

/* ------------------------------------------------------------------ *
 * 索引
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
      return Promise.reject(new ApiError("mock:/runs/default", 404, "mock 无可用运行"))
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
  if (USE_MOCK) return delay(mockWorld)
  return request<WorldInfo>(`/worlds/${encodeURIComponent(world)}`)
}

/* ------------------------------------------------------------------ *
 * 世界生命周期 + 分步构建
 * ------------------------------------------------------------------ */

export function createWorld(payload: WorldCreateRequest): Promise<WorldCreateResult> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError("mock:/worlds", 501, "mock 模式不创建世界，请设置 VITE_USE_MOCK=0"),
    )
  }
  return postJson<WorldCreateResult>("/worlds", payload)
}

export function deleteWorld(world: string): Promise<WorldDeleteResult> {
  if (USE_MOCK) {
    return Promise.reject(
      new ApiError(`mock:/worlds/${world}`, 501, "mock 模式不删除世界，请设置 VITE_USE_MOCK=0"),
    )
  }
  return deleteJson<WorldDeleteResult>(`/worlds/${encodeURIComponent(world)}`)
}

export function getBuildState(world: string): Promise<BuildState> {
  if (USE_MOCK) return delay(mockBuildState(world))
  return request<BuildState>(`/worlds/${encodeURIComponent(world)}/build`)
}

export function getBuildPreview(world: string, step: BuildStep, house?: string): Promise<BuildPreview> {
  if (USE_MOCK) return delay(mockBuildPreview(world, step, house ?? null))
  return request<BuildPreview>(
    `/worlds/${encodeURIComponent(world)}/build/steps/${encodeURIComponent(step)}/preview`,
    { house },
  )
}

/* ------------------------------------------------------------------ *
 * 家庭元数据
 * ------------------------------------------------------------------ */

export function getHousehold(run: string, house: string): Promise<HouseholdInfo> {
  if (USE_MOCK) {
    const found = mockHouseholds[mockHouseholdKey(run, house)]
    if (!found) return Promise.reject(new ApiError(`mock:${run}/${house}`, 404, `mock 数据中没有 ${house}`))
    return delay(found)
  }
  return request<HouseholdInfo>(`/worlds/${encodeURIComponent(run)}/houses/${encodeURIComponent(house)}`)
}

/* ------------------------------------------------------------------ *
 * 回放
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
        new ApiError(`mock:${run}/${date}/${house}`, 404, `mock 数据中没有 ${date} / ${house} 的回放`),
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
 * mock 下由已存的各户回放就地推导快照：与 total_watts / intervals 同源，
 * 不会出现"快照和曲线对不上"的假数据。
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
 * 决策流水线
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
      return Promise.reject(new ApiError(`mock:${member}`, 404, `mock 数据中没有 ${member} 的流水线记录`))
    }
    return delay(found)
  }
  return request<StagePayload>(
    `/runs/${encodeURIComponent(run)}/days/${encodeURIComponent(date)}/houses/${encodeURIComponent(house)}/stages/${encodeURIComponent(member)}`,
  )
}

/* ------------------------------------------------------------------ *
 * 作业
 * ------------------------------------------------------------------ */

export function listJobs(): Promise<JobInfo[]> {
  if (USE_MOCK) return delay([])
  return request<JobInfo[]>("/jobs")
}

export function estimateJob(payload: JobRequest): Promise<JobEstimate> {
  if (USE_MOCK) {
    return delay({ kind: payload.kind, estimated_calls: 0, detail: "mock 模式不产生真实调用" })
  }
  return postJson<JobEstimate>("/jobs/estimate", payload)
}

export function createJob(payload: JobRequest): Promise<JobCreateResult> {
  if (USE_MOCK) {
    return Promise.reject(new ApiError("mock:/jobs", 501, "mock 模式不提交作业，请设置 VITE_USE_MOCK=0"))
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
    return Promise.reject(new ApiError(`mock:${callId}`, 404, "mock 模式没有 LLM 调用记录"))
  }
  return request<LLMCallDetail>(
    `/jobs/${encodeURIComponent(jobId)}/llm-calls/${encodeURIComponent(callId)}`,
  )
}

export function cancelJob(jobId: string): Promise<JobInfo> {
  if (USE_MOCK) {
    return Promise.reject(new ApiError("mock:/jobs", 501, "mock 模式不能取消作业"))
  }
  return postJson<JobInfo>(`/jobs/${encodeURIComponent(jobId)}/cancel`, {})
}
