import { useEffect, useRef } from "react"

import { useQueryClient } from "@tanstack/react-query"
import { Hammer, RefreshCw } from "lucide-react"

import { ApiError } from "@/api/client"
import { BuildStepCard } from "@/components/BuildStepCard"
import { Button } from "@/components/ui/button"
import { useJobs } from "@/hooks/useJobs"
import {
  BUILD_STEP_HINT,
  BUILD_STEP_LABEL,
  BUILD_STEP_ORDER,
  findStepStatus,
  isActiveJob,
  isBuildStep,
  latestJobFor,
  useBuildState,
  worldKeys,
} from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

interface WorldBuilderProps {
  world: string
  district: string
}

export function WorldBuilder({ world, district }: WorldBuilderProps) {
  const step = useTimeStore((state) => state.step)
  const house = useTimeStore((state) => state.house)
  const setStep = useTimeStore((state) => state.setStep)
  const setHouse = useTimeStore((state) => state.setHouse)
  const queryClient = useQueryClient()
  const jobsQuery = useJobs()
  const jobs = jobsQuery.data ?? []

  const districtJobs = jobs.filter(
    (job) => job.kind === "build" && job.world === world && (job.district ?? "") === district,
  )
  const activeJob = districtJobs.some(isActiveJob)
  const buildQuery = useBuildState(world, district, activeJob)
  const buildState = buildQuery.data

  const jobSignature = districtJobs.map((job) => `${job.id}:${job.status}`).join("|")
  const previousSignature = useRef(jobSignature)
  useEffect(() => {
    if (previousSignature.current === jobSignature) return
    previousSignature.current = jobSignature
    void queryClient.invalidateQueries({ queryKey: worldKeys.buildAll(world) })
  }, [jobSignature, world, queryClient])

  useEffect(() => {
    if (isBuildStep(step)) return
    if (buildState === undefined) return
    const pending = BUILD_STEP_ORDER.find(
      (item) => findStepStatus(buildState.steps, item)?.done === false,
    )
    setStep(pending ?? "home")
  }, [step, buildState, setStep])

  useEffect(() => {
    if (buildState === undefined) return
    if (buildState.houses.includes(house)) return
    const first = buildState.houses[0]
    if (first === undefined) return
    setHouse(first)
  }, [buildState, house, setHouse])

  return (
    <section className="card flex flex-col overflow-hidden">
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-3.5 py-2.5">
        <Hammer className="size-4 shrink-0 text-brand" aria-hidden />
        <span className="text-[15px] font-bold tracking-[-0.01em] text-fg">Build</span>
        <span className="num text-[13px] text-fg-muted">{district}</span>
        {buildState !== undefined ? (
          <span className="label-micro">
            {buildState.houses.length} households ·{" "}
            {buildState.exists ? "world directory ready" : "world directory missing"}
          </span>
        ) : null}
        <Button
          variant="ghost"
          size="icon-sm"
          className="ml-auto"
          aria-label="Refresh build state"
          onClick={() => void buildQuery.refetch()}
        >
          <RefreshCw />
        </Button>
      </header>

      {buildQuery.isPending ? (
        <p className="px-3.5 py-4 text-[13px] text-fg-subtle">Loading build state…</p>
      ) : buildQuery.isError ? (
        <div className="flex flex-col items-start gap-2 px-3.5 py-4">
          <p className="text-[13px] text-danger">
            {buildQuery.error instanceof ApiError && buildQuery.error.status === 404
              ? "World or district missing: "
              : "Failed to load build state: "}
            {errorMessage(buildQuery.error)}
          </p>
          <Button variant="outline" size="xs" onClick={() => void buildQuery.refetch()}>
            Retry
          </Button>
        </div>
      ) : buildState === undefined ? (
        <p className="px-3.5 py-4 text-[13px] text-fg-subtle">Loading build state…</p>
      ) : (
        <div className="flex flex-col gap-3 p-3.5">
          <div className="flex flex-wrap items-center gap-2">
            <span className="label-micro">Target household</span>
            {buildState.houses.length === 0 ? (
              <span className="text-[13px] text-fg-subtle">
                No households in this district yet — run Household first.
              </span>
            ) : (
              buildState.houses.map((item) => (
                <button
                  key={item}
                  type="button"
                  aria-pressed={house === item}
                  onClick={() => setHouse(item)}
                  className={cn(
                    "num text-[12px] transition-colors",
                    house === item
                      ? "chip chip-active"
                      : "chip hover:border-border-strong hover:bg-item-hover hover:text-fg",
                  )}
                >
                  {item}
                </button>
              ))
            )}
            {house.length > 0 && !buildState.houses.includes(house) ? (
              <span className="num text-[12px] text-energy">{house} is not in {district}</span>
            ) : null}
          </div>

          {BUILD_STEP_ORDER.map((item, index) => (
            <BuildStepCard
              key={item}
              world={world}
              district={district}
              house={house}
              step={item}
              index={index}
              status={findStepStatus(buildState.steps, item)}
              job={latestJobFor(jobs, world, district, item, house)}
              focused={step === item}
              onFocus={() => setStep(item)}
            />
          ))}

          {jobsQuery.isError ? (
            <p className="text-[12px] text-danger">
              Failed to load jobs; recent run status may be incomplete:{" "}
              {errorMessage(jobsQuery.error)}
            </p>
          ) : null}

          <div className="flex flex-col gap-2 rounded-xl border border-border bg-surface-2 px-3.5 py-3">
            <dl className="flex flex-col gap-1">
              {BUILD_STEP_ORDER.map((item) => (
                <div key={item} className="flex flex-wrap items-baseline gap-2">
                  <dt className="label-latin w-24 shrink-0">{BUILD_STEP_LABEL[item]}</dt>
                  <dd className="text-[12px] text-fg-subtle">{BUILD_STEP_HINT[item]}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      )}
    </section>
  )
}
