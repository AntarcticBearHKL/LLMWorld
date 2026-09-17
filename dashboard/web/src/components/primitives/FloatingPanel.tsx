import * as React from "react"

import { X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const DRAG_THRESHOLD = 4

export function FloatingPanel(props: {
  title: string
  subtitle?: string
  onClose: () => void
  children: React.ReactNode
}): React.JSX.Element {
  const { title, subtitle, onClose, children } = props
  const [offset, setOffset] = React.useState({ x: 0, y: 0 })
  const [dragEnabled] = React.useState(
    () => !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  )
  const drag = React.useRef<{
    pointerId: number
    startX: number
    startY: number
    baseX: number
    baseY: number
  } | null>(null)
  const moved = React.useRef(false)

  const onPointerDown = (event: React.PointerEvent<HTMLElement>) => {
    moved.current = false
    if (!dragEnabled || event.button !== 0) return
    if ((event.target as HTMLElement).closest("button") !== null) return
    drag.current = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      baseX: offset.x,
      baseY: offset.y,
    }
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  const onPointerMove = (event: React.PointerEvent<HTMLElement>) => {
    const state = drag.current
    if (state === null || state.pointerId !== event.pointerId) return
    const dx = event.clientX - state.startX
    const dy = event.clientY - state.startY
    if (!moved.current && Math.hypot(dx, dy) < DRAG_THRESHOLD) return
    moved.current = true
    setOffset({ x: state.baseX + dx, y: state.baseY + dy })
  }

  const endDrag = (event: React.PointerEvent<HTMLElement>) => {
    const state = drag.current
    if (state === null || state.pointerId !== event.pointerId) return
    drag.current = null
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId)
    }
  }

  const onClickCapture = (event: React.MouseEvent<HTMLElement>) => {
    if (!moved.current) return
    moved.current = false
    event.preventDefault()
    event.stopPropagation()
  }

  React.useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return
      onClose()
    }
    document.addEventListener("keydown", onKeyDown)
    return () => {
      document.removeEventListener("keydown", onKeyDown)
    }
  }, [onClose])

  return (
    <div
      style={{ transform: `translate3d(${offset.x}px, ${offset.y}px, 0)` }}
      className="fixed right-4 bottom-4 z-40 h-[min(600px,calc(100dvh-2rem))] w-[min(920px,calc(100vw-2rem))]"
    >
      <div
        role="complementary"
        aria-label={title}
        className="enter chrome-lg shadow-3 flex h-full w-full flex-col overflow-hidden rounded-xl"
      >
        <header
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={endDrag}
          onPointerCancel={endDrag}
          onClickCapture={onClickCapture}
          className={cn(
            "flex shrink-0 touch-none items-center justify-between gap-3 border-b border-border px-4 py-2.5 select-none",
            dragEnabled && "cursor-grab",
          )}
        >
          <div className="flex min-w-0 items-baseline gap-2">
            <h2 className="truncate text-[15px] font-semibold tracking-[-0.01em] text-fg">
              {title}
            </h2>
            {subtitle !== undefined ? <span className="label-latin truncate">{subtitle}</span> : null}
          </div>
          <Button variant="ghost" size="icon-xs" aria-label="Close job activity" onClick={onClose}>
            <X />
          </Button>
        </header>
        <div className="min-h-0 flex-1 overflow-hidden">{children}</div>
      </div>
    </div>
  )
}
