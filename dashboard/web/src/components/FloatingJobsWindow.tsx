import * as React from "react"

import { JobsPanel } from "@/components/JobsPanel"
import { FloatingPanel } from "@/components/primitives/FloatingPanel"
import { useTimeStore } from "@/store/time"

export function FloatingJobsWindow(props: { onClose: () => void }): React.JSX.Element {
  const jobsFocus = useTimeStore((state) => state.jobsFocus)

  return (
    <FloatingPanel title="Job activity" subtitle="LLM calls and live logs" onClose={props.onClose}>
      <JobsPanel key={jobsFocus ?? "all"} focusJobId={jobsFocus} />
    </FloatingPanel>
  )
}
