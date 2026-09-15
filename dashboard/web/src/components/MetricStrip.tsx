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
        label="全天用电"
        value={isPending ? SKELETON : formatKwh(metrics?.total_kwh ?? 0)}
        unit="kWh"
        tone="brand"
        detail={replay === undefined ? undefined : `${replay.house} · ${replay.policy}`}
      />
      <MetricCell
        label="峰值功率"
        value={isPending ? SKELETON : formatWatts(metrics?.peak_watts ?? 0)}
        tone="energy"
        detail={metrics === undefined ? undefined : `出现在 ${formatHHMM(metrics.peak_minute)}`}
      />
      <MetricCell
        label="傍晚用电"
        value={
          isPending || metrics?.evening_kwh === null || metrics?.evening_kwh === undefined
            ? SKELETON
            : formatKwh(metrics.evening_kwh)
        }
        unit="kWh"
        detail="17:00 – 22:00"
      />
      <MetricCell
        label="负荷率"
        value={
          isPending || metrics?.load_factor === null || metrics?.load_factor === undefined
            ? SKELETON
            : metrics.load_factor.toFixed(3)
        }
        detail="均值 / 峰值"
      />
      <MetricCell
        label="活跃电器"
        value={isPending ? SKELETON : String(running)}
        unit="台"
        detail={replay === undefined ? undefined : `共 ${replay.appliances.length} 台`}
      />
      <MetricCell
        label="成员"
        value={isPending ? SKELETON : String(replay?.members.length ?? 0)}
        unit="人"
        detail={replay?.household.household_type}
      />

      <div className="ml-auto flex items-center gap-4">
        <span className="flex items-center gap-1.5">
          <StatusDot on />
          <span className="text-[11px] text-fg-muted">用电中</span>
        </span>
        <span className="flex items-center gap-1.5">
          <StatusDot on={false} />
          <span className="text-[11px] text-fg-muted">待机 / 关闭</span>
        </span>
        <span className="flex items-center gap-1.5 text-fg-subtle" title="1 分钟仿真时间 = 1 秒真实时间（×1 倍速）">
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
