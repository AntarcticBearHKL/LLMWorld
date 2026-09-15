import { useEffect } from "react"

import { DAY_MINUTES } from "@/lib/time"
import { dwellMsFor, useTimeStore } from "@/store/time"

const INTERACTIVE_TAGS = new Set(["INPUT", "TEXTAREA", "SELECT", "OPTION"])

const CARET_ROLES = new Set([
  "slider",
  "combobox",
  "listbox",
  "option",
  "menuitem",
  "menu",
  "dialog",
  "textbox",
  "spinbutton",
])

const isTextEntry = (target: EventTarget | null): boolean => {
  if (!(target instanceof HTMLElement)) return false
  if (INTERACTIVE_TAGS.has(target.tagName)) return true
  return target.isContentEditable
}

const ownsArrowKeys = (target: EventTarget | null): boolean => {
  if (!(target instanceof HTMLElement)) return false
  const role = target.closest("[role]")?.getAttribute("role")
  return role !== null && role !== undefined && CARET_ROLES.has(role)
}

/**
 * Continuous mode advances minute via rAF; auto-step mode advances one step
 * every dwellMsFor(speed) milliseconds. Hidden tabs pause to avoid burning CPU
 * in the background. Keyboard shortcuts and playback stay out of each other's
 * way: keys are not hijacked inside inputs, and only Space is taken on sliders.
 */
export function usePlayback(): void {
  const isPlaying = useTimeStore((state) => state.isPlaying)
  const playMode = useTimeStore((state) => state.playMode)
  const speed = useTimeStore((state) => state.speed)

  useEffect(() => {
    if (!isPlaying) return

    if (playMode === "autoStep") {
      const tick = () => {
        const store = useTimeStore.getState()
        if (!store.isPlaying) return
        if (store.minute >= DAY_MINUTES) {
          store.setPlaying(false)
          return
        }
        store.stepOnce(1)
        const after = useTimeStore.getState()
        if (after.minute >= DAY_MINUTES) after.setPlaying(false)
      }
      const timer = window.setInterval(tick, dwellMsFor(speed))
      return () => window.clearInterval(timer)
    }

    let frame = 0
    let last = performance.now()
    const tick = (now: number) => {
      const deltaSeconds = Math.min((now - last) / 1000, 0.5)
      last = now
      useTimeStore.getState().advance(deltaSeconds)
      frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [isPlaying, playMode, speed])

  useEffect(() => {
    const onVisibility = () => {
      if (document.hidden) useTimeStore.getState().setPlaying(false)
    }
    document.addEventListener("visibilitychange", onVisibility)
    return () => document.removeEventListener("visibilitychange", onVisibility)
  }, [])

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) return
      if (isTextEntry(event.target)) return
      const store = useTimeStore.getState()
      const arrowsOwned = ownsArrowKeys(event.target)

      if (event.key === " " || event.code === "Space") {
        event.preventDefault()
        store.togglePlay()
        return
      }
      if (arrowsOwned) return

      switch (event.key) {
        case "ArrowLeft":
          event.preventDefault()
          if (event.shiftKey) {
            store.stepBy(-60)
          } else {
            store.setPlaying(false)
            store.stepOnce(-1)
          }
          break
        case "ArrowRight":
          event.preventDefault()
          if (event.shiftKey) {
            store.stepBy(60)
          } else {
            store.setPlaying(false)
            store.stepOnce(1)
          }
          break
        case "Home":
          event.preventDefault()
          store.setMinute(0)
          break
        case "End":
          event.preventDefault()
          store.setMinute(DAY_MINUTES)
          break
        default:
          break
      }
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])
}
