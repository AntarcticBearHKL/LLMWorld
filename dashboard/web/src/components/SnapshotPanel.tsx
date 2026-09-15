import { Plug, Users } from "lucide-react"

import { Panel } from "@/components/primitives/Panel"
import { StatusDot } from "@/components/primitives/StatusDot"
import { useSnapshot } from "@/hooks/useDayData"
import {
  APPLIANCE_STATE_LABELS,
  type ApplianceState,
  isRunning,
  stateOf,
} from "@/lib/appliance"
import { memberColorVar } from "@/lib/members"
import { formatHHMM, formatWatts } from "@/lib/time"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

const STATE_TONE: Record<ApplianceState, string> = {
  active: "text-energy",
  baseload: "text-fg-muted",
  standby: "text-fg-subtle",
  off: "text-fg-subtle",
}

export function SnapshotPanel() {
  const house = useTimeStore((state) => state.house)
  const minute = useTimeStore((state) => state.minute)
  const snapshotQuery = useSnapshot()
  const snapshot = snapshotQuery.data
  const current = snapshot?.houses.find((item) => item.house === house)

  const memberIds = (current?.people ?? []).map((person) => person.member)

  const running = [...(current?.powered ?? [])]
    .filter((appliance) =>
      isRunning(
        stateOf(
          {
            unique_id: appliance.unique_id,
            name: appliance.name,
            type: appliance.action === null ? "on_demand" : "on_demand",
            brand: null,
            room: appliance.room,
            owner: appliance.owner,
            power_watts: appliance.watts,
            standby_watts: 0,
            is_exclusive: false,
            available_actions: [],
          },
          {
            start: minute,
            end: minute + 1,
            watts: appliance.watts,
            action: appliance.action,
          },
        ),
      ),
    )
    .sort((a, b) => b.watts - a.watts)

  const label = (appliance: { watts: number; action: string | null }): string =>
    appliance.watts <= 0 || appliance.action === null
      ? APPLIANCE_STATE_LABELS.off
      : APPLIANCE_STATE_LABELS.active

  return (
    <Panel
      title="Current snapshot"
      hint={formatHHMM(minute)}
      index={1}
      className="min-h-[240px]"
      bodyClassName="flex min-h-0 flex-col overflow-y-auto"
      actions={
        <span className="num text-[12px] font-medium text-energy">
          {formatWatts(current?.total_watts ?? 0)}
        </span>
      }
    >
      <div className="flex items-center justify-between gap-3 border-b border-border px-4 py-2">
        <span className="label-micro truncate">{current?.household_type ?? "—"}</span>
        <span className="label-latin">
          {current !== undefined ? `${running.length} drawing power` : "house total"}
        </span>
      </div>

      <div className="flex flex-col gap-1.5 px-4 py-3">
        <span className="label-micro flex items-center gap-1.5">
          <Users className="size-3" aria-hidden />
          Member locations
        </span>
        <ul className="flex flex-col gap-1">
          {(current?.people ?? []).map((person) => (
            <li key={person.member} className="flex items-baseline gap-2">
              <span
                className="mt-1 inline-block size-1.5 shrink-0 rounded-full"
                style={{ backgroundColor: memberColorVar(person.member, memberIds) }}
                aria-hidden
              />
              <span className="num shrink-0 text-[11px] text-fg">{person.member}</span>
              <span className="min-w-0 flex-1 truncate text-right text-[11px] text-fg-muted">
                {person.location} · {person.activity}
              </span>
            </li>
          ))}
          {current === undefined ? (
            <li className="text-[11px] text-fg-subtle">
              {snapshotQuery.isPending ? "Loading…" : "No snapshot data at this minute."}
            </li>
          ) : null}
        </ul>
      </div>

      <div className="flex flex-col gap-1.5 border-t border-border px-4 py-3">
        <span className="label-micro flex items-center gap-1.5">
          <Plug className="size-3" aria-hidden />
          Powered appliances · {running.length}
        </span>
        <ul className="flex flex-col gap-1">
          {running.slice(0, 10).map((appliance) => (
            <li key={appliance.unique_id} className="flex items-center gap-2">
              <StatusDot on />
              <span className="min-w-0 flex-1 truncate text-[11px] text-fg-muted">
                {appliance.room !== null ? `${appliance.name} · ${appliance.room}` : appliance.name}
              </span>
              <span className={cn("num shrink-0 text-[10px]", STATE_TONE.active)}>
                {formatWatts(appliance.watts)}
              </span>
              <span className="label-latin shrink-0">{label(appliance)}</span>
            </li>
          ))}
          {running.length === 0 && current !== undefined ? (
            <li className="text-[11px] text-fg-subtle">No appliance drawing power at this minute.</li>
          ) : null}
        </ul>
      </div>
    </Panel>
  )
}
