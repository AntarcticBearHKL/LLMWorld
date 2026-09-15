import { useCallback, useEffect, useRef, useState } from "react"

export interface FpsReport {
  fps: number
  frames: number
  sampleSeconds: number
  heapUsedMb: number | null
  heapDeltaMb: number | null
  stalls: number
  valid: boolean
  at: number
}

export interface FpsMeter {
  fps: number | null
  sampleSeconds: number
  start: () => void
  stop: () => void
  lastReport: FpsReport | null
}

interface PerformanceMemory {
  usedJSHeapSize: number
  totalJSHeapSize: number
  jsHeapSizeLimit: number
}

const DEFAULT_WINDOW_MS = 500
const MIN_WINDOW_MS = 100
const STALL_FACTOR = 4
const STALL_GAP_MS = 250
const MAX_STALL_RATIO = 0.5

const readHeapBytes = (): number | null => {
  const perf = performance as Performance & { memory?: PerformanceMemory }
  return perf.memory === undefined ? null : perf.memory.usedJSHeapSize
}

const toMb = (bytes: number): number => Math.round((bytes / 1024 / 1024) * 10) / 10

const buildReport = (
  frames: number,
  windowSeconds: number,
  totalSeconds: number,
  heapStartBytes: number | null,
  stalls: number,
): FpsReport => {
  const heapNowBytes = readHeapBytes()
  const fps = Math.round((frames / Math.max(windowSeconds, 0.001)) * 10) / 10
  return {
    fps,
    frames,
    sampleSeconds: Math.round(totalSeconds * 10) / 10,
    heapUsedMb: heapNowBytes === null ? null : toMb(heapNowBytes),
    heapDeltaMb:
      heapNowBytes === null || heapStartBytes === null ? null : toMb(heapNowBytes - heapStartBytes),
    stalls,
    valid: frames > 0 && stalls / Math.max(1, frames) <= MAX_STALL_RATIO,
    at: Date.now(),
  }
}

/**
 * rAF-driven FPS sampler: averages over windowMs, with performance.memory (Chrome).
 * Hidden tabs or long stalls reset the window so paused time is not counted as low FPS.
 */
export function useFpsMeter(windowMs: number = DEFAULT_WINDOW_MS): FpsMeter {
  const [fps, setFps] = useState<number | null>(null)
  const [sampleSeconds, setSampleSeconds] = useState(0)
  const [lastReport, setLastReport] = useState<FpsReport | null>(null)

  const rafRef = useRef(0)
  const framesRef = useRef(0)
  const windowStartRef = useRef(0)
  const totalStartRef = useRef(0)
  const lastFrameRef = useRef(0)
  const stallsRef = useRef(0)
  const heapStartRef = useRef<number | null>(null)

  const stop = useCallback(() => {
    if (rafRef.current === 0) return
    cancelAnimationFrame(rafRef.current)
    rafRef.current = 0
    const now = performance.now()
    const windowSeconds = (now - windowStartRef.current) / 1000
    if (framesRef.current === 0 || windowSeconds <= 0) return
    const report = buildReport(
      framesRef.current,
      windowSeconds,
      (now - totalStartRef.current) / 1000,
      heapStartRef.current,
      stallsRef.current,
    )
    framesRef.current = 0
    setFps(report.fps)
    setSampleSeconds(report.sampleSeconds)
    setLastReport(report)
  }, [])

  const start = useCallback(() => {
    stop()
    const window = Math.max(MIN_WINDOW_MS, windowMs)
    const now = performance.now()
    framesRef.current = 0
    stallsRef.current = 0
    windowStartRef.current = now
    lastFrameRef.current = now
    totalStartRef.current = now
    heapStartRef.current = readHeapBytes()
    setFps(null)
    setSampleSeconds(0)
    setLastReport(null)

    const loop = (frameTime: number) => {
      if (frameTime - lastFrameRef.current > STALL_GAP_MS) stallsRef.current += 1
      lastFrameRef.current = frameTime
      const elapsedMs = frameTime - windowStartRef.current
      if (elapsedMs > window * STALL_FACTOR) {
        windowStartRef.current = frameTime
        framesRef.current = 0
        rafRef.current = requestAnimationFrame(loop)
        return
      }
      framesRef.current += 1
      if (elapsedMs >= window) {
        const report = buildReport(
          framesRef.current,
          elapsedMs / 1000,
          (frameTime - totalStartRef.current) / 1000,
          heapStartRef.current,
          stallsRef.current,
        )
        framesRef.current = 0
        stallsRef.current = 0
        windowStartRef.current = frameTime
        setFps(report.fps)
        setSampleSeconds(report.sampleSeconds)
        setLastReport(report)
      }
      rafRef.current = requestAnimationFrame(loop)
    }
    rafRef.current = requestAnimationFrame(loop)
  }, [stop, windowMs])

  useEffect(() => stop, [stop])

  return { fps, sampleSeconds, start, stop, lastReport }
}
