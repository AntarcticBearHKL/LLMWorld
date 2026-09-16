import { useEffect, useState } from "react"

import { ChevronRight, Loader2, Plus, RefreshCw, Sparkles, Trash2 } from "lucide-react"

import { USE_MOCK } from "@/api/client"
import type { DistrictInfo, JobInfo, JobRequest, WorldInfo } from "@/api/types"
import { MOCK_REASON } from "@/components/BuildStepCard"
import { DistrictPromptFields } from "@/components/DistrictPromptFields"
import { HouseholdPreview } from "@/components/HouseholdPreview"
import { JobSubmitBar } from "@/components/JobSubmitBar"
import { WorldBuilder } from "@/components/WorldBuilder"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useJobs } from "@/hooks/useJobs"
import {
  findStepStatus,
  isActiveJob,
  useBuildState,
  useCreateDistrict,
  useDeleteDistrict,
  useDistrictPresets,
  useDistricts,
} from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { countLabel } from "@/lib/format"
import { cn } from "@/lib/utils"

const FIELD_CLASS = "h-8 px-2.5 text-[14px]"

function NewDistrictForm({ world }: { world: string }) {
  const create = useCreateDistrict(world)
  const [draft, setDraft] = useState("")

  const onCreate = () => {
    const name = draft.trim()
    if (name.length === 0) return
    create.mutate({ name }, { onSuccess: () => setDraft("") })
  }

  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor="new-district-name" className="label-micro text-fg-muted">
        New district
      </Label>
      <div className="flex flex-wrap items-center gap-2">
        <Input
          id="new-district-name"
          value={draft}
          placeholder="3168"
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") onCreate()
          }}
          className={cn(FIELD_CLASS, "num w-40")}
        />
        <Button size="sm" onClick={onCreate} disabled={create.isPending || draft.trim().length === 0}>
          {create.isPending ? <Loader2 className="animate-spin" /> : <Plus />}
          Create district
        </Button>
        <span className="text-[12px] text-fg-subtle">Creating a district is local — no LLM calls.</span>
      </div>
      {create.isError ? (
        <p className="text-[12px] text-danger">Create failed: {errorMessage(create.error)}</p>
      ) : null}
      {create.isSuccess ? (
        <p className="num text-[12px] text-success">
          District {create.data.name}{" "}
          {create.data.created ? "created" : "already existed — nothing changed"}.
        </p>
      ) : null}
    </div>
  )
}

function HouseholdRow({
  world,
  district,
  house,
  homeDone,
  homeRunnable,
  homeBlockedReason,
}: {
  world: string
  district: string
  house: string
  homeDone: boolean
  homeRunnable: boolean
  homeBlockedReason: string | null
}) {
  const [previewOpen, setPreviewOpen] = useState(false)
  const [homeFormOpen, setHomeFormOpen] = useState(false)
  const homePayload: JobRequest = { kind: "build", world, district, step: "home", house }

  return (
    <div className="flex flex-col rounded-xl border border-border bg-surface-2">
      <div className="flex flex-wrap items-center gap-2 px-3 py-2">
        <button
          type="button"
          aria-expanded={previewOpen}
          onClick={() => setPreviewOpen((open) => !open)}
          className="num flex items-center gap-1.5 text-[13px] text-fg transition-colors hover:text-brand"
        >
          <ChevronRight
            className={cn("size-3.5 shrink-0 transition-transform", previewOpen && "rotate-90")}
            aria-hidden
          />
          {house}
        </button>
        <span
          className={cn(
            "num rounded-full border px-2 py-px text-[12px]",
            homeDone
              ? "border-success/40 bg-success/10 text-success"
              : "border-border-strong bg-surface-2 text-fg-subtle",
          )}
        >
          {homeDone ? "home ready" : "no home yet"}
        </span>
        <span className="label-micro ml-auto">{previewOpen ? "Hide" : "Preview"}</span>
        {!homeDone ? (
          <Button
            variant="outline"
            size="xs"
            disabled={!homeRunnable}
            onClick={() => setHomeFormOpen((open) => !open)}
          >
            Generate home
          </Button>
        ) : null}
      </div>

      {homeFormOpen && !homeDone ? (
        <div className="px-3 pb-3">
          <JobSubmitBar
            key={`${house}-home`}
            payload={homePayload}
            disabled={USE_MOCK || !homeRunnable}
            disabledReason={
              USE_MOCK
                ? MOCK_REASON
                : (homeBlockedReason ?? "This household is not runnable right now.")
            }
          />
        </div>
      ) : null}

      {previewOpen ? (
        <div className="border-t border-border px-3 py-2.5">
          {homeDone ? (
            <HouseholdPreview world={world} district={district} house={house} />
          ) : (
            <p className="text-[12px] text-fg-subtle">
              No home for {house} yet — generate its rooms and appliances to preview them here.
            </p>
          )}
        </div>
      ) : null}
    </div>
  )
}

function DistrictCard({ world, district, jobs }: { world: string; district: DistrictInfo; jobs: JobInfo[] }) {
  const districtJobs = jobs.filter((job) => (job.district ?? "") === district.name)
  const activeJob = districtJobs.some(isActiveJob)
  const buildQuery = useBuildState(world, district.name, activeJob)
  const presetsQuery = useDistrictPresets()
  const remove = useDeleteDistrict(world)

  const [armed, setArmed] = useState(false)
  const [descriptionFormOpen, setDescriptionFormOpen] = useState(false)
  const [descriptionExpanded, setDescriptionExpanded] = useState(false)
  const [preset, setPreset] = useState("")
  const [prompt, setPrompt] = useState("")
  const [householdFormOpen, setHouseholdFormOpen] = useState(false)
  const [stepsOpen, setStepsOpen] = useState(false)

  useEffect(() => {
    if (!armed) return
    const timer = window.setTimeout(() => setArmed(false), 6000)
    return () => window.clearTimeout(timer)
  }, [armed])

  const buildState = buildQuery.data
  const districtStep = buildState === undefined ? null : findStepStatus(buildState.steps, "district")
  const householdStep =
    buildState === undefined ? null : findStepStatus(buildState.steps, "household")
  const homeStep = buildState === undefined ? null : findStepStatus(buildState.steps, "home")
  const houses = buildState?.houses ?? []
  const districtRunnable = districtStep?.runnable ?? false
  const householdRunnable = householdStep?.runnable ?? false
  const homeStatusFor = (house: string) => homeStep?.houses.find((item) => item.house === house) ?? null

  const trimmedPrompt = prompt.trim()
  const descriptionPayload: JobRequest = {
    kind: "build",
    world,
    district: district.name,
    step: "district",
  }
  if (trimmedPrompt.length > 0) descriptionPayload.prompt = trimmedPrompt
  else if (preset.length > 0) descriptionPayload.preset = preset

  const householdPayload: JobRequest = {
    kind: "build",
    world,
    district: district.name,
    step: "household",
  }

  return (
    <article className="card card-lift flex flex-col overflow-hidden">
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-3.5 py-2.5">
        <span className="num text-[15px] font-semibold tracking-[-0.01em] text-fg">
          {district.name}
        </span>
        <span
          className={cn(
            "num rounded-full border px-2 py-px text-[12px]",
            district.has_description
              ? "border-success/40 bg-success/10 text-success"
              : "border-border-strong bg-surface-2 text-fg-subtle",
          )}
        >
          {district.has_description ? "described" : "no description"}
        </span>
        <span className="num text-[12px] text-fg-subtle">
          {countLabel(district.house_count, "household")}
        </span>

        <span className="ml-auto flex items-center gap-1">
          <Button
            variant="outline"
            size="xs"
            disabled={!districtRunnable}
            title={
              districtRunnable
                ? undefined
                : (districtStep?.blocked_reason ?? "This district is not runnable right now.")
            }
            onClick={() => setDescriptionFormOpen((open) => !open)}
          >
            <Sparkles aria-hidden />
            {district.has_description ? "Regenerate description" : "Generate description"}
          </Button>
          <Button
            variant="ghost"
            size="xs"
            disabled={remove.isPending}
            title={
              armed
                ? "Click again to delete"
                : "Delete this district (moves to output/_trash/, recoverable)"
            }
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => {
              if (!armed) {
                setArmed(true)
                return
              }
              remove.mutate(district.name)
            }}
            className={cn(armed && "bg-danger/10 text-danger hover:bg-danger/15 hover:text-danger")}
          >
            {remove.isPending ? <Loader2 className="animate-spin" /> : <Trash2 />}
            {armed ? "Confirm delete" : "Delete"}
          </Button>
        </span>
      </header>

      <div className="flex flex-col gap-3 px-3.5 py-3">
        <div className="flex flex-col gap-2">
          <span className="label-micro">Description</span>
          {!district.has_description ? (
            <p className="text-[13px] text-fg-subtle">
              No description yet — generate one from a preset or write a custom prompt.
            </p>
          ) : district.description.length === 0 ? (
            <p className="text-[13px] text-fg-subtle">
              The description file for {district.name} exists, but its text is not inlined here.
            </p>
          ) : (
            <div className="flex flex-col items-start gap-1.5">
              <p
                className={cn(
                  "text-[13px] leading-relaxed whitespace-pre-wrap text-fg-muted",
                  !descriptionExpanded && "line-clamp-3",
                )}
              >
                {district.description}
              </p>
              <button
                type="button"
                onClick={() => setDescriptionExpanded((open) => !open)}
                className="label-micro transition-colors hover:text-fg"
              >
                {descriptionExpanded ? "Collapse" : "Expand"}
              </button>
            </div>
          )}
        </div>

        {descriptionFormOpen ? (
          <div className="flex flex-col gap-3 rounded-xl border border-border bg-surface-2 p-3.5">
            <DistrictPromptFields
              presets={presetsQuery.data ?? []}
              presetsPending={presetsQuery.isPending}
              preset={preset}
              prompt={prompt}
              disabled={!districtRunnable}
              onPresetChange={setPreset}
              onPromptChange={setPrompt}
            />
            <JobSubmitBar
              key={`${district.name}-${preset}-${trimmedPrompt.length > 0 ? "custom" : "none"}`}
              payload={descriptionPayload}
              disabled={USE_MOCK || !districtRunnable}
              disabledReason={
                USE_MOCK
                  ? MOCK_REASON
                  : (districtStep?.blocked_reason ?? "This district is not runnable right now.")
              }
            />
          </div>
        ) : null}

        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="label-micro">Households</span>
            <span className="num text-[12px] text-fg-subtle">{houses.length}</span>
            <Button
              variant="outline"
              size="xs"
              className="ml-auto"
              disabled={!householdRunnable}
              title={
                householdRunnable
                  ? undefined
                  : (householdStep?.blocked_reason ?? "Add the district description first.")
              }
              onClick={() => setHouseholdFormOpen((open) => !open)}
            >
              <Plus aria-hidden />
              Add household
            </Button>
          </div>

          {householdFormOpen ? (
            <JobSubmitBar
              key={`${district.name}-household`}
              payload={householdPayload}
              disabled={USE_MOCK || !householdRunnable}
              disabledReason={
                USE_MOCK
                  ? MOCK_REASON
                  : (householdStep?.blocked_reason ?? "Add the district description first.")
              }
            />
          ) : null}

          {buildQuery.isPending ? (
            <p className="text-[12px] text-fg-subtle">Loading households…</p>
          ) : buildQuery.isError ? (
            <p className="text-[12px] text-fg-subtle">
              Households unavailable: {errorMessage(buildQuery.error)}
            </p>
          ) : houses.length === 0 ? (
            <p className="text-[12px] text-fg-subtle">No households in this district yet.</p>
          ) : (
            <ul className="flex flex-col gap-2">
              {houses.map((house) => {
                const homeStatus = homeStatusFor(house)
                return (
                  <li key={house}>
                    <HouseholdRow
                      world={world}
                      district={district.name}
                      house={house}
                      homeDone={homeStatus?.done ?? false}
                      homeRunnable={homeStatus?.runnable ?? false}
                      homeBlockedReason={homeStatus?.blocked_reason ?? homeStep?.blocked_reason ?? null}
                    />
                  </li>
                )
              })}
            </ul>
          )}
        </div>

        <div className="flex flex-col gap-2">
          <button
            type="button"
            aria-expanded={stepsOpen}
            onClick={() => setStepsOpen((open) => !open)}
            className="label-micro flex items-center gap-1.5 self-start transition-colors hover:text-fg"
          >
            <ChevronRight
              className={cn("size-3.5 transition-transform", stepsOpen && "rotate-90")}
              aria-hidden
            />
            Step runner · district → household → home → assemble
          </button>
          {stepsOpen ? <WorldBuilder world={world} district={district.name} /> : null}
        </div>

        {remove.isError ? (
          <p className="text-[12px] text-danger">Delete failed: {errorMessage(remove.error)}</p>
        ) : null}
        {remove.isSuccess ? (
          <p className="min-w-0 text-[12px] text-fg-subtle">
            {remove.data.deleted
              ? `Deleted ${remove.data.name} — recoverable from output/_trash/`
              : `Nothing deleted for ${remove.data.name}`}
            {remove.data.moved_to !== null ? (
              <span className="num ml-1 inline-block max-w-full truncate align-bottom" title={remove.data.moved_to}>
                {remove.data.moved_to}
              </span>
            ) : null}
          </p>
        ) : null}
      </div>
    </article>
  )
}

export function WorldDistricts({ info }: { info: WorldInfo }) {
  const world = info.world_id
  const districtsQuery = useDistricts(world)
  const jobsQuery = useJobs()
  const jobs = jobsQuery.data ?? []
  const worldJobs = jobs.filter((job) => job.kind === "build" && job.world === world)
  const districts = districtsQuery.data ?? []

  return (
    <section className="card flex min-h-0 flex-1 flex-col overflow-hidden">
      <header className="flex shrink-0 flex-col gap-2.5 border-b border-border px-3.5 py-3">
        <div className="flex items-center gap-2">
          <span className="text-[15px] font-bold tracking-[-0.01em] text-fg">
            Districts{" "}
            <span className="num text-[14px] font-medium text-fg-muted">{districts.length}</span>
          </span>
          <Button
            variant="ghost"
            size="icon-sm"
            className="ml-auto"
            aria-label="Refresh districts"
            onClick={() => void districtsQuery.refetch()}
          >
            <RefreshCw />
          </Button>
        </div>
        <p className="label-micro">
          {countLabel(districts.length, "district")} ·{" "}
          {countLabel(info.houses.length, "household")} in {world}
        </p>
        <NewDistrictForm world={world} />
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {districtsQuery.isPending ? (
          <p className="px-1 py-4 text-[13px] text-fg-subtle">Loading districts…</p>
        ) : districtsQuery.isError ? (
          <div className="flex flex-col items-start gap-2 px-1 py-4">
            <p className="text-[13px] text-danger">
              Failed to load districts: {errorMessage(districtsQuery.error)}
            </p>
            <Button variant="outline" size="xs" onClick={() => void districtsQuery.refetch()}>
              Retry
            </Button>
          </div>
        ) : districts.length === 0 ? (
          <div className="flex flex-col gap-1.5 px-1 py-4">
            <p className="text-[15px] font-semibold text-fg">No districts yet</p>
            <p className="text-[13px] leading-relaxed text-fg-muted">
              Add a district above to start building this world: name it, generate its description,
              then add households and generate their homes.
            </p>
          </div>
        ) : (
          <ul className="flex flex-col gap-3">
            {districts.map((district) => (
              <li key={district.name} className="min-w-0">
                <DistrictCard world={world} district={district} jobs={worldJobs} />
              </li>
            ))}
          </ul>
        )}

        {jobsQuery.isError ? (
          <p className="px-1 pt-3 text-[12px] text-danger">
            Failed to load jobs; recent run status may be incomplete: {errorMessage(jobsQuery.error)}
          </p>
        ) : null}
      </div>
    </section>
  )
}
