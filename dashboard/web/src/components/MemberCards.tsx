import { Clock } from "lucide-react"

import type { DayReplay } from "@/api/types"
import { Panel } from "@/components/primitives/Panel"
import { intervalAt, isRunning, stateAt } from "@/lib/appliance"
import { memberColorVar, memberInitial } from "@/lib/members"
import { formatHHMM, formatWatts } from "@/lib/time"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

interface MemberCardsProps {
  replay: DayReplay | undefined
}

const POWERED_ACTIONS = new Set(["use", "run", "charge_home"])

export function MemberCards({ replay }: MemberCardsProps) {
  const minute = useTimeStore((state) => state.minute)
  const selectedMember = useTimeStore((state) => state.selectedMember)
  const setSelectedMember = useTimeStore((state) => state.setSelectedMember)

  const memberIds = replay?.members.map((member) => member.id) ?? []
  const applianceById = new Map((replay?.appliances ?? []).map((item) => [item.unique_id, item]))

  return (
    <Panel
      title="Household members"
      hint={formatHHMM(minute)}
      index={1}
      className="shrink-0"
      bodyClassName="overflow-x-auto"
      actions={
        <span className="label-latin">
          {replay !== undefined ? `${replay.members.length} members` : "—"}
        </span>
      }
    >
      {replay === undefined ? (
        <div className="flex items-center justify-center px-4 py-8">
          <span className="text-[11px] text-fg-subtle">Loading members…</span>
        </div>
      ) : (
        <div className="flex min-w-full gap-2.5 p-3">
          {replay.members.map((member) => {
            const segment = member.activities.find(
              (item) => minute >= item.start && minute < item.end,
            )
            const decision = member.decisions.find(
              (item) => minute >= item.start && minute < item.end,
            )
            const usedIds = (decision?.operations ?? [])
              .filter((operation) => POWERED_ACTIONS.has(operation.action))
              .map((operation) => operation.unique_id)
            const used = [...new Set(usedIds)]
              .map((id) => applianceById.get(id))
              .filter((item) => item !== undefined)
              .map((item) => ({
                uniqueId: item.unique_id,
                name: item.info.name,
                watts: intervalAt(item, minute)?.watts ?? 0,
              }))
              .sort((a, b) => b.watts - a.watts)

            const dayWatts = used.reduce((sum, item) => sum + item.watts, 0)
            const next = member.activities.find((item) => item.start >= minute)
            const done = (minute / 1440) * 100
            const isSelected = selectedMember === member.id
            const running = member.decisions.length > 0

            return (
              <button
                key={member.id}
                type="button"
                onClick={() => setSelectedMember(isSelected ? null : member.id)}
                className={cn(
                  "card-lift flex w-[228px] shrink-0 flex-col gap-2 rounded-xl border px-3 py-2.5 text-left",
                  isSelected
                    ? "border-brand-ring bg-brand-soft"
                    : "border-border bg-surface-2 hover:border-border-strong hover:shadow-1",
                )}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="num flex size-6 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold"
                    style={{
                      backgroundColor: memberColorVar(member.id, memberIds),
                      color: "var(--bg)",
                    }}
                  >
                    {memberInitial(member.id)}
                  </span>
                  <span className="num min-w-0 flex-1 truncate text-[12px] font-semibold text-fg">
                    {member.id}
                  </span>
                  <span
                    className={cn(
                      "label-latin shrink-0",
                      member.info.is_out || !running ? "text-fg-subtle" : "text-brand",
                    )}
                  >
                    {segment !== undefined && segment.location.toLowerCase().includes("out")
                      ? "Away"
                      : "Home"}
                  </span>
                </div>

                <div className="flex flex-col gap-0.5">
                  <span className="num text-[10px] text-fg-subtle">
                    {member.info.bedroom ?? "—"}
                    {member.info.age !== null ? ` · age ${member.info.age}` : ""}
                  </span>
                  <span className="text-[11px] leading-snug text-fg">
                    {segment !== undefined ? segment.activity : "No activity recorded at this time"}
                  </span>
                  {segment !== undefined ? (
                    <span className="num text-[9px] text-fg-subtle">
                      {segment.location} · {formatHHMM(segment.start)}–{formatHHMM(segment.end)}
                    </span>
                  ) : null}
                </div>

                <div className="flex flex-wrap items-center gap-1">
                  {used.length === 0 ? (
                    <span className="text-[10px] text-fg-subtle">No appliance in use</span>
                  ) : (
                    <>
                      {used.slice(0, 3).map((item) => (
                        <span
                          key={item.uniqueId}
                          className="num rounded-full border border-energy/40 bg-energy-soft px-2 py-px text-[9px] text-energy"
                        >
                          {item.name}
                          {item.watts > 0 ? ` ${Math.round(item.watts)}W` : ""}
                        </span>
                      ))}
                      {used.length > 3 ? (
                        <span className="num text-[9px] text-fg-subtle">+{used.length - 3}</span>
                      ) : null}
                    </>
                  )}
                </div>

                <div className="mt-auto flex items-center gap-2 border-t border-border pt-1.5">
                  <span className="num text-[9px] text-fg-subtle">
                    {dayWatts > 0 ? formatWatts(dayWatts) : "—"}
                  </span>
                  <span className="num ml-auto flex items-center gap-1 text-[9px] text-fg-subtle">
                    <Clock className="size-2.5" aria-hidden />
                    {next !== undefined
                      ? `${formatHHMM(next.start)} ${next.activity.slice(0, 12)}`
                      : "Day over"}
                  </span>
                </div>

                <div className="h-0.5 w-full overflow-hidden rounded-full bg-surface-3">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${done}%`,
                      backgroundColor: memberColorVar(member.id, memberIds),
                    }}
                  />
                </div>
              </button>
            )
          })}
        </div>
      )}
      {replay !== undefined ? (
        <p className="sr-only">
          {replay.appliances.filter((item) => isRunning(stateAt(item, minute))).length} appliances
          drawing power.
        </p>
      ) : null}
    </Panel>
  )
}
