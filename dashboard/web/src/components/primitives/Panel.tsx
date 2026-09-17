import { useCallback, useRef, useState } from "react"
import type { CSSProperties, KeyboardEvent, ReactNode } from "react"

import { MAX_PANEL_PX, MIN_PANEL_PX, usePanelHeight } from "@/hooks/usePanelHeight"
import { cn } from "@/lib/utils"

const KEYBOARD_STEP_PX = 16

interface PanelProps {
  panelId?: string
  title: string
  hint?: ReactNode
  actions?: ReactNode
  children: ReactNode
  className?: string
  bodyClassName?: string
  index?: number
}

export function Panel({ panelId, title, hint, actions, children, className, bodyClassName, index = 0 }: PanelProps) {
  const { height, setHeight, dragging, dragProps } = usePanelHeight(panelId ?? title)
  const sectionRef = useRef<HTMLElement>(null)
  const [measuredHeight, setMeasuredHeight] = useState<number | null>(null)

  const handleFocus = useCallback(() => {
    const measured = sectionRef.current?.getBoundingClientRect().height
    if (measured !== undefined) setMeasuredHeight(Math.round(measured))
  }, [])

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLElement>) => {
      if (event.key !== "ArrowUp" && event.key !== "ArrowDown") return
      event.preventDefault()
      const base = height ?? sectionRef.current?.getBoundingClientRect().height ?? MIN_PANEL_PX
      setHeight(base + (event.key === "ArrowDown" ? KEYBOARD_STEP_PX : -KEYBOARD_STEP_PX))
    },
    [height, setHeight],
  )

  const style = {
    "--enter-index": index,
    ...(height !== null ? { height, flex: "none" } : {}),
  } as CSSProperties

  return (
    <section
      ref={sectionRef}
      className={cn("enter card relative flex min-h-0 flex-col overflow-hidden", className)}
      style={style}
    >
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
      <div
        role="separator"
        aria-orientation="horizontal"
        aria-label={`Resize ${title}`}
        aria-valuemin={MIN_PANEL_PX}
        aria-valuemax={MAX_PANEL_PX}
        aria-valuenow={height ?? measuredHeight ?? undefined}
        tabIndex={0}
        data-dragging={dragging}
        onFocus={handleFocus}
        onKeyDown={handleKeyDown}
        className="group absolute inset-x-0 bottom-0 h-2 cursor-row-resize touch-none outline-none"
        {...dragProps}
      >
        <div className="absolute inset-x-0 bottom-0 h-px bg-border group-hover:h-[3px] group-hover:bg-brand group-focus-visible:h-[3px] group-focus-visible:bg-brand group-data-[dragging=true]:h-[3px] group-data-[dragging=true]:bg-brand" />
      </div>
    </section>
  )
}
