import type { ReactNode } from "react"

import { Lock } from "lucide-react"

interface GateHintProps {
  children: ReactNode
  action?: ReactNode
}

export function GateHint({ children, action }: GateHintProps) {
  return (
    <span className="t-caption text-fg-subtle flex items-center gap-1.5">
      <Lock aria-hidden className="size-3 shrink-0" />
      {children}
      {action}
    </span>
  )
}
