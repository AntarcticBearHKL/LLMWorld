import type { CSSProperties, ReactNode } from "react"

import { cn } from "@/lib/utils"

interface PanelProps {
  title: string
  hint?: ReactNode
  actions?: ReactNode
  children: ReactNode
  className?: string
  bodyClassName?: string
  index?: number
}

export function Panel({ title, hint, actions, children, className, bodyClassName, index = 0 }: PanelProps) {
  const style = { "--enter-index": index } as CSSProperties

  return (
    <section className={cn("enter card flex min-h-0 flex-col overflow-hidden", className)} style={style}>
      <header className="flex shrink-0 items-center justify-between gap-3 border-b border-border px-4 py-2.5">
        <div className="flex min-w-0 items-baseline gap-2">
          <h2 className="truncate text-[15px] font-semibold tracking-[-0.01em] text-fg">{title}</h2>
          {hint !== undefined ? (
            <span className="label-latin truncate">{hint}</span>
          ) : null}
        </div>
        {actions !== undefined ? <div className="flex shrink-0 items-center gap-1.5">{actions}</div> : null}
      </header>
      <div className={cn("min-h-0 flex-1", bodyClassName)}>{children}</div>
    </section>
  )
}
