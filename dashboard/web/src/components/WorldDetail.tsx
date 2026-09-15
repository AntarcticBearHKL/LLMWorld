import { ArrowLeft } from "lucide-react"

import { CloneWorldButton } from "@/components/CloneWorldButton"
import { SpacetimeList } from "@/components/SpacetimeList"
import { WorldHouseholds } from "@/components/WorldHouseholds"
import { WorldBadge } from "@/components/primitives/WorldBadge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useWorld } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { countLabel } from "@/lib/format"
import { useTimeStore, type WorldTab } from "@/store/time"

const isWorldTab = (value: string): value is WorldTab =>
  value === "spacetime" || value === "household"

export function WorldDetail() {
  const world = useTimeStore((state) => state.world)
  const tab = useTimeStore((state) => state.tab)
  const setTab = useTimeStore((state) => state.setTab)
  const setView = useTimeStore((state) => state.setView)
  const setWorld = useTimeStore((state) => state.setWorld)
  const worldQuery = useWorld(world)

  const back = (
    <Button variant="ghost" size="xs" onClick={() => setView("worlds")}>
      <ArrowLeft />
      All worlds
    </Button>
  )

  if (world.length === 0) {
    return (
      <div className="mx-auto flex h-full w-full max-w-5xl flex-col gap-3">
        <section className="flex flex-col items-start gap-3 rounded-lg border border-border bg-surface p-4">
          {back}
          <p className="text-[11px] text-fg-subtle">
            No world selected. Pick one from the worlds list.
          </p>
        </section>
      </div>
    )
  }

  if (worldQuery.isPending) {
    return (
      <div className="mx-auto flex h-full w-full max-w-5xl flex-col gap-3">
        <section className="flex flex-col items-start gap-3 rounded-lg border border-border bg-surface p-4">
          {back}
          <p className="text-[11px] text-fg-subtle">
            Loading world <span className="num">{world}</span>…
          </p>
        </section>
      </div>
    )
  }

  const info = worldQuery.data

  if (worldQuery.isError || info === undefined) {
    return (
      <div className="mx-auto flex h-full w-full max-w-5xl flex-col gap-3">
        <section className="flex flex-col items-start gap-3 rounded-lg border border-border bg-surface p-4">
          {back}
          <p className="text-[11px] text-danger">
            Failed to load world <span className="num">{world}</span>: {errorMessage(worldQuery.error)}
          </p>
          <Button variant="outline" size="xs" onClick={() => void worldQuery.refetch()}>
            Retry
          </Button>
        </section>
      </div>
    )
  }

  return (
    <div className="mx-auto flex h-full min-h-0 w-full max-w-5xl flex-col gap-3">
      <header className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-2 rounded-lg border border-border bg-surface px-3 py-2.5">
        {back}
        <span className="h-4 w-px shrink-0 bg-border-strong" aria-hidden />
        <span className="num truncate text-[13px] font-semibold text-fg">{info.world_id}</span>
        <WorldBadge frozen={info.frozen} />
        <span className="label-micro">
          {countLabel(info.districts.length, "block")} ·{" "}
          {countLabel(info.houses.length, "household")} ·{" "}
          {countLabel(info.spacetimes.length, "spacetime")}
        </span>
        <span className="ml-auto">
          <CloneWorldButton
            world={info.world_id}
            size="sm"
            label="Clone world"
            onCloned={(worldId) => {
              setWorld(worldId)
              setTab("household")
            }}
          />
        </span>
      </header>

      <Tabs
        value={tab}
        onValueChange={(value) => {
          if (isWorldTab(value)) setTab(value)
        }}
        className="flex min-h-0 flex-1 flex-col"
      >
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          <TabsList className="h-8 p-0.5">
            <TabsTrigger value="spacetime" className="h-7 px-3 text-[12px]">
              Spacetimes{" "}
              <span className="num text-[10px] text-fg-subtle">{info.spacetimes.length}</span>
            </TabsTrigger>
            <TabsTrigger value="household" className="h-7 px-3 text-[12px]">
              Households <span className="num text-[10px] text-fg-subtle">{info.houses.length}</span>
            </TabsTrigger>
          </TabsList>
          <span className="label-micro">Spacetimes read the households; they never change them.</span>
        </div>

        <TabsContent value="spacetime" className="mt-0 flex min-h-0 flex-1 flex-col">
          <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-border bg-surface">
            <SpacetimeList world={info.world_id} />
          </section>
        </TabsContent>

        <TabsContent value="household" className="mt-0 flex min-h-0 flex-1 flex-col">
          <WorldHouseholds info={info} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
