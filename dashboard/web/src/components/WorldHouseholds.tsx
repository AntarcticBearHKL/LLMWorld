import { Lock } from "lucide-react"

import type { WorldInfo } from "@/api/types"
import { WorldDistricts } from "@/components/WorldDistricts"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useSpacetimes, useWorldDayBlocks } from "@/hooks/useSpacetimes"
import { errorMessage } from "@/lib/errors"
import { countLabel } from "@/lib/format"

function Chips({ items }: { items: string[] }) {
  return (
    <span className="flex flex-wrap gap-1.5">
      {items.map((item) => (
        <span
          key={item}
          className="num t-body rounded-full border border-border-strong bg-surface-2 px-2.5 py-0.5"
        >
          {item}
        </span>
      ))}
    </span>
  )
}

function FrozenHouseholds({ info }: { info: WorldInfo }) {
  const spacetimesQuery = useSpacetimes(info.world_id)
  const latest = spacetimesQuery.data?.[0] ?? null
  const run = latest?.name ?? ""
  const date = latest?.start_date ?? ""
  const policy = latest?.policy ?? "baseline"
  const blocksQuery = useWorldDayBlocks(info.world_id, run, date, policy, latest !== null)
  const blocks = blocksQuery.data?.blocks ?? []
  const grouped = blocks.some((block) => block.houses.length > 0)

  const noDaysNote = (
    <p className="t-caption">
      No simulated days in {latest?.name ?? "this world"} yet — household-to-block grouping appears
      after the simulation has run.
    </p>
  )

  return (
    <section className="card flex min-h-0 flex-1 flex-col overflow-hidden">
      <div className="mx-3 mt-3 flex shrink-0 flex-wrap items-center gap-2 rounded-xl border border-energy/30 bg-energy-soft px-3.5 py-2.5">
        <Lock className="size-3.5 shrink-0 text-energy" aria-hidden />
        <span className="t-caption">
          Households are frozen (this world has scenarios). Clone the world to edit.
        </span>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        {spacetimesQuery.isPending ? (
          <p className="t-caption">Loading scenarios…</p>
        ) : spacetimesQuery.isError ? (
          <div className="flex flex-col items-start gap-2">
            <p className="t-caption text-danger">
              Failed to load scenarios: {errorMessage(spacetimesQuery.error)}
            </p>
            <Button variant="outline" size="xs" onClick={() => void spacetimesQuery.refetch()}>
              Retry
            </Button>
          </div>
        ) : latest === null ? (
          <p className="t-caption">No scenarios found for this world.</p>
        ) : (
          <div className="flex flex-col gap-4">
            <span className="label-micro">
              {countLabel(info.districts.length, "district")} ·{" "}
              {countLabel(info.houses.length, "household")} · latest scenario{" "}
              <span className="num">{latest.name}</span>
            </span>

            {info.districts.length === 0 ? (
              <p className="t-caption">This world has no blocks yet.</p>
            ) : grouped ? (
              <ul className="grid grid-cols-1 gap-0 sm:grid-cols-2">
                {blocks.map((block) => (
                  <li
                    key={block.postcode}
                    className="card-lift flex flex-col gap-2 border-b border-border bg-surface-2 p-3.5 hover:border-border-strong sm:odd:border-r"
                  >
                    <span className="flex items-center gap-2">
                      <span className="num t-title">{block.postcode}</span>
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
                    <p className="t-caption">No households in this world.</p>
                  ) : (
                    <Chips items={info.houses} />
                  )}
                </div>
                {date.length === 0 ? (
                  noDaysNote
                ) : blocksQuery.isPending ? (
                  <p className="t-caption">Loading block structure…</p>
                ) : blocksQuery.isError ? (
                  <p className="t-caption">
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
  return info.frozen ? <FrozenHouseholds info={info} /> : <WorldDistricts info={info} />
}
