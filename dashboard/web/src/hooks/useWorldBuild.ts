import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import {
  cloneWorld,
  createWorld,
  deleteWorld,
  getBuildPreview,
  getBuildState,
  getWorld,
  listWorlds,
} from "@/api/client"
import type { BuildStep, BuildStepStatus, JobInfo, WorldCreateRequest } from "@/api/types"

export const BUILD_STEP_ORDER: readonly BuildStep[] = ["types", "personas", "household", "assemble"]

export const BUILD_STEP_LABEL: Record<BuildStep, string> = {
  types: "Types",
  personas: "Personas",
  household: "Household",
  assemble: "Assemble",
}

export const BUILD_STEP_SCOPE: Record<BuildStep, "world" | "house"> = {
  types: "world",
  personas: "house",
  household: "house",
  assemble: "house",
}

export const isBuildStep = (value: string): value is BuildStep =>
  BUILD_STEP_ORDER.some((step) => step === value)

export const isActiveJob = (job: JobInfo): boolean =>
  job.status === "running" || job.status === "queued"

export const worldKeys = {
  list: ["worlds"] as const,
  detail: (world: string) => ["worlds", world] as const,
  build: (world: string) => ["worlds", world, "build"] as const,
  preview: (world: string, step: string, house: string) =>
    ["worlds", world, "build", step, "preview", house] as const,
}

export function useWorlds() {
  return useQuery({ queryKey: worldKeys.list, queryFn: listWorlds, staleTime: 300_000 })
}

export function useWorld(world: string) {
  return useQuery({
    queryKey: worldKeys.detail(world),
    queryFn: () => getWorld(world),
    enabled: world.length > 0,
    staleTime: 30_000,
  })
}

/** 有该世界的构建作业在跑就快轮询，否则慢轮询。 */
export function useBuildState(world: string, activeJob: boolean) {
  return useQuery({
    queryKey: worldKeys.build(world),
    queryFn: () => getBuildState(world),
    enabled: world.length > 0,
    refetchInterval: activeJob ? 2500 : 15000,
    refetchIntervalInBackground: false,
  })
}

export function useBuildPreview(world: string, step: BuildStep, house: string) {
  const needsHouse = BUILD_STEP_SCOPE[step] === "house"
  return useQuery({
    queryKey: worldKeys.preview(world, step, house),
    queryFn: () => getBuildPreview(world, step, house.length > 0 ? house : undefined),
    enabled: world.length > 0 && (!needsHouse || house.length > 0),
    staleTime: 15_000,
  })
}

export function useCreateWorld() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: WorldCreateRequest) => createWorld(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: worldKeys.list })
    },
  })
}

export function useDeleteWorld() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (world: string) => deleteWorld(world),
    onSuccess: (_result, world) => {
      void queryClient.invalidateQueries({ queryKey: worldKeys.list })
      queryClient.removeQueries({ queryKey: worldKeys.build(world) })
    },
  })
}

export function useCloneWorld() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ world, newId }: { world: string; newId: string }) =>
      cloneWorld(world, { new_id: newId }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: worldKeys.list })
    },
  })
}

/** 最近一次匹配的构建作业：住户级步骤优先匹配当前目标住户。 */
export function latestJobFor(
  jobs: JobInfo[],
  world: string,
  step: BuildStep,
  house: string,
): JobInfo | null {
  const matches = jobs.filter(
    (job) => job.kind === "build" && job.world === world && job.step === step,
  )
  if (matches.length === 0) return null
  const scoped =
    BUILD_STEP_SCOPE[step] === "world" || house.length === 0
      ? matches
      : matches.filter((job) => job.house === house)
  const pool = scoped.length > 0 ? scoped : matches
  return pool.reduce((latest, job) => (job.created_at > latest.created_at ? job : latest))
}

export function findStepStatus(steps: BuildStepStatus[], step: BuildStep): BuildStepStatus | null {
  return steps.find((item) => item.step === step) ?? null
}
