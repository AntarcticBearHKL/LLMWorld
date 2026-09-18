import * as React from "react"

import { Activity } from "lucide-react"

import { JobsPanel } from "@/components/JobsPanel"
import { FloatingPanel } from "@/components/primitives/FloatingPanel"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { useJobs } from "@/hooks/useJobs"
import { useTimeStore } from "@/store/time"

export function FloatingJobsWindow(props: { onClose: () => void }): React.JSX.Element {
  const jobsFocus = useTimeStore((state) => state.jobsFocus)
  const jobsOpen = useTimeStore((state) => state.jobsOpen)
  const view = useTimeStore((state) => state.view)
  const setJobsOpen = useTimeStore((state) => state.setJobsOpen)
  const activeJobs = (useJobs().data ?? []).filter(
    (job) => job.status === "running" || job.status === "queued",
  ).length
  const expanded = jobsOpen || view === "jobs"

  if (!expanded) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            type="button"
            onClick={() => setJobsOpen(true)}
            aria-label={activeJobs > 0 ? `Job activity, ${activeJobs} active` : "Job activity"}
            aria-expanded={false}
            className="chrome-lg shadow-3 fixed right-4 bottom-4 z-40 flex size-12 items-center justify-center rounded-full text-fg-muted transition-colors hover:text-fg focus-visible:outline-2 focus-visible:outline-brand max-md:bottom-20"
          >
            <Activity className="size-5" />
            {activeJobs > 0 ? (
              <span className="num absolute -top-1 -right-1 rounded-full border border-energy/40 bg-energy-soft px-1 t-caption leading-4 text-energy">
                {activeJobs}
              </span>
            ) : null}
          </button>
        </TooltipTrigger>
        <TooltipContent>Job activity</TooltipContent>
      </Tooltip>
    )
  }

  return (
    <FloatingPanel title="Job activity" subtitle="LLM calls and live logs" onClose={props.onClose}>
      <JobsPanel key={jobsFocus ?? "all"} focusJobId={jobsFocus} />
    </FloatingPanel>
  )
}
