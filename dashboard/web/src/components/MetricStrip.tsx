import { Panel } from "@/components/primitives/Panel"
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
    <Panel title="Day metrics" hint="1440 pt · W / min" index={0}>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 lg:divide-x lg:divide-border">
        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="label-micro text-fg-muted">Total energy</span>
          <span className="flex items-baseline gap-1.5">
            <span className="num text-[22px] font-bold leading-none text-fg">
              {isPending ? SKELETON : formatKwh(metrics?.total_kwh ?? 0)}
            </span>
            <span className="text-[12px] font-medium text-fg-muted">kWh</span>
          </span>
          <span className="text-[12px] text-fg-subtle">
            {replay === undefined ? undefined : `${replay.house} · ${replay.policy}`}
          </span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="label-micro text-fg-muted">Peak load</span>
          <span className="flex items-baseline gap-1.5">
            <span className="num text-[22px] font-bold leading-none text-fg">
              {isPending ? SKELETON : formatWatts(metrics?.peak_watts ?? 0)}
            </span>
          </span>
          <span className="text-[12px] text-fg-subtle">
            {metrics === undefined ? undefined : `at ${formatHHMM(metrics.peak_minute)}`}
          </span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="label-micro text-fg-muted">Evening energy</span>
          <span className="flex items-baseline gap-1.5">
            <span className="num text-[22px] font-bold leading-none text-fg">
              {isPending || metrics?.evening_kwh === null || metrics?.evening_kwh === undefined
                ? SKELETON
                : formatKwh(metrics.evening_kwh)}
            </span>
            <span className="text-[12px] font-medium text-fg-muted">kWh</span>
          </span>
          <span className="text-[12px] text-fg-subtle">17:00 – 22:00</span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="label-micro text-fg-muted">Load factor</span>
          <span className="flex items-baseline gap-1.5">
            <span className="num text-[22px] font-bold leading-none text-fg">
              {isPending || metrics?.load_factor === null || metrics?.load_factor === undefined
                ? SKELETON
                : metrics.load_factor.toFixed(3)}
            </span>
          </span>
          <span className="text-[12px] text-fg-subtle">mean / peak</span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="label-micro text-fg-muted">Active appliances</span>
          <span className="flex items-baseline gap-1.5">
            <span className="num text-[22px] font-bold leading-none text-fg">
              {isPending ? SKELETON : String(running)}
            </span>
            <span className="text-[12px] font-medium text-fg-muted">on</span>
          </span>
          <span className="text-[12px] text-fg-subtle">
            {replay === undefined ? undefined : `${replay.appliances.length} total`}
          </span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="label-micro text-fg-muted">Members</span>
          <span className="flex items-baseline gap-1.5">
            <span className="num text-[22px] font-bold leading-none text-fg">
              {isPending ? SKELETON : String(replay?.members.length ?? 0)}
            </span>
            <span className="text-[12px] font-medium text-fg-muted">people</span>
          </span>
          <span className="text-[12px] text-fg-subtle">{replay?.household.household_type}</span>
        </div>
      </div>
    </Panel>
  )
}
