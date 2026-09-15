import { Lock } from "lucide-react"

import type { WorldInfo } from "@/api/types"
import { CloneWorldButton } from "@/components/CloneWorldButton"
import { WorldBuilder } from "@/components/WorldBuilder"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useSpacetimes, useWorldDayBlocks } from "@/hooks/useSpacetimes"
import { errorMessage } from "@/lib/errors"
import { countLabel } from "@/lib/format"
import { useTimeStore } from "@/store/time"

function Chips({ items }: { items: string[] }) {
  return (
    <span className="flex flex-wrap gap-1.5">
      {items.map((item) => (
        <span
          key={item}
          className="num rounded-sm border border-border-strong px-1.5 py-0.5 text-[10px] text-fg-muted"
        >
          {item}
        </span>
      ))}
    </span>
  )
}

function FrozenHouseholds({ info }: { info: WorldInfo }) {
  const setWorld = useTimeStore((state) => state.setWorld)
  const setTab = useTimeStore((state) => state.setTab)
  const spacetimesQuery = useSpacetimes(info.world_id)
  const latest = spacetimesQuery.data?.[0] ?? null
  const run = latest?.name ?? ""
  const date = latest?.start_date ?? ""
  const policy = latest?.policy ?? "baseline"
  const blocksQuery = useWorldDayBlocks(info.world_id, run, date, policy, latest !== null)
  const blocks = blocksQuery.data?.blocks ?? []
  const grouped = blocks.some((block) => block.houses.length > 0)

  const noDaysNote = (
    <p className="text-[10px] text-fg-subtle">
      No simulated days in {latest?.name ?? "this world"} yet — household-to-block grouping appears
      after the simulation has run.
    </p>
  )

  return (
    <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-border bg-surface">
      <div className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border bg-energy-soft px-4 py-2.5">
        <Lock className="size-3.5 shrink-0 text-energy" aria-hidden />
        <span className="text-[11px] text-fg">
          Households are frozen (this world has spacetimes). Clone the world to edit.
        </span>
        <span className="ml-auto">
          <CloneWorldButton
            world={info.world_id}
            label="Clone world"
            onCloned={(worldId) => {
              setWorld(worldId)
              setTab("household")
            }}
          />
        </span>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        {spacetimesQuery.isPending ? (
          <p className="text-[11px] text-fg-subtle">Loading spacetimes…</p>
        ) : spacetimesQuery.isError ? (
          <div className="flex flex-col items-start gap-2">
            <p className="text-[11px] text-danger">
              Failed to load spacetimes: {errorMessage(spacetimesQuery.error)}
            </p>
            <Button variant="outline" size="xs" onClick={() => void spacetimesQuery.refetch()}>
              Retry
            </Button>
          </div>
        ) : latest === null ? (
          <p className="text-[11px] text-fg-subtle">No spacetimes found for this world.</p>
        ) : (
          <div className="flex flex-col gap-4">
            <span className="label-micro">
              {countLabel(info.districts.length, "block")} ·{" "}
              {countLabel(info.houses.length, "household")} · latest spacetime{" "}
              <span className="num">{latest.name}</span>
            </span>

            {info.districts.length === 0 ? (
              <p className="text-[11px] text-fg-subtle">This world has no blocks yet.</p>
            ) : grouped ? (
              <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {blocks.map((block) => (
                  <li
                    key={block.postcode}
                    className="flex flex-col gap-2 rounded-lg border border-border p-3"
                  >
                    <span className="flex items-center gap-2">
                      <span className="num text-[12px] text-fg">{block.postcode}</span>
                      <Badge variant="outline" className="label-latin">
                        {countLabel(block.house_count, "household")}
                      </Badge>
                    </span>
                    <Chips items={block.houses} />
                    <span className="num label-micro">
                      {block.total_kwh.toFixed(2)} kWh · peak {Math.round(block.peak_watts)} W
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="flex flex-col gap-4">
                <div className="flex flex-col gap-1.5">
                  <span className="label-micro">Blocks</span>
                  <Chips items={info.districts} />
                </div>
                <div className="flex flex-col gap-1.5">
                  <span className="label-micro">Households</span>
                  {info.houses.length === 0 ? (
                    <p className="text-[11px] text-fg-subtle">No households in this world.</p>
                  ) : (
                    <Chips items={info.houses} />
                  )}
                </div>
                {date.length === 0 ? (
                  noDaysNote
                ) : blocksQuery.isPending ? (
                  <p className="text-[11px] text-fg-subtle">Loading block structure…</p>
                ) : blocksQuery.isError ? (
                  <p className="text-[11px] text-fg-subtle">
                    Block structure unavailable: {errorMessage(blocksQuery.error)}
                  </p>
                ) : (
                  noDaysNote
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}

export function WorldHouseholds({ info }: { info: WorldInfo }) {
  return info.frozen ? <FrozenHouseholds info={info} /> : <WorldBuilder />
}
