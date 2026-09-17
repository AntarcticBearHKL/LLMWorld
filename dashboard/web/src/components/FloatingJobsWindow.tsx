import * as React from "react"

import { JobsPanel } from "@/components/JobsPanel"
import { FloatingPanel } from "@/components/primitives/FloatingPanel"

export function FloatingJobsWindow(props: { onClose: () => void }): React.JSX.Element {
  return (
    <FloatingPanel title="Job activity" subtitle="LLM calls and live logs" onClose={props.onClose}>
      <JobsPanel />
    </FloatingPanel>
  )
}
