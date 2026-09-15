import { useMemo, useState } from "react"

import type { DayReplay } from "@/api/types"
import { Panel } from "@/components/primitives/Panel"
import { minutesOf } from "@/lib/appliance"
import { DAY_MINUTES, clampMinute, formatHHMM, formatKwh, formatWatts } from "@/lib/time"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

interface EnergyChartProps {
  replay: DayReplay | undefined
}

const CHART_HEIGHT = 168
const MAX_SERIES = 7
const STEP = 2

const SERIES_COLORS: readonly string[] = [
  "var(--energy)",
  "var(--brand)",
  "var(--cat-focus)",
  "var(--cat-leisure)",
  "var(--cat-meal)",
  "var(--cat-chore)",
  "var(--cat-sleep)",
  "var(--fg-subtle)",
]

const FALLBACK_COLOR = "var(--fg-subtle)"

const colorAt = (index: number): string => {
  const size = SERIES_COLORS.length
  return SERIES_COLORS[((index % size) + size) % size] ?? FALLBACK_COLOR
}

interface Series {
  id: string
  name: string
  energy: number
  color: string
  values: number[]
}

interface Layer {
  id: string
  name: string
  color: string
  lower: number[]
  upper: number[]
}

export function EnergyChart({ replay }: EnergyChartProps) {
  const minute = useTimeStore((state) => state.minute)
  const [hidden, setHidden] = useState<Set<string>>(() => new Set())
  const [hover, setHover] = useState<number | null>(null)

  const model = useMemo(() => {
    if (replay === undefined) return null
    const ranked = replay.appliances
      .filter((appliance) => appliance.energy_kwh > 0.005)
      .sort((a, b) => b.energy_kwh - a.energy_kwh)

    const series: Series[] = ranked.slice(0, MAX_SERIES).map((appliance, index) => ({
      id: appliance.unique_id,
      name: appliance.info.name,
      energy: appliance.energy_kwh,
      color: colorAt(index),
      values: minutesOf(appliance),
    }))

    const rest = ranked.slice(MAX_SERIES)
    if (rest.length > 0) {
      const values = new Array<number>(DAY_MINUTES).fill(0)
      for (const appliance of rest) {
        const partial = minutesOf(appliance)
        for (let index = 0; index < DAY_MINUTES; index += 1) {
          values[index] = (values[index] ?? 0) + (partial[index] ?? 0)
        }
      }
      series.push({
        id: "__rest__",
        name: `Other ${rest.length}`,
        energy: rest.reduce((sum, appliance) => sum + appliance.energy_kwh, 0),
        color: colorAt(SERIES_COLORS.length - 1),
        values,
      })
    }
    return { series, totals: replay.total_watts }
  }, [replay])

  const stacked = useMemo(() => {
    if (model === null) return null
    const cumulative = new Array<number>(DAY_MINUTES).fill(0)
    const layers: Layer[] = []
    for (const item of model.series) {
      if (hidden.has(item.id)) continue
      const lower = cumulative.slice()
      for (let index = 0; index < DAY_MINUTES; index += 1) {
        cumulative[index] = (cumulative[index] ?? 0) + (item.values[index] ?? 0)
      }
      layers.push({
        id: item.id,
        name: item.name,
        color: item.color,
        lower,
        upper: cumulative.slice(),
      })
    }
    const peakTotal = model.totals.reduce((max, value) => Math.max(max, value), 0)
    const peakStack = cumulative.reduce((max, value) => Math.max(max, value), 0)
    const ceiling = Math.max(peakTotal, peakStack) * 1.08 || 1
    return { layers, ceiling, peak: peakTotal }
  }, [model, hidden])

  const toY = (watts: number, ceiling: number): number =>
    CHART_HEIGHT - Math.min(1, Math.max(0, watts / ceiling)) * CHART_HEIGHT

  const areaPath = (lower: number[], upper: number[], ceiling: number): string => {
    let path = ""
    for (let index = 0; index <= DAY_MINUTES; index += STEP) {
      const at = Math.min(index, DAY_MINUTES - 1)
      path += `${path === "" ? "M" : " L"} ${index} ${toY(upper[at] ?? 0, ceiling).toFixed(1)}`
    }
    for (let index = DAY_MINUTES; index >= 0; index -= STEP) {
      const at = Math.min(index, DAY_MINUTES - 1)
      path += ` L ${index} ${toY(lower[at] ?? 0, ceiling).toFixed(1)}`
    }
    return `${path} Z`
  }

  const seek = (clientX: number, element: HTMLElement) => {
    const rect = element.getBoundingClientRect()
    const ratio = (clientX - rect.left) / Math.max(1, rect.width)
    const store = useTimeStore.getState()
    store.setPlaying(false)
    store.setMinute(clampMinute(ratio * DAY_MINUTES))
  }

  const markMinute = hover ?? minute
  const markWatts = model?.totals[Math.min(DAY_MINUTES - 1, Math.max(0, markMinute))] ?? 0

  const toggle = (id: string) => {
    setHidden((previous) => {
      const next = new Set(previous)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <Panel
      title="Day load"
      hint={stacked !== null ? `peak ${formatWatts(stacked.peak)}` : "No data"}
      index={3}
      className="min-h-[248px]"
      bodyClassName="flex min-h-0 flex-col"
      actions={
        <span className="label-latin">
          {replay !== undefined ? `total ${formatKwh(replay.metrics.total_kwh)} kWh` : "—"}
        </span>
      }
    >
      {model === null || stacked === null ? (
        <div className="flex flex-1 items-center justify-center px-4 py-6">
          <span className="text-[11px] text-fg-subtle">Loading load curve…</span>
        </div>
      ) : (
        <>
          <div className="relative mx-3 mt-2 shrink-0 select-none" style={{ height: CHART_HEIGHT }}>
            <div
              className="relative h-full w-full cursor-crosshair touch-none"
              onPointerDown={(event) => {
                event.currentTarget.setPointerCapture(event.pointerId)
                seek(event.clientX, event.currentTarget)
              }}
              onPointerMove={(event) => {
                const rect = event.currentTarget.getBoundingClientRect()
                const ratio = (event.clientX - rect.left) / Math.max(1, rect.width)
                setHover(clampMinute(ratio * DAY_MINUTES))
                if (event.buttons === 1) seek(event.clientX, event.currentTarget)
              }}
              onPointerLeave={() => setHover(null)}
            >
              <svg
                className="h-full w-full"
                viewBox={`0 0 ${DAY_MINUTES} ${CHART_HEIGHT}`}
                preserveAspectRatio="none"
                aria-hidden
              >
                {[0.25, 0.5, 0.75].map((fraction) => (
                  <line
                    key={fraction}
                    x1={0}
                    x2={DAY_MINUTES}
                    y1={CHART_HEIGHT * fraction}
                    y2={CHART_HEIGHT * fraction}
                    stroke="var(--border)"
                    strokeWidth={1}
                    vectorEffect="non-scaling-stroke"
                  />
                ))}
                {stacked.layers.map((layer) => (
                  <path
                    key={layer.id}
                    d={areaPath(layer.lower, layer.upper, stacked.ceiling)}
                    fill={layer.color}
                    fillOpacity={0.45}
                  />
                ))}
                <path
                  d={model.totals
                    .map(
                      (value, index) =>
                        `${index === 0 ? "M" : "L"} ${index} ${toY(value, stacked.ceiling).toFixed(1)}`,
                    )
                    .join(" ")}
                  fill="none"
                  stroke="var(--fg-muted)"
                  strokeWidth={1.25}
                  vectorEffect="non-scaling-stroke"
                />
                <line
                  x1={markMinute}
                  x2={markMinute}
                  y1={0}
                  y2={CHART_HEIGHT}
                  stroke={hover !== null ? "var(--fg-muted)" : "var(--brand)"}
                  strokeWidth={hover !== null ? 1 : 1.5}
                  strokeDasharray={hover !== null ? "3 3" : undefined}
                  vectorEffect="non-scaling-stroke"
                />
              </svg>

              {hover !== null ? (
                <div
                  className="pointer-events-none absolute top-0 z-10 -translate-x-1/2 rounded border border-border bg-surface-2 px-2 py-1 shadow-[var(--shadow-1)]"
                  style={{ left: `${(hover / DAY_MINUTES) * 100}%` }}
                >
                  <div className="num text-[10px] text-fg">{formatHHMM(hover)}</div>
                  <div className="num text-[10px] text-energy">{formatWatts(markWatts)}</div>
                </div>
              ) : null}
            </div>

            <div className="pointer-events-none absolute -bottom-0.5 left-0 right-0 flex justify-between">
              {["00:00", "06:00", "12:00", "18:00", "24:00"].map((label) => (
                <span key={label} className="num text-[9px] text-fg-subtle">
                  {label}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-4 flex min-h-0 flex-1 flex-wrap content-start gap-x-3 gap-y-1 overflow-y-auto border-t border-border px-3 pt-2">
            {model.series.map((item) => {
              const isHidden = hidden.has(item.id)
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => toggle(item.id)}
                  title={`${item.name} · ${formatKwh(item.energy)} kWh`}
                  className={cn(
                    "flex items-center gap-1.5 rounded-sm px-1 py-0.5 text-left transition-opacity",
                    isHidden ? "opacity-40" : "opacity-100 hover:bg-surface-2",
                  )}
                >
                  <span
                    className="inline-block size-2 shrink-0 rounded-[2px]"
                    style={{ backgroundColor: item.color }}
                    aria-hidden
                  />
                  <span className="num text-[10px] text-fg-muted">{item.name}</span>
                  <span className="num text-[10px] text-fg-subtle">{formatKwh(item.energy)}</span>
                </button>
              )
            })}
          </div>
        </>
      )}
    </Panel>
  )
}
