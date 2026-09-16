import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import {
  cloneWorld,
  createWorld,
  createWorldDistrict,
  deleteWorld,
  deleteWorldDistrict,
  getBuildPreview,
  getBuildState,
  getDistrictHousehold,
  getWorld,
  listDistrictPresets,
  listWorldDistricts,
  listWorlds,
} from "@/api/client"
import type {
  BuildStep,
  BuildStepScope,
  BuildStepStatus,
  DistrictCreateRequest,
  JobInfo,
  WorldCreateRequest,
} from "@/api/types"

export const BUILD_STEP_ORDER: readonly BuildStep[] = ["district", "household", "home"]

export const BUILD_STEP_LABEL: Record<BuildStep, string> = {
  district: "District",
  household: "Household",
  home: "Home",
}

export const BUILD_STEP_SCOPE: Record<BuildStep, BuildStepScope> = {
  district: "district",
  household: "district",
  home: "house",
}

export const BUILD_STEP_HINT: Record<BuildStep, string> = {
  district: "1 LLM call per district, from a preset or a custom prompt.",
  household: "2 LLM calls per household: compose, then adapt to a sampled persona.",
  home: "1 LLM call per household: invent its rooms and appliances.",
}

export const SCOPE_LABEL: Record<BuildStepScope, string> = {
  world: "world-scoped",
  district: "district-scoped",
  house: "household-scoped",
}

export const isBuildStep = (value: string): value is BuildStep =>
  BUILD_STEP_ORDER.some((step) => step === value)

export const isActiveJob = (job: JobInfo): boolean =>
  job.status === "running" || job.status === "queued"

export const worldKeys = {
  list: ["worlds"] as const,
  detail: (world: string) => ["worlds", world] as const,
  districts: (world: string) => ["worlds", world, "districts"] as const,
  build: (world: string, district: string) => ["worlds", world, "build", district] as const,
  buildAll: (world: string) => ["worlds", world, "build"] as const,
  preview: (world: string, step: string, district: string, house: string) =>
    ["worlds", world, "build", step, "preview", district, house] as const,
  districtHousehold: (world: string, district: string, house: string) =>
    ["worlds", world, "districts", district, "houses", house] as const,
  districtPresets: ["district-presets"] as const,
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

  /** Poll fast while a build job for this district is running, otherwise slowly. */
export function useBuildState(world: string, district: string, activeJob: boolean) {
  return useQuery({
    queryKey: worldKeys.build(world, district),
    queryFn: () => getBuildState(world, district.length > 0 ? district : undefined),
    enabled: world.length > 0,
    refetchInterval: activeJob ? 2500 : 15000,
    refetchIntervalInBackground: false,
  })
}

export function useBuildPreview(world: string, step: BuildStep, district: string, house: string) {
  const needsHouse = BUILD_STEP_SCOPE[step] === "house"
  return useQuery({
    queryKey: worldKeys.preview(world, step, district, house),
    queryFn: () =>
      getBuildPreview(
        world,
        step,
        district.length > 0 ? district : undefined,
        house.length > 0 ? house : undefined,
      ),
    enabled: world.length > 0 && (!needsHouse || house.length > 0),
    staleTime: 15_000,
  })
}

export function useDistricts(world: string) {
  return useQuery({
    queryKey: worldKeys.districts(world),
    queryFn: () => listWorldDistricts(world),
    enabled: world.length > 0,
    staleTime: 15_000,
  })
}

export function useDistrictPresets() {
  return useQuery({
    queryKey: worldKeys.districtPresets,
    queryFn: listDistrictPresets,
    staleTime: 300_000,
  })
}

export function useDistrictHousehold(
  world: string,
  district: string,
  house: string,
  enabled: boolean,
) {
  return useQuery({
    queryKey: worldKeys.districtHousehold(world, district, house),
    queryFn: () => getDistrictHousehold(world, district, house),
    enabled: enabled && world.length > 0 && district.length > 0 && house.length > 0,
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
      queryClient.removeQueries({ queryKey: worldKeys.build(world, "") })
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

export function useCreateDistrict(world: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: DistrictCreateRequest) => createWorldDistrict(world, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: worldKeys.districts(world) })
      void queryClient.invalidateQueries({ queryKey: worldKeys.detail(world) })
      void queryClient.invalidateQueries({ queryKey: worldKeys.list })
    },
  })
}

export function useDeleteDistrict(world: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (district: string) => deleteWorldDistrict(world, district),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: worldKeys.districts(world) })
      void queryClient.invalidateQueries({ queryKey: worldKeys.detail(world) })
      void queryClient.invalidateQueries({ queryKey: worldKeys.list })
    },
  })
}

  /** Most recent matching build job: house-scoped steps prefer the current target household. */
export function latestJobFor(
  jobs: JobInfo[],
  world: string,
  district: string,
  step: BuildStep,
  house: string,
): JobInfo | null {
  const matches = jobs.filter(
    (job) =>
      job.kind === "build" &&
      job.world === world &&
      job.step === step &&
      (job.district ?? "") === district,
  )
  if (matches.length === 0) return null
  const scoped =
    BUILD_STEP_SCOPE[step] !== "house" || house.length === 0
      ? matches
      : matches.filter((job) => job.house === house)
  const pool = scoped.length > 0 ? scoped : matches
  return pool.reduce((latest, job) => (job.created_at > latest.created_at ? job : latest))
}

export function latestDistrictJob(
  jobs: JobInfo[],
  world: string,
  district: string,
): JobInfo | null {
  const matches = jobs.filter(
    (job) =>
      job.kind === "build" && job.world === world && (job.district ?? "") === district,
  )
  if (matches.length === 0) return null
  return matches.reduce((latest, job) => (job.created_at > latest.created_at ? job : latest))
}

export function findStepStatus(steps: BuildStepStatus[], step: BuildStep): BuildStepStatus | null {
  return steps.find((item) => item.step === step) ?? null
}
