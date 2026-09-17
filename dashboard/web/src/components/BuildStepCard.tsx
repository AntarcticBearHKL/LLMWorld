import { useState } from "react"

import { AlertTriangle, CheckCircle2, SlidersHorizontal, XCircle } from "lucide-react"

import { USE_MOCK } from "@/api/client"
import type { BuildStep, BuildStepStatus, JobInfo, JobRequest } from "@/api/types"
import { BuildPreviewList } from "@/components/BuildPreviewList"
import { DistrictPromptFields } from "@/components/DistrictPromptFields"
import { JobSubmitBar } from "@/components/JobSubmitBar"
import { StepInspector } from "@/components/StepInspector"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { errorMessage } from "@/lib/errors"
import { cn } from "@/lib/utils"
import {
  BUILD_STEP_LABEL,
  BUILD_STEP_SCOPE,
  SCOPE_LABEL,
  isActiveJob,
  useBuildPreview,
  useDistrictPresets,
} from "@/hooks/useWorldBuild"

export const MOCK_REASON =
  "Mock mode is on (VITE_USE_MOCK=1), so nothing is submitted. Start the frontend with VITE_USE_MOCK=0 to reach the backend."

const JOB_STATUS_LABEL: Record<JobInfo["status"], string> = {
  queued: "Queued",
  running: "Running",
  done: "Done",
  failed: "Failed",
  cancelled: "Cancelled",
}

const JOB_STATUS_CLASS: Record<JobInfo["status"], string> = {
  queued: "border-border-strong bg-surface-2 text-fg-muted",
  running: "border-energy/40 bg-energy-soft text-energy",
  done: "border-success/40 bg-success/10 text-success",
  failed: "border-danger/40 bg-danger/10 text-danger",
  cancelled: "border-border-strong bg-surface-2 text-fg-subtle",
}

interface BuildStepCardProps {
  world: string
  district: string
  house: string
  step: BuildStep
  index: number
  status: BuildStepStatus | null
  job: JobInfo | null
  focused: boolean
  onFocus: () => void
}

export function BuildStepCard({
  world,
  district,
  house,
  step,
  index,
  status,
  job,
  focused,
  onFocus,
}: BuildStepCardProps) {
  const [preset, setPreset] = useState("")
  const [prompt, setPrompt] = useState("")
  const presetsQuery = useDistrictPresets()

  const scope = status?.scope ?? BUILD_STEP_SCOPE[step]
  const needsHouse = scope === "house"
  const done = status?.done ?? false
  const runnable = status?.runnable ?? false
  const blockedReason = status?.blocked_reason ?? null
  const missingHouse = needsHouse && house.length === 0

  const houseStatus =
    needsHouse && status !== null
      ? (status.houses.find((item) => item.house === house) ?? null)
      : null
  const houseBlocked =
    needsHouse && !missingHouse && houseStatus === null
      ? "The target household is not in this district's household list."
      : needsHouse && !missingHouse && houseStatus?.runnable === false
        ? (houseStatus.blocked_reason ?? "This household is not runnable right now.")
        : null
  const targetRunnable = needsHouse ? houseStatus?.runnable === true : runnable

  const previewQuery = useBuildPreview(world, step, district, house)

  const trimmedPrompt = prompt.trim()
  const payload: JobRequest = { kind: "build", world, district, step }
  if (needsHouse) payload.house = house
  if (step === "district") {
    if (trimmedPrompt.length > 0) payload.prompt = trimmedPrompt
    else if (preset.length > 0) payload.preset = preset
  }

  const disabled = USE_MOCK || !targetRunnable || missingHouse
  const disabledReason = USE_MOCK
    ? MOCK_REASON
    : missingHouse
      ? "Pick a target household first."
      : (houseBlocked ?? blockedReason ?? "This step is not runnable right now.")

  const reasonLines = [blockedReason, houseBlocked === blockedReason ? null : houseBlocked].filter(
    (reason): reason is string => reason !== null,
  )

  const statusChip = done
    ? { text: "Done", className: "border-success/40 bg-success/10 text-success" }
    : runnable
      ? { text: "Runnable", className: "border-brand-ring bg-brand-soft text-fg" }
      : { text: "Blocked", className: "border-danger/40 bg-danger/10 text-danger" }

  return (
    <section
      className={cn(
        "card card-lift flex flex-col overflow-hidden",
        focused ? "border-brand-ring shadow-2" : "hover:border-border-strong",
      )}
    >
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-3.5 py-2.5">
        <span className="num t-micro flex size-5 shrink-0 items-center justify-center rounded-full border border-border-strong bg-surface-2">
          {index + 1}
        </span>
        <span className="t-title">{BUILD_STEP_LABEL[step]}</span>
        <span className="label-latin">{step}</span>
        <Badge variant="outline" className={cn("label-latin", statusChip.className)}>
          {statusChip.text}
        </Badge>
        <span className="label-micro">{SCOPE_LABEL[scope]}</span>
        <Button
          variant="outline"
          size="xs"
          className="ml-auto"
          onClick={onFocus}
          disabled={!runnable}
          title={
            runnable
              ? `Configure "${BUILD_STEP_LABEL[step]}"`
              : (blockedReason ?? houseBlocked ?? "This step is not runnable right now")
          }
        >
          <SlidersHorizontal aria-hidden />
          Configure
        </Button>
      </header>

      <div className="flex flex-col gap-2 px-3 py-2.5">
        {reasonLines.map((reason) => (
          <p key={reason} className="flex items-start gap-1.5 t-caption text-danger">
            <AlertTriangle className="mt-px size-3 shrink-0" aria-hidden />
            {reason}
          </p>
        ))}

        {needsHouse ? (
          status === null || status.houses.length === 0 ? (
            <p className="t-caption">No households in this district yet — run Household first.</p>
          ) : (
            <ul className="flex flex-wrap gap-1.5">
              {status.houses.map((item) => (
                <li key={item.house}>
                  <span
                    title={item.blocked_reason ?? undefined}
                    className={cn(
                      "num t-caption inline-flex items-center gap-1 rounded-full border px-2 py-0.5",
                      item.done
                        ? "border-success/40 bg-success/10 text-success"
                        : item.runnable
                          ? "border-border-strong bg-surface-2 text-fg-muted"
                          : "border-danger/30 text-fg-subtle",
                    )}
                  >
                    {item.house}
                    {item.done ? (
                      <CheckCircle2 className="size-2.5" aria-hidden />
                    ) : item.runnable ? null : (
                      <XCircle className="size-2.5" aria-hidden />
                    )}
                  </span>
                </li>
              ))}
            </ul>
          )
        ) : null}

        <div className="flex flex-wrap items-center gap-2">
          <span
            className={cn(
              "num t-caption rounded-full border px-2 py-px",
              done
                ? "border-success/40 bg-success/10 text-success"
                : "border-border-strong bg-surface-2 text-fg-subtle",
            )}
          >
            {done ? "done" : "not done"}
          </span>
          <span
            className={cn(
              "num t-caption rounded-full border px-2 py-px",
              runnable
                ? "border-brand-ring bg-brand-soft text-fg"
                : "border-border-strong bg-surface-2 text-fg-subtle",
            )}
          >
            {runnable ? "runnable" : "blocked"}
          </span>

          {missingHouse ? (
            <span className="t-caption">Pick a target household to preview read/write paths.</span>
          ) : previewQuery.isPending ? (
            <span className="label-micro">Loading preview…</span>
          ) : previewQuery.isError ? (
            <span className="t-caption text-danger">Failed to load preview</span>
          ) : (
            <span className="num t-body">
              read {previewQuery.data?.reads.length ?? 0} · write{" "}
              {previewQuery.data?.writes.length ?? 0} · overwrite{" "}
              <span
                className={
                  (previewQuery.data?.overwrites.length ?? 0) > 0 ? "text-energy" : undefined
                }
              >
                {previewQuery.data?.overwrites.length ?? 0}
              </span>
            </span>
          )}

          {job !== null ? (
            <>
              <Badge variant="outline" className={cn("label-latin", JOB_STATUS_CLASS[job.status])}>
                {JOB_STATUS_LABEL[job.status]}
              </Badge>
              <span className="num t-caption">latest {job.id.slice(0, 8)}</span>
            </>
          ) : (
            <span className="t-caption">No runs yet</span>
          )}
        </div>

        {focused ? (
          <div className="flex flex-col gap-3 rounded-xl border border-border bg-surface-2 p-3.5">
            <BuildPreviewList
              preview={previewQuery.data}
              isPending={previewQuery.isPending}
              error={previewQuery.isError ? errorMessage(previewQuery.error) : null}
              needsHouse={needsHouse}
              house={house}
            />

            {step === "district" ? (
              <div className="flex flex-col gap-2.5">
                <DistrictPromptFields
                  presets={presetsQuery.data ?? []}
                  presetsPending={presetsQuery.isPending}
                  preset={preset}
                  prompt={prompt}
                  disabled={disabled}
                  onPresetChange={setPreset}
                  onPromptChange={setPrompt}
                />
                {preset.length === 0 && trimmedPrompt.length === 0 ? (
                  <p className="t-caption text-energy">
                    No preset or prompt set — the backend refuses to run the district step with
                    neither.
                  </p>
                ) : null}
              </div>
            ) : null}

            <JobSubmitBar
              key={`${step}-${house}-${preset}-${trimmedPrompt.length > 0 ? "custom" : "none"}`}
              payload={payload}
              disabled={disabled}
              disabledReason={disabledReason}
            />

            {job !== null ? (
              <div className="flex min-h-0 flex-col gap-2">
                {job.error !== null ? (
                  <p className="rounded-xl border border-danger/40 bg-danger/10 px-3 py-2 t-body text-danger">
                    Last failure: {job.error}
                  </p>
                ) : null}
                <div className="flex h-80 min-h-0 flex-col overflow-hidden rounded-xl border border-border bg-surface">
                  <StepInspector jobId={job.id} step={job.step} live={isActiveJob(job)} />
                </div>
              </div>
            ) : (
              <p className="t-body">
                No runs for this step yet; after submitting, each LLM call&apos;s prompt, response and
                latency appear here.
              </p>
            )}
          </div>
        ) : null}
      </div>
    </section>
  )
}
