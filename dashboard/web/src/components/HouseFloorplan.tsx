import { DoorOpen, Users } from "lucide-react"

import type { DayReplay } from "@/api/types"
import { Panel } from "@/components/primitives/Panel"
import { isRunning, roomOf, stateAt, wattsAt } from "@/lib/appliance"
import { memberColorVar, memberInitial } from "@/lib/members"
import { formatWatts } from "@/lib/time"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

interface HouseFloorplanProps {
  replay: DayReplay | undefined
  className?: string
}

const ROOM_RANK = ["Living Room", "Kitchen", "Bathroom", "Dining Room", "Study", "Laundry"]

const rankOf = (room: string): number => {
  const index = ROOM_RANK.indexOf(room)
  return index < 0 ? ROOM_RANK.length + (room.startsWith("Bedroom") ? 0 : 1) : index
}

export function HouseFloorplan({ replay, className }: HouseFloorplanProps) {
  const minute = useTimeStore((state) => state.minute)
  const memberIds = replay?.members.map((member) => member.id) ?? []
  const rooms = [...(replay?.household.rooms ?? [])].sort(
    (a, b) => rankOf(a) - rankOf(b) || a.localeCompare(b),
  )

  const present = new Map<string, string[]>()
  const away: string[] = []
  for (const member of replay?.members ?? []) {
    const segment = member.activities.find((item) => minute >= item.start && minute < item.end)
    if (segment === undefined || !rooms.includes(segment.location)) {
      away.push(member.id)
      continue
    }
    const list = present.get(segment.location) ?? []
    list.push(member.id)
    present.set(segment.location, list)
  }

  const houseWatts = replay?.total_watts[Math.min(1439, Math.max(0, minute))] ?? 0
  const activeCount = (replay?.appliances ?? []).filter((appliance) =>
    isRunning(stateAt(appliance, minute)),
  ).length

  return (
    <Panel
      title="Floor plan"
      hint={`${rooms.length} rooms`}
      index={0}
      className={cn("min-h-[232px]", className)}
      bodyClassName="flex min-h-0 flex-col overflow-y-auto"
      actions={<span className="label-latin">{formatWatts(houseWatts)}</span>}
    >
      {replay === undefined ? (
        <div className="flex flex-1 items-center justify-center p-4">
          <span className="text-[11px] text-fg-subtle">Loading floor plan…</span>
        </div>
      ) : (
        <>
          <div className="grid shrink-0 grid-cols-2 gap-1.5 p-3 xl:grid-cols-3">
            {rooms.map((room) => {
              const here = present.get(room) ?? []
              const occupied = here.length > 0
              const roomAppliances = replay.appliances.filter(
                (appliance) => roomOf(appliance.info) === room,
              )
              const watts = roomAppliances.reduce(
                (sum, appliance) => sum + wattsAt(appliance, minute),
                0,
              )
              return (
                <div
                  key={room}
                  className={cn(
                    "flex min-h-[68px] flex-col justify-between rounded-md border px-2.5 py-2 transition-colors",
                    occupied ? "border-brand/45 bg-brand-soft" : "border-border-strong bg-surface-2",
                  )}
                >
                  <div className="flex items-baseline justify-between gap-1.5">
                    <span
                      className={cn(
                        "truncate text-[11px] font-medium",
                        occupied ? "text-fg" : "text-fg-muted",
                      )}
                    >
                      {room}
                    </span>
                    {watts > 0 ? (
                      <span className="num shrink-0 text-[9px] text-energy">
                        {formatWatts(watts)}
                      </span>
                    ) : null}
                  </div>

                  <div className="mt-1 flex flex-wrap items-center gap-1">
                    {here.map((member) => (
                      <span
                        key={member}
                        title={member}
                        className="num flex size-5 items-center justify-center rounded-full text-[9px] font-semibold"
                        style={{
                          backgroundColor: memberColorVar(member, memberIds),
                          color: "var(--bg)",
                        }}
                      >
                        {memberInitial(member)}
                      </span>
                    ))}
                    {roomAppliances.map((appliance) => {
                      const on = isRunning(stateAt(appliance, minute))
                      return (
                        <span
                          key={appliance.unique_id}
                          title={`${appliance.info.name} · ${formatWatts(wattsAt(appliance, minute))}`}
                          aria-hidden
                          className={cn(
                            "inline-block size-1.5 rounded-full",
                            on ? "bg-energy" : "bg-border-strong",
                          )}
                        />
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>

          <div className="mt-auto flex shrink-0 flex-wrap items-center gap-x-4 gap-y-1 border-t border-border px-3 py-2">
            <span className="label-micro flex items-center gap-1.5">
              <Users className="size-3" aria-hidden />
              Home {memberIds.length - away.length}/{memberIds.length}
            </span>
            {away.length > 0 ? (
              <span className="label-micro flex items-center gap-1.5">
                <DoorOpen className="size-3" aria-hidden />
                Away {away.join(" · ")}
              </span>
            ) : null}
            <span className="label-micro ml-auto">Powered appliances {activeCount}</span>
          </div>
        </>
      )}
    </Panel>
  )
}
