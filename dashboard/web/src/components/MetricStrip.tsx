import { Activity, Clock, Gauge, Zap } from "lucide-react"

import { MetricCell } from "@/components/primitives/MetricCell"
import { StatusDot } from "@/components/primitives/StatusDot"
import type { DayReplay } from "@/api/types"
import { formatHHMM, formatKwh, formatWatts } from "@/lib/time"

interface MetricStripProps {
  replay: DayReplay | undefined
  isPending: boolean
}

const SKELETON = "—"

export function MetricStrip({ replay, isPending }: MetricStripProps) {
  const metrics = replay?.metrics
  const running = replay?.appliances.filter((item) => item.peak_watts > 0).length ?? 0

  return (
    <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
      <MetricCell
        label="Total energy"
        value={isPending ? SKELETON : formatKwh(metrics?.total_kwh ?? 0)}
        unit="kWh"
        tone="brand"
        detail={replay === undefined ? undefined : `${replay.house} · ${replay.policy}`}
      />
      <MetricCell
        label="Peak load"
        value={isPending ? SKELETON : formatWatts(metrics?.peak_watts ?? 0)}
        tone="energy"
        detail={metrics === undefined ? undefined : `at ${formatHHMM(metrics.peak_minute)}`}
      />
      <MetricCell
        label="Evening energy"
        value={
          isPending || metrics?.evening_kwh === null || metrics?.evening_kwh === undefined
            ? SKELETON
            : formatKwh(metrics.evening_kwh)
        }
        unit="kWh"
        detail="17:00 – 22:00"
      />
      <MetricCell
        label="Load factor"
        value={
          isPending || metrics?.load_factor === null || metrics?.load_factor === undefined
            ? SKELETON
            : metrics.load_factor.toFixed(3)
        }
        detail="mean / peak"
      />
      <MetricCell
        label="Active appliances"
        value={isPending ? SKELETON : String(running)}
        unit="on"
        detail={replay === undefined ? undefined : `${replay.appliances.length} total`}
      />
      <MetricCell
        label="Members"
        value={isPending ? SKELETON : String(replay?.members.length ?? 0)}
        unit="people"
        detail={replay?.household.household_type}
      />

      <div className="ml-auto flex flex-wrap items-center gap-x-4 gap-y-2">
        <span className="chip">
          <StatusDot on />
          <span className="text-[11px] text-fg-muted">Drawing power</span>
        </span>
        <span className="chip">
          <StatusDot on={false} />
          <span className="text-[11px] text-fg-muted">Standby / off</span>
        </span>
        <span
          className="flex items-center gap-1.5 text-fg-subtle"
          title="1 minute of simulated time = 1 second of real time at ×1 speed"
        >
          <Clock className="size-3" aria-hidden />
          <span className="label-latin">1 min / s</span>
        </span>
        <span className="flex items-center gap-1.5 text-fg-subtle">
          <Gauge className="size-3" aria-hidden />
          <span className="label-latin">1440 pt</span>
        </span>
        <span className="flex items-center gap-1.5 text-fg-subtle">
          <Zap className="size-3" aria-hidden />
          <span className="label-latin">w / min</span>
        </span>
        <span className="flex items-center gap-1.5 text-fg-subtle">
          <Activity className="size-3" aria-hidden />
          <span className="label-latin">half-open</span>
        </span>
      </div>
    </div>
  )
}
