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
          <span className="t-micro">Total energy</span>
          <span className="flex items-baseline gap-1.5">
            <span className="t-display">
              {isPending ? SKELETON : formatKwh(metrics?.total_kwh ?? 0)}
            </span>
            <span className="t-caption">kWh</span>
          </span>
          <span className="t-caption">
            {replay === undefined ? undefined : `${replay.house} · ${replay.policy}`}
          </span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="t-micro">Peak load</span>
          <span className="flex items-baseline gap-1.5">
            <span className="t-display">
              {isPending ? SKELETON : formatWatts(metrics?.peak_watts ?? 0)}
            </span>
          </span>
          <span className="t-caption">
            {metrics === undefined ? undefined : `at ${formatHHMM(metrics.peak_minute)}`}
          </span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="t-micro">Evening energy</span>
          <span className="flex items-baseline gap-1.5">
            <span className="t-display">
              {isPending || metrics?.evening_kwh === null || metrics?.evening_kwh === undefined
                ? SKELETON
                : formatKwh(metrics.evening_kwh)}
            </span>
            <span className="t-caption">kWh</span>
          </span>
          <span className="t-caption">17:00 – 22:00</span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="t-micro">Load factor</span>
          <span className="flex items-baseline gap-1.5">
            <span className="t-display">
              {isPending || metrics?.load_factor === null || metrics?.load_factor === undefined
                ? SKELETON
                : metrics.load_factor.toFixed(3)}
            </span>
          </span>
          <span className="t-caption">mean / peak</span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="t-micro">Active appliances</span>
          <span className="flex items-baseline gap-1.5">
            <span className="t-display">
              {isPending ? SKELETON : String(running)}
            </span>
            <span className="t-caption">on</span>
          </span>
          <span className="t-caption">
            {replay === undefined ? undefined : `${replay.appliances.length} total`}
          </span>
        </div>

        <div className="flex flex-col gap-1 px-4 py-3">
          <span className="t-micro">Members</span>
          <span className="flex items-baseline gap-1.5">
            <span className="t-display">
              {isPending ? SKELETON : String(replay?.members.length ?? 0)}
            </span>
            <span className="t-caption">people</span>
          </span>
          <span className="t-caption">{replay?.household.household_type}</span>
        </div>
      </div>
    </Panel>
  )
}
