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
  const setWorld = useTimeStore((state) => state.setWorld)
  const worldQuery = useWorld(world)

  const back = (
    <Button variant="ghost" size="xs" className="lg:hidden" onClick={() => setWorld("")}>
      <ArrowLeft />
      All worlds
    </Button>
  )

  if (world.length === 0) {
    return (
      <section className="card flex h-full min-h-0 flex-col items-start justify-center gap-2 p-8">
        <h2 className="text-[16px] font-bold tracking-[-0.01em] text-fg">Select a world</h2>
        <p className="max-w-[420px] text-[14px] leading-relaxed text-fg-muted">
          Pick a world from the list on the left to open its spacetimes and households, or create a
          new blank world there.
        </p>
      </section>
    )
  }

  if (worldQuery.isPending) {
    return (
      <section className="card flex h-full min-h-0 flex-col items-start gap-3 p-8">
        {back}
        <p className="text-[13px] text-fg-subtle">
          Loading world <span className="num">{world}</span>…
        </p>
      </section>
    )
  }

  const info = worldQuery.data

  if (worldQuery.isError || info === undefined) {
    return (
      <section className="card flex h-full min-h-0 flex-col items-start gap-3 p-8">
        {back}
        <p className="text-[13px] text-danger">
          Failed to load world <span className="num">{world}</span>: {errorMessage(worldQuery.error)}
        </p>
        <Button variant="outline" size="xs" onClick={() => void worldQuery.refetch()}>
          Retry
        </Button>
      </section>
    )
  }

  return (
    <div className="flex h-full min-h-0 w-full flex-col gap-3">
      <header className="chrome flex shrink-0 flex-wrap items-center gap-x-3 gap-y-2 px-3.5 py-3">
        {back}
        <span className="h-4 w-px shrink-0 bg-border-strong lg:hidden" aria-hidden />
        <span className="num truncate text-[15px] font-semibold tracking-[-0.01em] text-fg">
          {info.world_id}
        </span>
        <WorldBadge frozen={info.frozen} />
        <span className="chip num text-[12px]">
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
          <TabsList className="h-8">
            <TabsTrigger value="spacetime" className="h-7 px-3.5 text-[14px]">
              Spacetimes{" "}
              <span className="num text-[12px] text-fg-subtle">{info.spacetimes.length}</span>
            </TabsTrigger>
            <TabsTrigger value="household" className="h-7 px-3.5 text-[14px]">
              Households <span className="num text-[12px] text-fg-subtle">{info.houses.length}</span>
            </TabsTrigger>
          </TabsList>
          <span className="label-micro">Spacetimes read the households; they never change them.</span>
        </div>

        <TabsContent value="spacetime" className="mt-0 flex min-h-0 flex-1 flex-col">
          <section className="card flex min-h-0 flex-1 flex-col overflow-hidden">
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
