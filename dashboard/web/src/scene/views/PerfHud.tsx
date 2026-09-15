import { useEffect, useRef, useState } from "react"

import { Button } from "@/components/ui/button"
import { useFpsMeter } from "@/hooks/useFpsMeter"
import { cn } from "@/lib/utils"

export const FPS_FLOOR = 45
export const HEAP_GROWTH_LIMIT = 0.2
const BAD_SAMPLES_TO_DEGRADE = 2
const GOOD_SAMPLES_TO_RECOVER = 4

interface PerfHudProps {
  autoStart?: boolean
  onDegradeChange?: (degraded: boolean) => void
}

const heapGrowthRatio = (usedMb: number | null, deltaMb: number | null): number | null => {
  if (usedMb === null || deltaMb === null) return null
  const start = usedMb - deltaMb
  if (start <= 0) return null
  return deltaMb / start
}

export function PerfHud({ autoStart = false, onDegradeChange }: PerfHudProps) {
  const meter = useFpsMeter()
  const [running, setRunning] = useState(false)
  const [degraded, setDegraded] = useState(false)
  const badStreak = useRef(0)
  const goodStreak = useRef(0)
  const report = meter.lastReport
  const { start, stop } = meter

  useEffect(() => {
    if (!autoStart) return
    start()
    setRunning(true)
  }, [autoStart, start])

  useEffect(() => {
    if (report === null) return
    if (!report.valid) {
      badStreak.current = 0
      return
    }
    const growth = heapGrowthRatio(report.heapUsedMb, report.heapDeltaMb)
    const bad = report.fps < FPS_FLOOR || (growth !== null && growth > HEAP_GROWTH_LIMIT)
    if (!bad) {
      badStreak.current = 0
      goodStreak.current += 1
      if (degraded && goodStreak.current >= GOOD_SAMPLES_TO_RECOVER) {
        setDegraded(false)
        onDegradeChange?.(false)
      }
      return
    }
    goodStreak.current = 0
    badStreak.current += 1
    if (badStreak.current >= BAD_SAMPLES_TO_DEGRADE && !degraded) {
      setDegraded(true)
      onDegradeChange?.(true)
    }
  }, [report, degraded, onDegradeChange])

  const growth = report === null ? null : heapGrowthRatio(report.heapUsedMb, report.heapDeltaMb)
  const invalid = report !== null && !report.valid

  const toggle = () => {
    if (running) {
      stop()
      setRunning(false)
      return
    }
    badStreak.current = 0
    goodStreak.current = 0
    start()
    setRunning(true)
  }

  return (
    <div className="flex items-center gap-2 rounded-full border border-border bg-surface-2 px-3 py-1">
      <span className="label-micro">Perf</span>
      <span className="num text-[10px] text-fg">
        {report === null ? "Not sampled" : `${report.fps} fps`}
      </span>
      <span className="num text-[10px] text-fg-subtle">
        {report === null || report.heapDeltaMb === null
          ? "heap n/a"
          : `heap ${report.heapDeltaMb >= 0 ? "+" : ""}${report.heapDeltaMb} MB`}
      </span>
      <span className="num text-[10px] text-fg-subtle">
        {growth === null ? "" : `${(growth * 100).toFixed(1)}%`}
      </span>
      <span className="num text-[10px] text-fg-subtle">
        {report === null ? "" : `${report.sampleSeconds}s`}
      </span>
      <span
        className={cn(
          "label-latin",
          invalid ? "text-fg-subtle" : degraded ? "text-danger" : "text-success",
        )}
      >
        {invalid ? "Invalid sample" : degraded ? "Degraded" : "OK"}
      </span>
      {invalid ? (
        <span className="num text-[10px] text-fg-subtle">needs foreground tab</span>
      ) : null}
      <Button variant="outline" size="sm" className="h-6 px-2 text-[11px]" onClick={toggle}>
        {running ? "Stop sampling" : "Start sampling"}
      </Button>
    </div>
  )
}
