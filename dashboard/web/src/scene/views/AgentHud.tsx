import { useEffect } from "react"

import { X } from "lucide-react"

import type { ApplianceDay, DayReplay } from "@/api/types"
import { Button } from "@/components/ui/button"
import { APPLIANCE_STATE_LABELS, roomOf, stateAt, wattsAt } from "@/lib/appliance"
import { memberColorVar, memberInitial } from "@/lib/members"
import { formatHHMM, formatMinutesAsDuration, formatWatts } from "@/lib/time"
import { useTimeStore } from "@/store/time"

interface AgentHudProps {
  replay: DayReplay | undefined
  onOpenPipeline?: (memberId: string) => void
}

const POWERED_ACTIONS = new Set(["use", "run", "charge_home"])

const isAppliance = (value: ApplianceDay | undefined): value is ApplianceDay => value !== undefined

export function AgentHud({ replay, onOpenPipeline }: AgentHudProps) {
  const selectedMember = useTimeStore((store) => store.selectedMember)
  const setSelectedMember = useTimeStore((store) => store.setSelectedMember)
  const minute = useTimeStore((store) => store.minute)

  useEffect(() => {
    if (selectedMember === null) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setSelectedMember(null)
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [selectedMember, setSelectedMember])

  if (replay === undefined || selectedMember === null) return null
  const member = replay.members.find((item) => item.id === selectedMember)
  if (member === undefined) return null

  const memberIds = replay.members.map((item) => item.id)
  const segment = member.activities.find((item) => minute >= item.start && minute < item.end)
  const decision = member.decisions.find((item) => minute >= item.start && minute < item.end)
  const byId = new Map(replay.appliances.map((item) => [item.unique_id, item]))
  const used = (decision?.operations ?? [])
    .filter((operation) => POWERED_ACTIONS.has(operation.action))
    .map((operation) => byId.get(operation.unique_id))
    .filter(isAppliance)
  const totalWatts = used.reduce((sum, appliance) => sum + wattsAt(appliance, minute), 0)
  const upcoming = member.activities.filter((item) => item.start > minute).slice(0, 2)

  return (
    <aside
      className="chrome-lg pointer-events-auto absolute bottom-3 left-3 z-20 flex max-h-[min(420px,calc(100%-24px))] w-[320px] flex-col overflow-hidden shadow-3"
      aria-label="Member details"
    >
      <header className="flex shrink-0 items-center gap-2 border-b border-border px-3 py-2">
        <span
          className="num flex size-6 items-center justify-center rounded-full text-[12px] font-semibold"
          style={{ backgroundColor: memberColorVar(member.id, memberIds), color: "var(--bg)" }}
        >
          {memberInitial(member.id)}
        </span>
        <span className="num text-[14px] font-semibold text-fg">{member.id}</span>
        <span className="label-micro text-fg-muted truncate">{member.info.bedroom ?? ""}</span>
        <Button
          variant="ghost"
          size="icon-sm"
          className="ml-auto"
          aria-label="Close"
          onClick={() => setSelectedMember(null)}
        >
          <X />
        </Button>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-2.5">
        <div className="flex flex-col gap-0.5">
          <span className="num text-[12px] text-fg-muted">
            {member.info.age !== null ? `age ${member.info.age}` : "Age unknown"}
            {member.info.gender !== null ? ` · ${member.info.gender}` : ""}
          </span>
          {member.info.occupation !== null ? (
            <span className="text-[13px] leading-snug text-fg-muted" title={member.info.occupation}>
              {member.info.occupation}
            </span>
          ) : null}
          {member.info.persona.length > 0 ? (
            <span className="mt-0.5 line-clamp-2 text-[12px] leading-snug text-fg-muted">
              {member.info.persona}
            </span>
          ) : null}
        </div>

        <section className="mt-3 flex flex-col gap-1 border-t border-border pt-2">
          <span className="label-micro text-fg-muted">Now</span>
          {segment !== undefined ? (
            <>
              <span className="text-[13px] leading-snug text-fg">{segment.activity}</span>
              <span className="num text-[12px] text-fg-muted">
                {segment.location} · {formatHHMM(segment.start)}–{formatHHMM(segment.end)} ·{" "}
                {formatMinutesAsDuration(minute - segment.start)} elapsed
              </span>
            </>
          ) : (
            <span className="text-[13px] text-fg-muted">No activity recorded at this time.</span>
          )}
        </section>

        <section className="mt-3 flex flex-col gap-1 border-t border-border pt-2">
          <span className="label-micro text-fg-muted">
            In use · {used.length} appliances · {formatWatts(totalWatts)} total
          </span>
          {used.length === 0 ? (
            <span className="text-[13px] text-fg-muted">No appliance in use.</span>
          ) : (
            <ul className="flex flex-col gap-1">
              {used.map((appliance) => (
                <li key={appliance.unique_id} className="flex items-baseline gap-2">
                  <span className="min-w-0 flex-1 truncate text-[13px] text-fg-muted">
                    {appliance.info.name} · {roomOf(appliance.info)}
                  </span>
                  <span className="num shrink-0 text-[12px] text-energy">
                    {formatWatts(wattsAt(appliance, minute))}
                  </span>
                  <span className="label-latin shrink-0 text-fg-muted">
                    {APPLIANCE_STATE_LABELS[stateAt(appliance, minute)]}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="mt-3 flex flex-col gap-1 border-t border-border pt-2">
          <span className="label-micro text-fg-muted">Next</span>
          {upcoming.length === 0 ? (
            <span className="text-[13px] text-fg-muted">No more activity today.</span>
          ) : (
            <ul className="flex flex-col gap-1">
              {upcoming.map((item) => (
                <li key={`${item.start}-${item.activity.slice(0, 12)}`} className="flex items-baseline gap-2">
                  <span className="num shrink-0 text-[12px] text-brand">{formatHHMM(item.start)}</span>
                  <span className="min-w-0 flex-1 truncate text-[13px] text-fg-muted">{item.activity}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {onOpenPipeline !== undefined ? (
        <footer className="shrink-0 border-t border-border px-3 py-2">
          <Button variant="outline" size="sm" className="w-full" onClick={() => onOpenPipeline(member.id)}>
            Open decision pipeline
          </Button>
        </footer>
      ) : null}
    </aside>
  )
}
