import { useQuery } from "@tanstack/react-query"

import {
  getDayReplay,
  getHousehold,
  getRunMeta,
  getSnapshot,
  getStages,
  listRuns,
} from "@/api/client"
import { useTimeStore } from "@/store/time"

export const queryKeys = {
  runs: ["runs"] as const,
  runMeta: (run: string) => ["run-meta", run] as const,
  household: (run: string, house: string) => ["household", run, house] as const,
  replay: (run: string, date: string, house: string, policy: string) =>
    ["replay", run, date, house, policy] as const,
  snapshot: (run: string, date: string, minute: number, policy: string) =>
    ["snapshot", run, date, minute, policy] as const,
  stages: (run: string, date: string, house: string, member: string) =>
    ["stages", run, date, house, member] as const,
}

export const bucketMinute = (minute: number, bucket: number): number =>
  Math.min(1440, Math.floor(minute / bucket) * bucket)

export function useRuns() {
  return useQuery({ queryKey: queryKeys.runs, queryFn: listRuns, staleTime: 60_000 })
}

export function useRunMeta(run: string) {
  return useQuery({
    queryKey: queryKeys.runMeta(run),
    queryFn: () => getRunMeta(run),
    enabled: run.length > 0,
    staleTime: 300_000,
  })
}

export function useHousehold(run: string, house: string) {
  return useQuery({
    queryKey: queryKeys.household(run, house),
    queryFn: () => getHousehold(run, house),
    enabled: run.length > 0 && house.length > 0,
    staleTime: 300_000,
  })
}

export function useSelection() {
  const run = useTimeStore((state) => state.run)
  const date = useTimeStore((state) => state.date)
  const house = useTimeStore((state) => state.house)
  const policy = useTimeStore((state) => state.policy)
  return { run, date, house, policy }
}

export function useDayReplay() {
  const { run, date, house, policy } = useSelection()
  const enabled = run.length > 0 && date.length > 0 && house.length > 0
  return useQuery({
    queryKey: queryKeys.replay(run, date, house, policy),
    queryFn: () => getDayReplay(run, date, house, policy),
    enabled,
    staleTime: 300_000,
  })
}

export function useSnapshot() {
  const { run, date, policy } = useSelection()
  const stepMinutes = useTimeStore((state) => state.stepMinutes)
  const rawMinute = useTimeStore((state) => state.minute)
  const minute = bucketMinute(rawMinute, stepMinutes)
  const enabled = run.length > 0 && date.length > 0
  return useQuery({
    queryKey: queryKeys.snapshot(run, date, minute, policy),
    queryFn: () => getSnapshot(run, date, minute, policy),
    enabled,
    staleTime: 300_000,
    placeholderData: (previous) => previous,
  })
}

export function useStages(member: string | null) {
  const { run, date, house } = useSelection()
  const enabled = member !== null && run.length > 0 && date.length > 0 && house.length > 0
  return useQuery({
    queryKey: queryKeys.stages(run, date, house, member ?? ""),
    queryFn: () => getStages(run, date, house, member ?? ""),
    enabled,
    staleTime: 300_000,
  })
}
