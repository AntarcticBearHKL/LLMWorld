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
  queued: "Queued",
  running: "Running",
  done: "Done",
  failed: "Failed",
  cancelled: "Cancelled",
}

const STATUS_CLASS: Record<JobInfo["status"], string> = {
  queued: "border-border-strong bg-surface-2 text-fg-muted",
  running: "border-energy/40 bg-energy-soft text-energy",
  done: "border-success/40 bg-success/10 text-success",
  failed: "border-danger/40 bg-danger/10 text-danger",
  cancelled: "border-border-strong bg-surface-2 text-fg-subtle",
}

const KIND_LABEL: Record<string, string> = {
  world: "Generate world",
  simulate: "Simulate",
  build: "Build",
}

const STEP_LABEL: Record<string, string> = {
  district: "District",
  household: "Household",
  home: "Home",
}

const isActive = (job: JobInfo): boolean => job.status === "running" || job.status === "queued"

const jobMeta = (job: JobInfo): string => {
  const parts = [
    job.world ?? (job.kind === "build" ? null : "(auto world name)"),
    job.district,
    job.step !== null ? `step ${STEP_LABEL[job.step] ?? job.step}` : null,
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
        <span className="text-[13px] text-fg-subtle">Select a job to view its live log.</span>
      </div>
    )
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-center justify-between gap-2 border-b border-border px-4 py-2">
        <span className="label-micro">Live log · {lines.length} lines</span>
        <span className={cn("label-latin", connected ? "text-success" : "text-fg-subtle")}>
          {connected ? "streaming" : "idle"}
        </span>
      </div>
      <pre className="num min-h-0 flex-1 overflow-auto px-4 py-3 text-[12px] leading-relaxed whitespace-pre-wrap text-fg-muted">
        {lines.length === 0 ? "(no output yet)" : lines.join("\n")}
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
          <TabsTrigger value="trace" className="h-6 flex-none px-2 text-[13px]">
            LLM calls
          </TabsTrigger>
          <TabsTrigger value="log" className="h-6 flex-none px-2 text-[13px]">
            Live log
          </TabsTrigger>
        </TabsList>
        <span className="num ml-auto text-[12px] text-fg-subtle">{job.id.slice(0, 8)}</span>
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
      setError(caught instanceof ApiError ? caught.message : "Cancel failed")
    } finally {
      setBusy(null)
    }
  }

  const selectedIsBuild = selectedJob !== null && selectedJob.kind === "build"

  return (
    <div className="grid h-full min-h-0 grid-cols-1 gap-3 lg:grid-cols-[minmax(0,340px)_minmax(0,1fr)] lg:grid-rows-[minmax(0,1fr)_auto]">
      <section className="card flex min-h-0 flex-col overflow-hidden">
        <header className="flex shrink-0 items-center justify-between gap-2 border-b border-border px-4 py-3">
          <span className="text-[15px] font-bold tracking-[-0.01em] text-fg">
            Jobs <span className="num text-[13px] font-medium text-fg-subtle">{jobs.length}</span>
          </span>
          <Button variant="ghost" size="icon-sm" aria-label="Refresh jobs" onClick={() => void jobsQuery.refetch()}>
            <RefreshCw />
          </Button>
        </header>
        <div className="min-h-0 flex-1 overflow-y-auto">
          {jobs.length === 0 ? (
            <p className="px-4 py-6 text-[13px] text-fg-subtle">
              No jobs yet. Submit one from the build or simulation flows. Jobs really run run.py and
              spend API credits.
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
                      job.id === selected ? "bg-item-selected" : "hover:bg-item-hover",
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={cn("label-latin", STATUS_CLASS[job.status])}>
                        {STATUS_LABEL[job.status]}
                      </Badge>
                      <span className="label-micro">{KIND_LABEL[job.kind] ?? job.kind}</span>
                      <span className="num ml-auto text-[12px] text-fg-subtle">{job.id.slice(0, 8)}</span>
                    </div>
                    <span className="num truncate text-[13px] text-fg-muted">{jobMeta(job)}</span>
                  </button>
                  {job.status === "running" || job.status === "queued" ? (
                    <button
                      type="button"
                      onClick={() => void onCancel(job.id)}
                      disabled={busy === job.id}
                      className={cn(
                        "label-micro mx-4 mb-2 inline-flex items-center gap-1 rounded-full border border-border-strong px-2 py-0.5",
                        busy === job.id ? "opacity-50" : "hover:border-danger/60 hover:text-danger",
                      )}
                    >
                      <X className="size-2.5" aria-hidden />
                      Cancel job
                    </button>
                  ) : null}
                </li>
              ))}
            </ul>
          )}
        </div>
        {error !== null ? (
          <p className="shrink-0 border-t border-border px-4 py-2 text-[12px] text-danger">{error}</p>
        ) : null}
      </section>

      <section className="card flex min-h-0 flex-col overflow-hidden">
        {selectedJob !== null && selectedIsBuild ? (
          <BuildJobView job={selectedJob} />
        ) : (
          <LogView jobId={selectedJob?.id ?? null} />
        )}
      </section>

      <p className="col-span-full label-micro">
        Jobs really run run.py and spend API credits; only one job runs at a time to avoid concurrent
        writes under output/.
      </p>
    </div>
  )
}
