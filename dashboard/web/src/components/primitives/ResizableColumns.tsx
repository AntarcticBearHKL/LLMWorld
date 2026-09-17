import { useCallback, useEffect, useRef, useState } from "react"
import type {
  CSSProperties,
  JSX,
  KeyboardEvent as ReactKeyboardEvent,
  PointerEvent as ReactPointerEvent,
  ReactNode,
} from "react"

import { cn } from "@/lib/utils"

const MIN_COLUMN_WIDTH = 260
const DIVIDER_WIDTH = 8
const KEYBOARD_STEP = 24

export function ResizableColumns(props: {
  first: ReactNode
  second: ReactNode
  storageId: string
  label: string
}): JSX.Element {
  const { first, second, storageId, label } = props
  const containerRef = useRef<HTMLDivElement | null>(null)
  const firstRef = useRef<HTMLDivElement | null>(null)
  const draggingRef = useRef(false)
  const startXRef = useRef(0)
  const startWidthRef = useRef(MIN_COLUMN_WIDTH)
  const [size, setSize] = useState<number | null>(null)
  const [dragging, setDragging] = useState(false)

  const storageKey = "llmworld.split." + storageId

  const clampSize = useCallback((value: number): number => {
    const container = containerRef.current
    const containerWidth = container ? container.getBoundingClientRect().width : 0
    const max = Math.max(MIN_COLUMN_WIDTH, containerWidth - DIVIDER_WIDTH - MIN_COLUMN_WIDTH)
    return Math.round(Math.min(Math.max(value, MIN_COLUMN_WIDTH), max))
  }, [])

  const measureFirst = useCallback((): number => {
    const node = firstRef.current
    if (!node) return MIN_COLUMN_WIDTH
    const width = Math.round(node.getBoundingClientRect().width)
    return width > 0 ? width : MIN_COLUMN_WIDTH
  }, [])

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(storageKey)
      if (stored === null) return
      const parsed = Number.parseInt(stored, 10)
      if (Number.isFinite(parsed)) queueMicrotask(() => setSize(clampSize(parsed)))
    } catch {
      // Storage is unavailable; the split still works in memory.
    }
  }, [storageKey, clampSize])

  useEffect(() => {
    if (size === null) return
    try {
      window.localStorage.setItem(storageKey, String(size))
    } catch {
      // Storage is unavailable; the split still works in memory.
    }
  }, [size, storageKey])

  const handlePointerDown = (event: ReactPointerEvent<HTMLDivElement>): void => {
    if (event.button !== 0) return
    const currentSize = size ?? measureFirst()
    startXRef.current = event.clientX
    startWidthRef.current = currentSize
    draggingRef.current = true
    setDragging(true)
    event.currentTarget.focus({ preventScroll: true })
    event.currentTarget.setPointerCapture(event.pointerId)
    event.preventDefault()
    if (size === null) setSize(clampSize(currentSize))
  }

  const handlePointerMove = (event: ReactPointerEvent<HTMLDivElement>): void => {
    if (!draggingRef.current) return
    const delta = event.clientX - startXRef.current
    setSize(clampSize(startWidthRef.current + delta))
  }

  const handlePointerEnd = (event: ReactPointerEvent<HTMLDivElement>): void => {
    if (!draggingRef.current) return
    draggingRef.current = false
    setDragging(false)
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId)
    }
  }

  const handleKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>): void => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return
    event.preventDefault()
    const current = size ?? measureFirst()
    const delta = event.key === "ArrowLeft" ? -KEYBOARD_STEP : KEYBOARD_STEP
    setSize(clampSize(current + delta))
  }

  const handleFocus = (): void => {
    if (size === null) setSize(clampSize(measureFirst()))
  }

  const style: CSSProperties | undefined =
    size === null ? undefined : ({ "--split-size": `${size}px` } as CSSProperties)

  return (
    <div
      ref={containerRef}
      className={cn(
        "grid h-full min-h-0 w-full min-w-0 flex-1",
        "grid-cols-1 lg:grid-cols-[var(--split-size,1fr)_auto_1fr]",
      )}
      style={style}
    >
      <div ref={firstRef} className="min-h-0 min-w-0 overflow-hidden">
        {first}
      </div>
      <div
        role="separator"
        aria-orientation="horizontal"
        aria-label={"Resize " + label}
        aria-valuenow={size ?? undefined}
        tabIndex={0}
        data-dragging={dragging}
        className={cn(
          "group hidden h-full w-2 shrink-0 cursor-col-resize touch-none items-center justify-center outline-none",
          "lg:flex",
        )}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerEnd}
        onPointerCancel={handlePointerEnd}
        onKeyDown={handleKeyDown}
        onFocus={handleFocus}
      >
        <div
          className={cn(
            "h-full w-px bg-border",
            "group-hover:w-[3px] group-hover:bg-brand",
            "group-focus-visible:w-[3px] group-focus-visible:bg-brand",
            "group-data-[dragging=true]:w-[3px] group-data-[dragging=true]:bg-brand",
          )}
        />
      </div>
      <div className="min-h-0 min-w-0 overflow-hidden">{second}</div>
    </div>
  )
}
