/**
 * 与 dashboard/backend/models.py 一一对应的 TypeScript 契约镜像。
 * 契约是唯一真源：此处不得新增后端不存在的字段。
 */

export interface RunInfo {
  run: string
  dates: string[]
  houses: string[]
  member_count: number
  has_analysis: boolean
  has_baseline: boolean
  policies: string[]
  latest_mtime: number | null
}

export interface RunSummary {
  run: string
  date_count: number
  house_count: number
  member_count: number
  has_baseline: boolean
  has_analysis: boolean
  latest_mtime: number | null
}

export interface RunMeta {
  run: string
  dates: string[]
  houses: string[]
  policies: string[]
}

export interface WorldInfo {
  world_id: string
  postcode: string | null
  houses: string[]
  has_events: boolean
  latest_mtime: number | null
}

export interface HomeListEntry {
  run: string
  dates: string[]
  houses: string[]
}

export type ApplianceType = "on_demand" | "charging" | "always_on" | "cycle"

export interface ApplianceInfo {
  unique_id: string
  name: string
  type: string
  brand: string | null
  room: string | null
  owner: string | null
  power_watts: number
  standby_watts: number
  is_exclusive: boolean
  available_actions: string[]
}

export interface MemberInfo {
  id: string
  age: number | null
  gender: string | null
  occupation: string | null
  bedroom: string | null
  energy_awareness: string | null
  big_five: Record<string, number>
  persona: string
  is_out: boolean
}

export interface RoomInfo {
  name: string
  size: number | null
}

export interface HouseholdInfo {
  run: string
  house: string
  household_type: string
  season: string | null
  story: string | null
  home_name: string | null
  home_type: string | null
  home_size: number | null
  rooms: string[]
  room_meta: RoomInfo[]
  members: MemberInfo[]
  appliances: ApplianceInfo[]
}

export interface ActivitySegment {
  start: number
  end: number
  time: string
  location: string
  activity: string
  desc: string | null
}

export type OperationAction =
  | "use"
  | "idle"
  | "run"
  | "charge_home"
  | "charge_external"

export interface Operation {
  unique_id: string
  action: string
}

export interface DecisionSegment {
  start: number
  end: number
  time: string
  location: string
  activity: string
  operations: Operation[]
}

export interface MemberDay {
  id: string
  info: MemberInfo
  activities: ActivitySegment[]
  decisions: DecisionSegment[]
}

export interface ApplianceInterval {
  start: number
  end: number
  watts: number
  action: string | null
}

export interface ApplianceDay {
  unique_id: string
  info: ApplianceInfo
  energy_kwh: number
  peak_watts: number
  on_minutes: number
  intervals: ApplianceInterval[]
}

export interface DayMetrics {
  total_kwh: number
  peak_watts: number
  peak_minute: number
  peak_window_kwh: number | null
  evening_kwh: number | null
  load_factor: number | null
}

export interface DayReplay {
  run: string
  date: string
  house: string
  policy: string
  household: HouseholdInfo
  members: MemberDay[]
  appliances: ApplianceDay[]
  total_watts: number[]
  metrics: DayMetrics
  warnings: string[]
}

export interface SnapshotPerson {
  member: string
  location: string
  activity: string
  powered: string[]
}

export interface SnapshotAppliance {
  unique_id: string
  name: string
  room: string | null
  owner: string | null
  watts: number
  action: string | null
}

export interface SnapshotHouse {
  house: string
  household_type: string
  total_watts: number
  people: SnapshotPerson[]
  powered: SnapshotAppliance[]
}

export interface Snapshot {
  run: string
  date: string
  minute: number
  policy: string
  houses: SnapshotHouse[]
}

export interface StagePayload {
  member: string
  s1: unknown
  s2: unknown
  s3: unknown
  s4: unknown
  s4_raw: unknown
  report: unknown
  logs: Record<string, string>
}

export type JobKind = "world" | "simulate" | "build"

export type BuildStep = "types" | "personas" | "household" | "assemble"

export type JobStatus = "queued" | "running" | "done" | "failed" | "cancelled"

export interface JobRequest {
  kind: JobKind
  world?: string | null
  count?: number | null
  world_config?: string | null
  seed?: number | null
  date?: string | null
  days?: number | null
  house?: string | null
  member?: string | null
  env?: string | null
  policy?: string | null
  policy_schedule?: string[]
  event?: string[]
  event_template?: string[]
  community_notice?: string[]
  s4_only?: boolean
  cost_context?: boolean
  cost_context_mode?: "strong" | "soft"
  price_sensitivity?: "low" | "high" | null
  natural_ev?: boolean
  peer_nudge?: boolean
  bill_feedback?: boolean
  temperature?: number | null
  no_thinking?: boolean
  reasoning_effort?: "low" | "medium" | "high" | null
  workers?: number | null
  confirm?: boolean
  step?: BuildStep | null
}

export interface JobEstimate {
  kind: string
  estimated_calls: number
  detail: string
}

export interface JobInfo {
  id: string
  kind: string
  status: JobStatus
  created_at: string
  started_at: string | null
  finished_at: string | null
  argv: string[]
  world: string | null
  exit_code: number | null
  log_path: string | null
  line_count: number
  error: string | null
  step: string | null
  house: string | null
}

export interface JobCreateResult {
  job: JobInfo
  estimate: JobEstimate
}

export interface WorldCreateRequest {
  world_id: string
  world_config?: string | null
  seed?: number | null
}

export interface WorldCreateResult {
  world_id: string
  world_dir: string
  created: boolean
}

export interface WorldDeleteResult {
  world_id: string
  existed: boolean
  deleted: boolean
  moved_to: string | null
}

export interface ArtifactRef {
  path: string
  exists: boolean
  role: "input" | "output"
}

export interface BuildPreview {
  world_id: string
  step: string
  house: string | null
  reads: ArtifactRef[]
  writes: ArtifactRef[]
  overwrites: string[]
}

export interface HouseStepStatus {
  house: string
  done: boolean
  runnable: boolean
  blocked_reason: string | null
}

export interface BuildStepStatus {
  step: string
  scope: "world" | "house"
  done: boolean
  runnable: boolean
  blocked_reason: string | null
  houses: HouseStepStatus[]
}

export interface BuildState {
  world_id: string
  world_dir: string
  exists: boolean
  houses: string[]
  steps: BuildStepStatus[]
}

export interface LLMCallSummary {
  logical_call_id: string
  request_index: number
  request_count: number
  http_status: number | null
  duration_seconds: number | null
  started_at: string | null
  prompt_chars: number | null
  ok: boolean
  error: string | null
  has_response: boolean
}

export interface LLMCallList {
  job_id: string
  world: string | null
  step: string | null
  exists: boolean
  total: number
  calls: LLMCallSummary[]
}

export interface LLMCallDetail {
  logical_call_id: string
  request_index: number
  request_count: number
  http_status: number | null
  duration_seconds: number | null
  started_at: string | null
  prompt_chars: number | null
  error: string | null
  request: Record<string, unknown> | null
  response: unknown
}

export interface Settings {
  model: string
  temperature: number
  max_tokens: number
  request_timeout_seconds: number
  max_retries: number
  retry_backoff_seconds: number
}

export type SettingsUpdate = Partial<Settings>
