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
  "当前是 mock 模式（VITE_USE_MOCK=1），不会真正提交。请用 VITE_USE_MOCK=0 启动前端以连接后端。"

const JOB_STATUS_LABEL: Record<JobInfo["status"], string> = {
  queued: "排队中",
  running: "运行中",
  done: "已完成",
  failed: "失败",
  cancelled: "已取消",
}

const JOB_STATUS_CLASS: Record<JobInfo["status"], string> = {
  queued: "border-border-strong text-fg-muted",
  running: "border-energy/50 text-energy",
  done: "border-success/50 text-success",
  failed: "border-danger/50 text-danger",
  cancelled: "border-border-strong text-fg-subtle",
}

const COUNT_FIELD_CLASS =
  "h-7 w-16 rounded-md border-border-strong bg-surface-2 px-2 text-[11px] text-fg focus-visible:border-brand"

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
      ? "目标住户不在该世界的住户列表中。"
      : needsHouse && !missingHouse && houseStatus?.runnable === false
        ? (houseStatus.blocked_reason ?? "该住户当前不可运行。")
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
      ? "请先选择目标住户。"
      : (houseBlocked ?? blockedReason ?? "当前步骤不可运行。")

  const reasonLines = [blockedReason, houseBlocked === blockedReason ? null : houseBlocked].filter(
    (reason): reason is string => reason !== null,
  )

  const statusChip = done
    ? { text: "已完成", className: "border-success/50 text-success" }
    : runnable
      ? { text: "可运行", className: "border-brand/50 text-brand" }
      : { text: "被阻塞", className: "border-danger/50 text-danger" }

  return (
    <section
      className={cn(
        "flex flex-col overflow-hidden rounded-lg border bg-surface transition-colors",
        focused ? "border-brand/50" : "border-border",
      )}
    >
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-3 py-2">
        <span className="num flex size-5 shrink-0 items-center justify-center rounded-sm border border-border-strong text-[10px] text-fg-muted">
          {index + 1}
        </span>
        <span className="text-[12px] font-semibold text-fg">{BUILD_STEP_LABEL[step]}</span>
        <span className="label-latin">{step}</span>
        <Badge variant="outline" className={cn("label-latin", statusChip.className)}>
          {statusChip.text}
        </Badge>
        <span className="label-micro">{needsHouse ? "住户级" : "世界级"}</span>
        <Button
          variant="outline"
          size="xs"
          className="ml-auto"
          onClick={onFocus}
          disabled={!runnable}
          title={
            runnable
              ? `运行「${BUILD_STEP_LABEL[step]}」`
              : (blockedReason ?? houseBlocked ?? "当前步骤不可运行")
          }
        >
          <Play aria-hidden />
          运行
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
            <p className="text-[10px] text-fg-subtle">暂无住户：先运行「类型」。</p>
          ) : (
            <ul className="flex flex-wrap gap-1.5">
              {status.houses.map((item) => (
                <li key={item.house}>
                  <span
                    title={item.blocked_reason ?? undefined}
                    className={cn(
                      "num inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 text-[10px]",
                      item.done
                        ? "border-success/40 text-success"
                        : item.runnable
                          ? "border-border-strong text-fg-muted"
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
              "num rounded-sm border px-1.5 py-px text-[9px]",
              done ? "border-success/40 text-success" : "border-border-strong text-fg-subtle",
            )}
          >
            {done ? "done" : "not done"}
          </span>
          <span
            className={cn(
              "num rounded-sm border px-1.5 py-px text-[9px]",
              runnable ? "border-brand/40 text-brand" : "border-border-strong text-fg-subtle",
            )}
          >
            {runnable ? "runnable" : "blocked"}
          </span>

          {missingHouse ? (
            <span className="text-[10px] text-fg-subtle">选择目标住户后可预览读写路径。</span>
          ) : previewQuery.isPending ? (
            <span className="label-micro">预览载入中…</span>
          ) : previewQuery.isError ? (
            <span className="text-[10px] text-danger">预览读取失败</span>
          ) : (
            <span className="num text-[10px] text-fg-subtle">
              读 {previewQuery.data?.reads.length ?? 0} · 写 {previewQuery.data?.writes.length ?? 0} · 覆盖{" "}
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
              <span className="num text-[10px] text-fg-subtle">最近 {job.id.slice(0, 8)}</span>
            </>
          ) : (
            <span className="text-[10px] text-fg-subtle">尚无运行记录</span>
          )}

          {!focused ? (
            <button
              type="button"
              onClick={onFocus}
              className="label-micro ml-auto transition-colors hover:text-fg"
            >
              展开
            </button>
          ) : null}
        </div>

        {focused ? (
          <div className="flex flex-col gap-3 rounded-md border border-border bg-surface-2 p-3">
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
                  住户类型数量（1–5）
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
                  <p className="rounded-md border border-danger/40 px-3 py-2 text-[11px] text-danger">
                    最近一次失败：{job.error}
                  </p>
                ) : null}
                <div className="flex h-80 min-h-0 flex-col overflow-hidden rounded-md border border-border bg-surface">
                  <StepInspector jobId={job.id} step={job.step} live={isActiveJob(job)} />
                </div>
              </div>
            ) : (
              <p className="text-[11px] text-fg-subtle">
                该步骤还没有运行记录；提交后这里会显示每次 LLM 调用的提示词、响应与耗时。
              </p>
            )}
          </div>
        ) : null}
      </div>
    </section>
  )
}
