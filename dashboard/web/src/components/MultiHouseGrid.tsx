import { ChevronRight, Users } from "lucide-react"

import { useSnapshot } from "@/hooks/useDayData"
import { memberColorVar, memberInitial } from "@/lib/members"
import { formatHHMM, formatWatts } from "@/lib/time"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

interface MultiHouseGridProps {
  onOpen: (house: string) => void
  houses?: readonly string[]
}

export function MultiHouseGrid({ onOpen, houses }: MultiHouseGridProps) {
  const minute = useTimeStore((state) => state.minute)
  const house = useTimeStore((state) => state.house)
  const run = useTimeStore((state) => state.run)
  const snapshotQuery = useSnapshot()
  const snapshot = snapshotQuery.data

  if (run.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-2.5 p-8 text-center">
        <p className="text-[15px] font-medium text-fg">No replay data yet</p>
        <p className="label-micro max-w-[420px] leading-relaxed">
          Pick a world and open one of its scenarios to replay a simulated day. This grid then shows
          what every household is doing and which appliances draw power.
        </p>
        <span className="label-latin mt-1">world → scenario → watch</span>
      </div>
    )
  }

  if (snapshotQuery.isPending) {
    return <p className="p-6 text-[13px] text-fg-subtle">Loading household snapshot…</p>
  }

  if (snapshot === undefined) {
    return <p className="p-6 text-[13px] text-fg-subtle">No household data at this minute.</p>
  }

  const visible =
    houses === undefined
      ? snapshot.houses
      : snapshot.houses.filter((item) => houses.includes(item.house))

  if (visible.length === 0) {
    return (
      <p className="p-6 text-[13px] text-fg-subtle">
        No households in this selection for this day.
      </p>
    )
  }

  const peak = visible.reduce((max, item) => Math.max(max, item.total_watts), 0) || 1

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-baseline gap-3 border-b border-border px-4 py-3">
        <span className="text-[15px] font-bold tracking-[-0.01em] text-fg">Household grid</span>
        <span className="num text-[13px] text-fg-subtle">
          {visible.length} households · {formatHHMM(minute)}
        </span>
        <span className="label-latin ml-auto">Select a household to inspect its members</span>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-1 content-start gap-3 overflow-y-auto p-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
        {visible.map((item) => {
          const memberIds = item.people.map((person) => person.member)
          const running = item.powered.filter((appliance) => appliance.watts > 0)
          const isCurrent = item.house === house
          return (
            <button
              key={item.house}
              type="button"
              onClick={() => onOpen(item.house)}
              className={cn(
                "card card-lift flex min-h-[236px] flex-col gap-2.5 p-3.5 text-left hover:-translate-y-0.5 hover:shadow-2",
                isCurrent
                  ? "border-brand-ring bg-brand-soft"
                  : "hover:border-border-strong",
              )}
            >
              <div className="flex items-center gap-2">
                <span className="num text-[15px] font-semibold text-fg">{item.house}</span>
                <ChevronRight className="size-3.5 shrink-0 text-fg-subtle" aria-hidden />
                <span className="num ml-auto text-[15px] font-medium text-energy">
                  {formatWatts(item.total_watts)}
                </span>
              </div>

              <div className="flex items-baseline gap-2">
                <span className="label-micro min-w-0 flex-1 truncate">{item.household_type}</span>
                <span className="label-micro flex shrink-0 items-center gap-1">
                  <Users className="size-3" aria-hidden />
                  {item.people.length}
                </span>
              </div>

              <div className="h-1 w-full overflow-hidden rounded-full bg-surface-3">
                <div
                  className="h-full rounded-full bg-energy"
                  style={{ width: `${Math.round((item.total_watts / peak) * 100)}%` }}
                />
              </div>

              <ul className="flex flex-col gap-1.5">
                {item.people.slice(0, 5).map((person) => (
                  <li key={person.member} className="flex items-start gap-1.5">
                    <span
                      className="num mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full text-[12px] font-semibold"
                      style={{
                        backgroundColor: memberColorVar(person.member, memberIds),
                        color: "var(--bg)",
                      }}
                    >
                      {memberInitial(person.member)}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="num text-[12px] text-fg">{person.member}</span>
                      <span className="ml-1.5 text-[12px] text-fg-subtle">{person.location}</span>
                      <span className="mt-px line-clamp-2 block text-[12px] leading-snug text-fg-muted">
                        {person.activity}
                      </span>
                    </span>
                  </li>
                ))}
                {item.people.length > 5 ? (
                  <li className="num text-[12px] text-fg-subtle">
                    {item.people.length - 5} more members
                  </li>
                ) : null}
              </ul>

              <div className="mt-auto flex flex-wrap items-center gap-1 border-t border-border pt-2">
                {running.length === 0 ? (
                  <span className="text-[12px] text-fg-subtle">No appliance drawing power</span>
                ) : (
                  <>
                    <span className="label-micro shrink-0">Drawing {running.length}</span>
                    {running.slice(0, 3).map((appliance) => (
                      <span
                        key={appliance.unique_id}
                        className="num truncate rounded-full border border-border-strong bg-surface-2 px-2 py-px text-[12px] text-fg-muted"
                      >
                        {appliance.name}
                      </span>
                    ))}
                    {running.length > 3 ? (
                      <span className="num text-[12px] text-fg-subtle">+{running.length - 3}</span>
                    ) : null}
                  </>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
