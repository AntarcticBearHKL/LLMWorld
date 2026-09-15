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
      title="同一运行的住户"
      hint={`${ids.length} 户`}
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
                "flex min-w-0 flex-col items-start gap-0.5 rounded-md border px-2.5 py-1.5 text-left transition-colors duration-150",
                active
                  ? "border-brand/50 bg-brand-soft"
                  : "border-border-strong bg-surface-2 hover:bg-surface-3",
              )}
            >
              <span
                className={cn(
                  "num text-[11px] leading-none font-semibold",
                  active ? "text-brand" : "text-fg",
                )}
              >
                {id}
              </span>
              <span className="num text-[10px] leading-none text-fg-subtle">
                {snapshot === undefined ? "—" : formatWatts(snapshot.total_watts)}
              </span>
            </button>
          )
        })}
        {ids.length === 0 ? (
          <span className="text-[11px] text-fg-subtle">尚未载入住户列表。</span>
        ) : null}
      </div>
    </Panel>
  )
}
