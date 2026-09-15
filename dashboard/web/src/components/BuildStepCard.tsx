import { useState } from "react"

import { AlertTriangle, CheckCircle2, Play, XCircle } from "lucide-react"

import { USE_MOCK } from "@/api/client"
import type { BuildStep, BuildStepStatus, JobInfo, JobRequest } from "@/api/types"
import { BuildPreviewList } from "@/components/BuildPreviewList"
import { JobSubmitBar } from "@/components/JobSubmitBar"
import { StepInspector } from "@/components/StepInspector"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { errorMessage } from "@/lib/errors"
import { cn } from "@/lib/utils"
import {
  BUILD_STEP_LABEL,
  BUILD_STEP_SCOPE,
  isActiveJob,
  useBuildPreview,
} from "@/hooks/useWorldBuild"

const MOCK_REASON =
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

const COUNT_FIELD_CLASS = "h-7 w-16 px-2 text-[11px]"

interface BuildStepCardProps {
  world: string
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
  house,
  step,
  index,
  status,
  job,
  focused,
  onFocus,
}: BuildStepCardProps) {
  const [typeCount, setTypeCount] = useState(1)

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
      ? "The target household is not in this world's household list."
      : needsHouse && !missingHouse && houseStatus?.runnable === false
        ? (houseStatus.blocked_reason ?? "This household is not runnable right now.")
        : null
  const targetRunnable = needsHouse ? houseStatus?.runnable === true : runnable

  const previewQuery = useBuildPreview(world, step, needsHouse ? house : "")

  const payload: JobRequest =
    step === "types"
      ? { kind: "build", world, step, count: typeCount }
      : { kind: "build", world, step, house }

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
        <span className="num flex size-5 shrink-0 items-center justify-center rounded-full border border-border-strong bg-surface-2 text-[10px] text-fg-muted">
          {index + 1}
        </span>
        <span className="text-[13px] font-semibold text-fg">{BUILD_STEP_LABEL[step]}</span>
        <span className="label-latin">{step}</span>
        <Badge variant="outline" className={cn("label-latin", statusChip.className)}>
          {statusChip.text}
        </Badge>
        <span className="label-micro">{needsHouse ? "household-scoped" : "world-scoped"}</span>
        <Button
          variant="outline"
          size="xs"
          className="ml-auto"
          onClick={onFocus}
          disabled={!runnable}
          title={
            runnable
              ? `Run "${BUILD_STEP_LABEL[step]}"`
              : (blockedReason ?? houseBlocked ?? "This step is not runnable right now")
          }
        >
          <Play aria-hidden />
          Run
        </Button>
      </header>

      <div className="flex flex-col gap-2 px-3 py-2.5">
        {reasonLines.map((reason) => (
          <p key={reason} className="flex items-start gap-1.5 text-[10px] text-danger">
            <AlertTriangle className="mt-px size-3 shrink-0" aria-hidden />
            {reason}
          </p>
        ))}

        {needsHouse ? (
          status === null || status.houses.length === 0 ? (
            <p className="text-[10px] text-fg-subtle">No households yet — run Types first.</p>
          ) : (
            <ul className="flex flex-wrap gap-1.5">
              {status.houses.map((item) => (
                <li key={item.house}>
                  <span
                    title={item.blocked_reason ?? undefined}
                    className={cn(
                      "num inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px]",
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
              "num rounded-full border px-2 py-px text-[9px]",
              done
                ? "border-success/40 bg-success/10 text-success"
                : "border-border-strong bg-surface-2 text-fg-subtle",
            )}
          >
            {done ? "done" : "not done"}
          </span>
          <span
            className={cn(
              "num rounded-full border px-2 py-px text-[9px]",
              runnable
                ? "border-brand-ring bg-brand-soft text-fg"
                : "border-border-strong bg-surface-2 text-fg-subtle",
            )}
          >
            {runnable ? "runnable" : "blocked"}
          </span>

          {missingHouse ? (
            <span className="text-[10px] text-fg-subtle">
              Pick a target household to preview read/write paths.
            </span>
          ) : previewQuery.isPending ? (
            <span className="label-micro">Loading preview…</span>
          ) : previewQuery.isError ? (
            <span className="text-[10px] text-danger">Failed to load preview</span>
          ) : (
            <span className="num text-[10px] text-fg-subtle">
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
              <span className="num text-[10px] text-fg-subtle">latest {job.id.slice(0, 8)}</span>
            </>
          ) : (
            <span className="text-[10px] text-fg-subtle">No runs yet</span>
          )}

          {!focused ? (
            <button
              type="button"
              onClick={onFocus}
              className="label-micro ml-auto transition-colors hover:text-fg"
            >
              Expand
            </button>
          ) : null}
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

            {step === "types" ? (
              <div className="flex items-center gap-2">
                <Label htmlFor={`build-count-${step}`} className="label-micro">
                  Household type count (1–5)
                </Label>
                <Input
                  id={`build-count-${step}`}
                  type="number"
                  min={1}
                  max={5}
                  value={typeCount}
                  onChange={(event) => {
                    const next = Number(event.target.value)
                    setTypeCount(Number.isFinite(next) ? Math.min(5, Math.max(1, Math.trunc(next))) : 1)
                  }}
                  className={COUNT_FIELD_CLASS}
                />
              </div>
            ) : null}

            <JobSubmitBar
              key={`${step}-${house}-${String(typeCount)}`}
              payload={payload}
              disabled={disabled}
              disabledReason={disabledReason}
            />

            {job !== null ? (
              <div className="flex min-h-0 flex-col gap-2">
                {job.error !== null ? (
                  <p className="rounded-xl border border-danger/40 bg-danger/10 px-3 py-2 text-[11px] text-danger">
                    Last failure: {job.error}
                  </p>
                ) : null}
                <div className="flex h-80 min-h-0 flex-col overflow-hidden rounded-xl border border-border bg-surface">
                  <StepInspector jobId={job.id} step={job.step} live={isActiveJob(job)} />
                </div>
              </div>
            ) : (
              <p className="text-[11px] text-fg-subtle">
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
