import { Home } from "lucide-react"

import { Panel } from "@/components/primitives/Panel"
import { useRunMeta, useSnapshot } from "@/hooks/useDayData"
import { formatWatts } from "@/lib/time"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

export function HouseSwitcher() {
  const run = useTimeStore((state) => state.run)
  const house = useTimeStore((state) => state.house)
  const setSelection = useTimeStore((state) => state.setSelection)
  const metaQuery = useRunMeta(run)
  const snapshotQuery = useSnapshot()

  const ids = metaQuery.data?.houses ?? []
  const live = new Map((snapshotQuery.data?.houses ?? []).map((item) => [item.house, item]))

  return (
    <Panel
      title="Households in this scenario"
      hint={`${ids.length} households`}
      index={2}
      bodyClassName="p-3"
      actions={<Home className="size-3.5 text-fg-subtle" aria-hidden />}
    >
      <div className="flex flex-wrap gap-1.5">
        {ids.map((id) => {
          const active = id === house
          const snapshot = live.get(id)
          return (
            <button
              key={id}
              type="button"
              onClick={() => setSelection({ house: id })}
              title={snapshot?.household_type ?? id}
              className={cn(
                "card-lift flex min-w-0 flex-col items-start gap-0.5 rounded-xl border px-2.5 py-1.5 text-left",
                active
                  ? "border-brand-ring bg-brand-soft"
                  : "border-border bg-surface-2 hover:border-border-strong hover:shadow-1",
              )}
            >
              <span
                className={cn(
                  "num text-[13px] leading-none font-semibold",
                  active ? "text-fg" : "text-fg-muted",
                )}
              >
                {id}
              </span>
              <span className="num text-[12px] leading-none text-fg-subtle">
                {snapshot === undefined ? "—" : formatWatts(snapshot.total_watts)}
              </span>
            </button>
          )
        })}
        {ids.length === 0 ? (
          <span className="text-[13px] text-fg-subtle">No household list yet.</span>
        ) : null}
      </div>
    </Panel>
  )
}
