import { useEffect } from "react"

import { ArrowLeft } from "lucide-react"

import { SpacetimeList } from "@/components/SpacetimeList"
import { WorldHouseholds } from "@/components/WorldHouseholds"
import { useScreenChrome } from "@/components/primitives/ScreenChrome"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useWorld } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { useTimeStore, type WorldTab } from "@/store/time"

const isWorldTab = (value: string): value is WorldTab =>
  value === "scenarios" || value === "household"

export function WorldDetail() {
  const world = useTimeStore((state) => state.world)
  const tab = useTimeStore((state) => state.tab)
  const setTab = useTimeStore((state) => state.setTab)
  const setWorld = useTimeStore((state) => state.setWorld)
  const setView = useTimeStore((state) => state.setView)
  const worldQuery = useWorld(world)
  const setChrome = useScreenChrome()
  const info = worldQuery.data

  useEffect(() => {
    if (world.length === 0) setView("worlds")
  }, [world, setView])

  useEffect(() => {
    if (info === undefined) return
    return setChrome({
      title: (
        <Button
          variant="ghost"
          size="xs"
          onClick={() => {
            setWorld("")
            setView("worlds")
          }}
        >
          <ArrowLeft />
          All worlds
        </Button>
      ),
    })
  }, [info, setChrome, setView, setWorld])

  const back = (
    <Button
      variant="ghost"
      size="xs"
      onClick={() => {
        setWorld("")
        setView("worlds")
      }}
    >
      <ArrowLeft />
      All worlds
    </Button>
  )

  if (world.length === 0) return null

  if (worldQuery.isPending) {
    return (
      <section className="card flex h-full min-h-0 flex-col items-start gap-3 p-8">
        {back}
        <p className="t-caption">
          Loading world <span className="num">{world}</span>…
        </p>
      </section>
    )
  }

  if (worldQuery.isError || info === undefined) {
    return (
      <section className="card flex h-full min-h-0 flex-col items-start gap-3 p-8">
        {back}
        <p className="t-caption text-danger">
          Failed to load world <span className="num">{world}</span>: {errorMessage(worldQuery.error)}
        </p>
        <Button variant="outline" size="xs" onClick={() => void worldQuery.refetch()}>
          Retry
        </Button>
      </section>
    )
  }

  return (
    <div className="flex h-full min-h-0 w-full flex-col gap-0">
      <Tabs
        value={tab}
        onValueChange={(value) => {
          if (isWorldTab(value)) setTab(value)
        }}
        className="flex min-h-0 flex-1 flex-col"
      >
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          <TabsList className="flex w-full items-stretch justify-start gap-6 rounded-none border-x-0 border-t-0 border-b border-border bg-transparent p-0">
            <TabsTrigger
              value="household"
              className="relative -mb-px h-auto flex-none items-center justify-start gap-1.5 rounded-none border-x-0 border-t-0 border-b-2 border-transparent bg-transparent px-0 py-0 t-body text-fg-muted hover:bg-transparent hover:text-fg data-[state=active]:border-fg data-[state=active]:bg-transparent data-[state=active]:text-fg data-[state=active]:shadow-none data-[state=active]:t-title"
            >
              Households <span className="num t-caption">{info.houses.length}</span>
            </TabsTrigger>
            <TabsTrigger
              value="scenarios"
              className="relative -mb-px h-auto flex-none items-center justify-start gap-1.5 rounded-none border-x-0 border-t-0 border-b-2 border-transparent bg-transparent px-0 py-0 t-body text-fg-muted hover:bg-transparent hover:text-fg data-[state=active]:border-fg data-[state=active]:bg-transparent data-[state=active]:text-fg data-[state=active]:shadow-none data-[state=active]:t-title"
            >
              Scenarios{" "}
              <span className="num t-caption">{info.spacetimes.length}</span>
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="scenarios" className="mt-0 flex min-h-0 flex-1 flex-col">
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
