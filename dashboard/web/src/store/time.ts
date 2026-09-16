import { create } from "zustand"

import { DAY_MINUTES, MINUTES_PER_SECOND_AT_1X, SPEED_PRESETS, clampMinute, snapToStep, stepIndex } from "@/lib/time"

export const DEFAULT_POLICY = "baseline"

export type ViewKey = "worlds" | "world" | "watch" | "jobs" | "settings"

export const DEFAULT_VIEW: ViewKey = "worlds"

const VIEW_KEYS = new Set<string>(["worlds", "world", "watch", "jobs", "settings"])

const readView = (value: string | null): ViewKey =>
  value !== null && VIEW_KEYS.has(value) ? (value as ViewKey) : DEFAULT_VIEW

export type WorldTab = "scenarios" | "household"

export const DEFAULT_WORLD_TAB: WorldTab = "household"

const WORLD_TABS = new Set<string>(["scenarios", "household"])

const LEGACY_TABS: Record<string, WorldTab> = { spacetime: "scenarios", scenario: "scenarios" }

const readWorldTab = (value: string | null): WorldTab => {
  if (value === null) return DEFAULT_WORLD_TAB
  if (WORLD_TABS.has(value)) return value as WorldTab
  return LEGACY_TABS[value] ?? DEFAULT_WORLD_TAB
}

const readIndoor = (value: string | null): boolean => value === "1" || value === "true"

export type PlayMode = "continuous" | "autoStep"

const SPEEDS: readonly number[] = SPEED_PRESETS

const DWELL_MS_BY_SPEED: Record<number, number> = { 1: 1500, 4: 500, 16: 120 }

export const dwellMsFor = (speed: number): number =>
  DWELL_MS_BY_SPEED[speed] ?? DWELL_MS_BY_SPEED[1] ?? 1500

export interface TimeState {
  minute: number
  isPlaying: boolean
  playMode: PlayMode
  dwellMs: number
  speed: number
  run: string
  date: string
  house: string
  policy: string
  view: ViewKey
  world: string
  tab: WorldTab
  block: string
  indoor: boolean
  step: string
  selectedMember: string | null
  carry: number
  stepMinutes: number
  advance: (deltaSeconds: number) => void
  setMinute: (minute: number) => void
  stepBy: (deltaMinutes: number) => void
  stepOnce: (direction: 1 | -1) => void
  setStepMinutes: (value: number) => void
  setPlaying: (playing: boolean) => void
  setPlayMode: (mode: PlayMode) => void
  togglePlay: () => void
  setSpeed: (speed: number) => void
  setRun: (run: string) => void
  setDate: (date: string) => void
  setHouse: (house: string) => void
  setPolicy: (policy: string) => void
  setView: (view: ViewKey) => void
  setWorld: (world: string) => void
  setTab: (tab: WorldTab) => void
  setBlock: (block: string) => void
  setIndoor: (indoor: boolean) => void
  setStep: (step: string) => void
  setSelectedMember: (member: string | null) => void
  setSelection: (selection: { run?: string; date?: string; house?: string; policy?: string }) => void
  reset: () => void
}

const readInitial = () => {
  const fallback = {
    minute: 0,
    run: "",
    date: "",
    house: "",
    policy: DEFAULT_POLICY,
    view: DEFAULT_VIEW,
    world: "",
    tab: DEFAULT_WORLD_TAB,
    block: "",
    indoor: false,
    step: "",
  }
  if (typeof window === "undefined") return fallback
  const params = new URLSearchParams(window.location.search)
  const minuteRaw = Number(params.get("minute"))
  return {
    minute: Number.isFinite(minuteRaw) && params.has("minute") ? clampMinute(minuteRaw) : 0,
    run: params.get("run") ?? "",
    date: params.get("date") ?? "",
    house: params.get("house") ?? "",
    policy: params.get("policy") ?? DEFAULT_POLICY,
    view: readView(params.get("view")),
    world: params.get("world") ?? "",
    tab: readWorldTab(params.get("tab")),
    block: params.get("block") ?? "",
    indoor: readIndoor(params.get("indoor")),
    step: params.get("step") ?? "",
  }
}

const initial = readInitial()

export const useTimeStore = create<TimeState>()((set, get) => ({
  minute: initial.minute,
  isPlaying: false,
  playMode: "continuous",
  dwellMs: dwellMsFor(1),
  speed: 1,
  run: initial.run,
  date: initial.date,
  house: initial.house,
  policy: initial.policy,
  view: initial.view,
  world: initial.world,
  tab: initial.tab,
  block: initial.block,
  indoor: initial.indoor,
  step: initial.step,
  selectedMember: null,
  carry: 0,
  stepMinutes: 10,

  advance: (deltaSeconds) => {
    const { isPlaying, speed, minute, carry } = get()
    if (!isPlaying) return
    const exact = carry + deltaSeconds * MINUTES_PER_SECOND_AT_1X * speed
    const whole = Math.floor(exact)
    const next = minute + whole
    if (next >= DAY_MINUTES) {
      set({ minute: DAY_MINUTES, carry: 0, isPlaying: false })
      return
    }
    set({ minute: next, carry: exact - whole })
  },

  setMinute: (minute) => set({ minute: clampMinute(minute), carry: 0 }),

  stepBy: (deltaMinutes) => {
    const next = clampMinute(get().minute + deltaMinutes)
    set({ minute: next, carry: 0 })
  },

  stepOnce: (direction) => {
    const { minute, stepMinutes } = get()
    const next = (stepIndex(minute, stepMinutes) + direction) * stepMinutes
    set({ minute: clampMinute(next), carry: 0 })
  },

  setStepMinutes: (value) => {
    const step = value > 0 ? value : 1
    set({ stepMinutes: step, minute: snapToStep(get().minute, step), carry: 0 })
  },

  setPlaying: (playing) => set({ isPlaying: playing, carry: 0 }),

  setPlayMode: (mode) => set({ playMode: mode }),

  togglePlay: () => {
    const { isPlaying, minute } = get()
    if (!isPlaying && minute >= DAY_MINUTES) {
      set({ minute: 0, carry: 0, isPlaying: true })
      return
    }
    set({ isPlaying: !isPlaying, carry: 0 })
  },

  setSpeed: (speed) => {
    const next = SPEEDS.includes(speed) ? speed : 1
    set({ speed: next, dwellMs: dwellMsFor(next) })
  },

  setRun: (run) => set({ run }),
  setDate: (date) => set({ date }),
  setHouse: (house) => set({ house, selectedMember: null }),
  setPolicy: (policy) => set({ policy }),

  setView: (view) => set({ view }),

  setWorld: (world) =>
    set((state) =>
      state.world === world
        ? { world }
        : { world, run: "", date: "", block: "", house: "", selectedMember: null },
    ),

  setTab: (tab) => set({ tab }),

  setBlock: (block) => set({ block }),

  setIndoor: (indoor) => set({ indoor }),

  setStep: (step) => set({ step }),

  setSelectedMember: (member) => set({ selectedMember: member }),

  setSelection: (selection) => {
    const next: Partial<TimeState> = {}
    if (selection.run !== undefined) next.run = selection.run
    if (selection.date !== undefined) next.date = selection.date
    if (selection.house !== undefined) {
      next.house = selection.house
      next.selectedMember = null
    }
    if (selection.policy !== undefined) next.policy = selection.policy
    set(next)
  },

  reset: () =>
    set({
      minute: 0,
      carry: 0,
      isPlaying: false,
      speed: 1,
      dwellMs: dwellMsFor(1),
      selectedMember: null,
    }),
}))

export const useMinute = () => useTimeStore((state) => state.minute)
export const useIsPlaying = () => useTimeStore((state) => state.isPlaying)
export const useSpeed = () => useTimeStore((state) => state.speed)
export const useSelectedMember = () => useTimeStore((state) => state.selectedMember)
