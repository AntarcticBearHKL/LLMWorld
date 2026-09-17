import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react"
import type { MouseEvent as ReactMouseEvent, PointerEvent as ReactPointerEvent } from "react"

export const MIN_PANEL_PX = 140
export const MAX_PANEL_PX = 1200

const DRAG_THRESHOLD_PX = 3

const storageKey = (panelId: string): string => `llmworld.panel.${panelId}.height`

const clampHeight = (value: number): number =>
  Math.min(MAX_PANEL_PX, Math.max(MIN_PANEL_PX, Math.round(value)))

const readStoredHeight = (panelId: string): number | null => {
  try {
    const raw = window.localStorage.getItem(storageKey(panelId))
    if (raw === null) return null
    const parsed = Number(raw)
    return Number.isFinite(parsed) ? clampHeight(parsed) : null
  } catch {
    return null
  }
}

const writeStoredHeight = (panelId: string, height: number | null): void => {
  try {
    if (height === null) {
      window.localStorage.removeItem(storageKey(panelId))
    } else {
      window.localStorage.setItem(storageKey(panelId), String(height))
    }
  } catch {
    // Storage can be disabled — the panel still resizes for this session.
  }
}

const heightCache = new Map<string, number | null>()
const hydratedPanels = new Set<string>()
const heightListeners = new Map<string, Set<() => void>>()

const subscribeToHeight = (panelId: string, listener: () => void): (() => void) => {
  if (!hydratedPanels.has(panelId)) {
    hydratedPanels.add(panelId)
    const stored = readStoredHeight(panelId)
    if (stored !== null) {
      heightCache.set(panelId, stored)
      listener()
    }
  }
  const group = heightListeners.get(panelId) ?? new Set<() => void>()
  group.add(listener)
  heightListeners.set(panelId, group)
  return () => {
    group.delete(listener)
    if (group.size === 0) heightListeners.delete(panelId)
  }
}

const emitHeight = (panelId: string): void => {
  const group = heightListeners.get(panelId)
  if (group === undefined) return
  for (const listener of group) listener()
}

const readHeight = (panelId: string): number | null => heightCache.get(panelId) ?? null

const storeHeight = (panelId: string, height: number | null): void => {
  heightCache.set(panelId, height)
  emitHeight(panelId)
}

interface DragState {
  node: HTMLElement
  pointerId: number
  startY: number
  startHeight: number
  moved: boolean
}

export interface PanelDragProps {
  onPointerDown: (event: ReactPointerEvent<HTMLElement>) => void
  onPointerMove: (event: ReactPointerEvent<HTMLElement>) => void
  onPointerUp: () => void
  onPointerCancel: () => void
  onClick: (event: ReactMouseEvent<HTMLElement>) => void
}

export interface PanelHeightControls {
  height: number | null
  setHeight: (next: number | null) => void
  dragging: boolean
  dragProps: PanelDragProps
}

export function usePanelHeight(panelId: string): PanelHeightControls {
  const [dragging, setDragging] = useState(false)
  const dragRef = useRef<DragState | null>(null)
  const suppressClickRef = useRef(false)

  const subscribe = useCallback(
    (listener: () => void) => subscribeToHeight(panelId, listener),
    [panelId],
  )
  const snapshot = useCallback(() => readHeight(panelId), [panelId])
  const height = useSyncExternalStore(subscribe, snapshot)

  useEffect(() => {
    return () => {
      const drag = dragRef.current
      if (drag !== null && drag.node.hasPointerCapture(drag.pointerId)) {
        drag.node.releasePointerCapture(drag.pointerId)
      }
      dragRef.current = null
    }
  }, [])

  const setHeight = useCallback(
    (next: number | null) => {
      const clamped = next === null ? null : clampHeight(next)
      storeHeight(panelId, clamped)
      writeStoredHeight(panelId, clamped)
    },
    [panelId],
  )

  const finishDrag = useCallback(() => {
    const drag = dragRef.current
    if (drag === null) return
    dragRef.current = null
    setDragging(false)
    if (drag.node.hasPointerCapture(drag.pointerId)) {
      drag.node.releasePointerCapture(drag.pointerId)
    }
    suppressClickRef.current = drag.moved
    if (drag.moved) {
      const current = readHeight(panelId)
      if (current !== null) writeStoredHeight(panelId, current)
    }
  }, [panelId])

  const onPointerDown = useCallback(
    (event: ReactPointerEvent<HTMLElement>) => {
      if (event.button !== 0) return
      const node = event.currentTarget
      const panelHeight = node.parentElement?.getBoundingClientRect().height ?? 0
      dragRef.current = {
        node,
        pointerId: event.pointerId,
        startY: event.clientY,
        startHeight: readHeight(panelId) ?? Math.max(panelHeight, MIN_PANEL_PX),
        moved: false,
      }
      suppressClickRef.current = false
      node.setPointerCapture(event.pointerId)
      setDragging(true)
      event.preventDefault()
    },
    [panelId],
  )

  const onPointerMove = useCallback(
    (event: ReactPointerEvent<HTMLElement>) => {
      const drag = dragRef.current
      if (drag === null || drag.pointerId !== event.pointerId) return
      const delta = event.clientY - drag.startY
      if (!drag.moved && Math.abs(delta) < DRAG_THRESHOLD_PX) return
      drag.moved = true
      storeHeight(panelId, clampHeight(drag.startHeight + delta))
    },
    [panelId],
  )

  const onClick = useCallback((event: ReactMouseEvent<HTMLElement>) => {
    if (!suppressClickRef.current) return
    suppressClickRef.current = false
    event.preventDefault()
    event.stopPropagation()
  }, [])

  return {
    height,
    setHeight,
    dragging,
    dragProps: {
      onPointerDown,
      onPointerMove,
      onPointerUp: finishDrag,
      onPointerCancel: finishDrag,
      onClick,
    },
  }
}
