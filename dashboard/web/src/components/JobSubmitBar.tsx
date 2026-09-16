import { useState } from "react"

import { AlertTriangle, CheckCircle2, Loader2, Send } from "lucide-react"

import type { JobRequest } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { useCreateJob, useEstimateJob } from "@/hooks/useJobs"
import { cn } from "@/lib/utils"

interface JobSubmitBarProps {
  payload: JobRequest
  disabled?: boolean
  disabledReason?: string
}

/**
 * Shared guardrail: estimate first, tick to confirm, then submit.
 * Submission is blocked until both steps are done, so a stray click cannot spend credits.
 */
export function JobSubmitBar({ payload, disabled = false, disabledReason }: JobSubmitBarProps) {
  const estimate = useEstimateJob()
  const create = useCreateJob()
  const [confirmed, setConfirmed] = useState(false)

  const estimated = estimate.data !== undefined
  const canSubmit = !disabled && estimated && confirmed && !create.isPending

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-border bg-surface-2 px-4 py-3.5">
      <div className="flex flex-wrap items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => estimate.mutate(payload)}
          disabled={disabled || estimate.isPending}
        >
          {estimate.isPending ? <Loader2 className="animate-spin" /> : null}
          Estimate LLM calls
        </Button>

        {estimate.data !== undefined ? (
          <span className="text-[13px] text-fg-muted">
            Estimated <span className="num text-energy">{estimate.data.estimated_calls}</span> LLM
            calls · {estimate.data.detail}
          </span>
        ) : (
          <span className="text-[13px] text-fg-subtle">
            Estimate first, then confirm the cost before submitting.
          </span>
        )}
      </div>

      <div className="flex items-center gap-2.5">
        <Switch
          id="job-confirm"
          checked={confirmed}
          onCheckedChange={setConfirmed}
          disabled={!estimated}
        />
        <Label htmlFor="job-confirm" className="text-[13px] text-fg-muted">
          I understand this run calls the LLM and spends API credits
        </Label>
      </div>

      {disabled && disabledReason !== undefined ? (
        <p className="flex items-center gap-1.5 text-[12px] text-energy">
          <AlertTriangle className="size-3" aria-hidden />
          {disabledReason}
        </p>
      ) : null}

      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" onClick={() => create.mutate({ ...payload, confirm: true })} disabled={!canSubmit}>
          {create.isPending ? <Loader2 className="animate-spin" /> : <Send />}
          Submit job
        </Button>
        {create.isSuccess ? (
          <span className="flex items-center gap-1.5 text-[13px] text-success">
            <CheckCircle2 className="size-3" aria-hidden />
            Submitted: <span className="num">{create.data.job.id.slice(0, 8)}</span>
          </span>
        ) : null}
        {create.isError ? (
          <span className={cn("text-[13px] text-danger")}>
            Submit failed: {create.error instanceof Error ? create.error.message : "Unknown error"}
          </span>
        ) : null}
      </div>
    </div>
  )
}
