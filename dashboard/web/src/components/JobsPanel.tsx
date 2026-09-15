import { useState } from "react"

import { RefreshCw, X } from "lucide-react"

import { ApiError, cancelJob } from "@/api/client"
import type { JobInfo } from "@/api/types"
import { StepInspector } from "@/components/StepInspector"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useJobLog, useJobs } from "@/hooks/useJobs"
import { cn } from "@/lib/utils"

const STATUS_LABEL: Record<JobInfo["status"], string> = {
  queued: "排队中",
  running: "运行中",
  done: "已完成",
  failed: "失败",
  cancelled: "已取消",
}

const STATUS_CLASS: Record<JobInfo["status"], string> = {
  queued: "border-border-strong text-fg-muted",
  running: "border-energy/50 bg-energy-soft text-energy",
  done: "border-success/50 text-success",
  failed: "border-danger/50 text-danger",
  cancelled: "border-border-strong text-fg-subtle",
}

const KIND_LABEL: Record<string, string> = {
  world: "生成世界",
  simulate: "模拟",
  build: "构建",
}

const STEP_LABEL: Record<string, string> = {
  types: "类型",
  personas: "人格",
  household: "家庭",
  assemble: "装配",
}

const isActive = (job: JobInfo): boolean => job.status === "running" || job.status === "queued"

const jobMeta = (job: JobInfo): string => {
  const parts = [
    job.world ?? (job.kind === "build" ? null : "（自动世界名）"),
    job.step !== null ? `步骤 ${STEP_LABEL[job.step] ?? job.step}` : null,
    job.house,
    job.exit_code !== null ? `exit ${job.exit_code}` : null,
  ]
  const kept = parts.filter((part): part is string => part !== null && part.length > 0)
  return kept.length === 0 ? "—" : kept.join(" · ")
}

function LogView({ jobId }: { jobId: string | null }) {
  const { lines, connected } = useJobLog(jobId)

  if (jobId === null) {
    return (
      <div className="flex flex-1 items-center justify-center p-6">
        <span className="text-[11px] text-fg-subtle">选择左侧任一作业以查看实时日志。</span>
      </div>
    )
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-center justify-between gap-2 border-b border-border px-4 py-2">
        <span className="label-micro">实时日志 · {lines.length} 行</span>
        <span className={cn("label-latin", connected ? "text-success" : "text-fg-subtle")}>
          {connected ? "streaming" : "idle"}
        </span>
      </div>
      <pre className="num min-h-0 flex-1 overflow-auto px-4 py-3 text-[10px] leading-relaxed whitespace-pre-wrap text-fg-muted">
        {lines.length === 0 ? "（暂无输出）" : lines.join("\n")}
      </pre>
    </div>
  )
}

function BuildJobView({ job }: { job: JobInfo }) {
  const active = isActive(job)

  return (
    <Tabs key={job.id} defaultValue={active ? "log" : "trace"} className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-center gap-2 border-b border-border px-4 py-2">
        <TabsList className="h-7 p-0.5">
          <TabsTrigger value="trace" className="h-6 flex-none px-2 text-[11px]">
            LLM 调用
          </TabsTrigger>
          <TabsTrigger value="log" className="h-6 flex-none px-2 text-[11px]">
            实时日志
          </TabsTrigger>
        </TabsList>
        <span className="num ml-auto text-[10px] text-fg-subtle">{job.id.slice(0, 8)}</span>
      </div>
      <TabsContent value="trace" className="mt-0 flex min-h-0 flex-1 flex-col">
        <StepInspector jobId={job.id} step={job.step} live={active} />
      </TabsContent>
      <TabsContent
        value="log"
        forceMount
        className="mt-0 flex min-h-0 flex-1 flex-col data-[state=inactive]:hidden"
      >
        <LogView jobId={job.id} />
      </TabsContent>
    </Tabs>
  )
}

export function JobsPanel() {
  const jobsQuery = useJobs()
  const [selected, setSelected] = useState<string | null>(null)
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const jobs = jobsQuery.data ?? []
  const selectedJob = jobs.find((job) => job.id === selected) ?? null

  const onCancel = async (jobId: string) => {
    setBusy(jobId)
    setError(null)
    try {
      await cancelJob(jobId)
      await jobsQuery.refetch()
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "取消失败")
    } finally {
      setBusy(null)
    }
  }

  const selectedIsBuild = selectedJob !== null && selectedJob.kind === "build"

  return (
    <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 p-3 lg:grid-cols-[minmax(0,340px)_minmax(0,1fr)]">
      <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface">
        <header className="flex shrink-0 items-center justify-between gap-2 border-b border-border px-4 py-2.5">
          <span className="text-[13px] font-semibold text-fg">
            作业 <span className="num text-[11px] text-fg-subtle">{jobs.length}</span>
          </span>
          <Button variant="ghost" size="icon-sm" aria-label="刷新" onClick={() => void jobsQuery.refetch()}>
            <RefreshCw />
          </Button>
        </header>
        <div className="min-h-0 flex-1 overflow-y-auto">
          {jobs.length === 0 ? (
            <p className="px-4 py-6 text-[11px] text-fg-subtle">
              还没有作业。切到「生成」「模拟」或「构建」提交一个。注意：作业会真实执行 run.py 并消耗 API
              额度。
            </p>
          ) : (
            <ul className="flex flex-col">
              {jobs.map((job) => (
                <li key={job.id} className="border-b border-border">
                  <button
                    type="button"
                    onClick={() => setSelected(job.id)}
                    className={cn(
                      "flex w-full flex-col gap-1 px-4 py-2.5 text-left transition-colors",
                      job.id === selected ? "bg-surface-2" : "hover:bg-surface-2",
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={cn("label-latin", STATUS_CLASS[job.status])}>
                        {STATUS_LABEL[job.status]}
                      </Badge>
                      <span className="label-micro">{KIND_LABEL[job.kind] ?? job.kind}</span>
                      <span className="num ml-auto text-[10px] text-fg-subtle">{job.id.slice(0, 8)}</span>
                    </div>
                    <span className="num truncate text-[11px] text-fg-muted">{jobMeta(job)}</span>
                  </button>
                  {job.status === "running" || job.status === "queued" ? (
                    <button
                      type="button"
                      onClick={() => void onCancel(job.id)}
                      disabled={busy === job.id}
                      className={cn(
                        "label-micro mx-4 mb-2 inline-flex items-center gap-1 rounded-sm border border-border-strong px-1.5 py-0.5",
                        busy === job.id ? "opacity-50" : "hover:border-danger/60 hover:text-danger",
                      )}
                    >
                      <X className="size-2.5" aria-hidden />
                      取消作业
                    </button>
                  ) : null}
                </li>
              ))}
            </ul>
          )}
        </div>
        {error !== null ? (
          <p className="shrink-0 border-t border-border px-4 py-2 text-[10px] text-danger">{error}</p>
        ) : null}
      </section>

      <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface">
        {selectedJob !== null && selectedIsBuild ? (
          <BuildJobView job={selectedJob} />
        ) : (
          <LogView jobId={selectedJob?.id ?? null} />
        )}
      </section>

      <p className="col-span-full text-[10px] text-fg-subtle">
        作业会真实执行 run.py 并消耗 API 额度；同一时间只运行一个作业，避免 output/ 并发写入。
      </p>
    </div>
  )
}
