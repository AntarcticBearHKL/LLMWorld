import { useEffect } from "react"

import { ArrowLeft, Building2, CalendarDays, ChevronRight, DoorOpen, Home, MapPin } from "lucide-react"

import type { BlockSummary } from "@/api/types"
import { HouseFloorplan } from "@/components/HouseFloorplan"
import { MetricStrip } from "@/components/MetricStrip"
import { ObserveDetail, ObserveGrid, ObserveScene } from "@/components/ObserveViews"
import { TimeController } from "@/components/TimeController"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useDayReplay, useRunMeta } from "@/hooks/useDayData"
import { usePlayback } from "@/hooks/usePlayback"
import { useWorldDayBlocks } from "@/hooks/useSpacetimes"
import { errorMessage } from "@/lib/errors"
import { countLabel } from "@/lib/format"
import { formatKwh, formatWatts } from "@/lib/time"
import { useTimeStore } from "@/store/time"

const FIELD_CLASS =
  "h-8 w-[142px] rounded-md border-border-strong bg-surface-2 px-2.5 text-[12px] font-medium text-fg hover:bg-surface-3 focus-visible:border-brand"

function Frame({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-full min-h-0 flex-col gap-3">{children}</div>
  )
}

function Notice({
  title,
  body,
  action,
}: {
  title: string
  body: string
  action?: React.ReactNode
}) {
  return (
    <Frame>
      <section className="flex flex-1 flex-col items-start justify-center gap-2 rounded-lg border border-border bg-surface p-6">
        <h2 className="text-[13px] font-semibold text-fg">{title}</h2>
        <p className="max-w-[520px] text-[11px] leading-relaxed text-fg-muted">{body}</p>
        {action}
      </section>
    </Frame>
  )
}

function Crumb({
  label,
  onClick,
  current,
}: {
  label: string
  onClick: () => void
  current: boolean
}) {
  if (current) {
    return (
      <span aria-current="location" className="num truncate text-[12px] font-semibold text-fg">
        {label}
      </span>
    )
  }
  return (
    <button
      type="button"
      onClick={onClick}
      className="num truncate rounded-sm px-1 text-[12px] text-fg-muted transition-colors hover:bg-surface-3 hover:text-fg"
    >
      {label}
    </button>
  )
}

function BlockChip({ block, onOpen }: { block: BlockSummary; onOpen: () => void }) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="flex min-w-[186px] shrink-0 flex-col gap-1 rounded-md border border-border-strong bg-surface-2 px-3 py-2 text-left transition-colors hover:border-brand/45 hover:bg-surface-3"
    >
      <span className="num flex items-center gap-1.5 text-[12px] font-semibold text-fg">
        <MapPin className="size-3 shrink-0 text-fg-subtle" aria-hidden />
        {block.postcode}
      </span>
      <span className="label-micro">
        {countLabel(block.house_count, "household")} · {formatKwh(block.total_kwh)} kWh · peak{" "}
        {formatWatts(block.peak_watts)}
      </span>
    </button>
  )
}

function BlockStrip({ blocks, onOpen }: { blocks: BlockSummary[]; onOpen: (block: string) => void }) {
  return (
    <section className="shrink-0 rounded-lg border border-border bg-surface px-3 py-2.5">
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="text-[12px] font-semibold text-fg">
          Blocks <span className="num text-[11px] text-fg-subtle">{blocks.length}</span>
        </span>
        <span className="label-micro">Select a block to drill into its households</span>
      </div>
      <div className="mt-2 flex gap-2 overflow-x-auto pb-1">
        {blocks.map((item) => (
          <BlockChip key={item.postcode} block={item} onOpen={() => onOpen(item.postcode)} />
        ))}
      </div>
    </section>
  )
}

export function WatchView() {
  const world = useTimeStore((state) => state.world)
  const run = useTimeStore((state) => state.run)
  const date = useTimeStore((state) => state.date)
  const block = useTimeStore((state) => state.block)
  const house = useTimeStore((state) => state.house)
  const indoor = useTimeStore((state) => state.indoor)
  const policy = useTimeStore((state) => state.policy)
  const setSelection = useTimeStore((state) => state.setSelection)
  const setView = useTimeStore((state) => state.setView)
  const setBlock = useTimeStore((state) => state.setBlock)
  const setHouse = useTimeStore((state) => state.setHouse)
  const setIndoor = useTimeStore((state) => state.setIndoor)

  usePlayback()

  const metaQuery = useRunMeta(run)
  const meta = metaQuery.data
  const dates = meta?.dates ?? []
  const blocksQuery = useWorldDayBlocks(world, run, date, policy, true)
  const replayQuery = useDayReplay()

  useEffect(() => {
    if (meta === undefined) return
    if (!meta.dates.includes(date)) setSelection({ date: meta.dates[0] ?? "" })
  }, [meta, date, setSelection])

  const clearTo = (level: "world" | "block" | "house") => {
    if (level === "world") {
      setBlock("")
      setHouse("")
      setIndoor(false)
      return
    }
    if (level === "block") {
      setHouse("")
      setIndoor(false)
      return
    }
    setIndoor(false)
  }

  const backToWorldDetail = (
    <Button variant="ghost" size="xs" onClick={() => setView(world.length > 0 ? "world" : "worlds")}>
      <ArrowLeft />
      {world.length > 0 ? "World" : "Worlds"}
    </Button>
  )

  if (world.length === 0 || run.length === 0) {
    return (
      <Notice
        title="No spacetime selected"
        body="Open a world, then pick one of its spacetimes to replay a simulated day. Blocks, households and rooms all live under that spacetime."
        action={backToWorldDetail}
      />
    )
  }

  if (metaQuery.isPending) {
    return (
      <Notice
        title="Loading spacetime…"
        body={`Reading days and households for ${run}.`}
        action={backToWorldDetail}
      />
    )
  }

  if (metaQuery.isError) {
    return (
      <Notice
        title="Failed to load spacetime"
        body={`Could not read ${run}: ${errorMessage(metaQuery.error)}`}
        action={
          <span className="flex items-center gap-2">
            {backToWorldDetail}
            <Button variant="outline" size="xs" onClick={() => void metaQuery.refetch()}>
              Retry
            </Button>
          </span>
        }
      />
    )
  }

  if (dates.length === 0) {
    return (
      <Notice
        title="No simulated days"
        body={`Spacetime ${run} has no simulated days yet. Run a simulation from its world page, then come back.`}
        action={backToWorldDetail}
      />
    )
  }

  const layer: 1 | 2 | 3 | 4 = house.length > 0 ? (indoor ? 4 : 3) : block.length > 0 ? 2 : 1

  const crumb = (label: string, onClick: () => void, current: boolean) => (
    <Crumb key={label} label={label} onClick={onClick} current={current} />
  )

  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      <header className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-2 rounded-lg border border-border bg-surface px-3 py-2">
        {backToWorldDetail}
        <span className="h-4 w-px shrink-0 bg-border-strong" aria-hidden />

        <nav
          aria-label="Watch breadcrumb"
          className="flex min-w-0 flex-wrap items-center gap-0.5"
        >
          {crumb(`World ${world}`, () => clearTo("world"), layer === 1)}
          <ChevronRight className="size-3 shrink-0 text-fg-subtle" aria-hidden />
          {crumb(run, () => clearTo("world"), layer === 1)}
          <ChevronRight className="size-3 shrink-0 text-fg-subtle" aria-hidden />
          {crumb(date, () => clearTo("world"), layer === 1)}
          {block.length > 0 ? (
            <>
              <ChevronRight className="size-3 shrink-0 text-fg-subtle" aria-hidden />
              {crumb(block, () => clearTo("block"), layer === 2)}
            </>
          ) : null}
          {house.length > 0 ? (
            <>
              <ChevronRight className="size-3 shrink-0 text-fg-subtle" aria-hidden />
              {crumb(house, () => clearTo("house"), layer === 3)}
            </>
          ) : null}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <span className="label-micro flex items-center gap-1.5">
            <CalendarDays className="size-3" aria-hidden />
            Day
          </span>
          <Select
            value={date}
            onValueChange={(next) => setSelection({ date: next })}
            disabled={dates.length === 0}
          >
            <SelectTrigger className={FIELD_CLASS} aria-label="Select day">
              <SelectValue placeholder="Select day" />
            </SelectTrigger>
            <SelectContent>
              {dates.map((item) => (
                <SelectItem key={item} value={item}>
                  <span className="num">{item}</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <span className="label-latin rounded-sm border border-border-strong px-1.5 py-0.5">
            {policy}
          </span>
        </div>
      </header>

      <div className="min-h-0 flex-1">
        {layer === 1 ? (
          <Frame>
            <div className="min-h-0 flex-1">
              <ObserveScene
                onEnterHouse={(next) => {
                  setHouse(next)
                  setIndoor(false)
                }}
              />
            </div>

            {blocksQuery.isPending ? (
              <p className="shrink-0 px-1 text-[11px] text-fg-subtle">Loading blocks…</p>
            ) : blocksQuery.isError ? (
              <section className="flex shrink-0 flex-wrap items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2">
                <p className="text-[11px] text-danger">
                  Failed to load blocks: {errorMessage(blocksQuery.error)}
                </p>
                <Button variant="outline" size="xs" onClick={() => void blocksQuery.refetch()}>
                  Retry
                </Button>
              </section>
            ) : (blocksQuery.data?.blocks.length ?? 0) === 0 ? (
              <section className="shrink-0 rounded-lg border border-border bg-surface px-3 py-2">
                <p className="text-[11px] text-fg-subtle">
                  No blocks with households for {date}.
                </p>
              </section>
            ) : (
              <BlockStrip
                blocks={blocksQuery.data?.blocks ?? []}
                onOpen={(next) => {
                  setBlock(next)
                  setHouse("")
                  setIndoor(false)
                }}
              />
            )}
          </Frame>
        ) : null}

        {layer === 2 ? (
          blocksQuery.isPending ? (
            <Notice title="Loading block…" body={`Reading households of block ${block} on ${date}.`} />
          ) : blocksQuery.isError ? (
            <Notice
              title="Failed to load block"
              body={`Could not read block ${block}: ${errorMessage(blocksQuery.error)}`}
              action={
                <Button variant="outline" size="xs" onClick={() => void blocksQuery.refetch()}>
                  Retry
                </Button>
              }
            />
          ) : (
            (() => {
              const info = blocksQuery.data?.blocks.find((item) => item.postcode === block)
              if (info === undefined) {
                return (
                  <Notice
                    title="Empty block"
                    body={`Block ${block} has no households in this spacetime on ${date}.`}
                    action={
                      <Button variant="outline" size="xs" onClick={() => clearTo("world")}>
                        All blocks
                      </Button>
                    }
                  />
                )
              }
              return (
                <Frame>
                  <header className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-1 rounded-lg border border-border bg-surface px-3 py-2">
                    <Button variant="ghost" size="xs" onClick={() => clearTo("world")}>
                      <ArrowLeft />
                      All blocks
                    </Button>
                    <span className="num text-[12px] font-semibold text-fg">{info.postcode}</span>
                    <span className="label-micro">
                      {countLabel(info.house_count, "household")} · {formatKwh(info.total_kwh)} kWh ·
                      peak {formatWatts(info.peak_watts)}
                    </span>
                    <span className="label-latin ml-auto">Select a household to open its day</span>
                  </header>
                  <div className="min-h-0 flex-1">
                    <ObserveGrid
                      houses={info.houses}
                      onOpen={(next) => {
                        setHouse(next)
                        setIndoor(false)
                      }}
                    />
                  </div>
                </Frame>
              )
            })()
          )
        ) : null}

        {layer === 3 ? (
          replayQuery.isError ? (
            <Notice
              title="No replay for this household"
              body={`Could not read ${house} on ${date}: ${errorMessage(replayQuery.error)}`}
              action={
                <span className="flex items-center gap-2">
                  <Button variant="outline" size="xs" onClick={() => void replayQuery.refetch()}>
                    Retry
                  </Button>
                  <Button variant="ghost" size="xs" onClick={() => clearTo("world")}>
                    {block.length > 0 ? "All blocks" : "World view"}
                  </Button>
                </span>
              }
            />
          ) : (
            <Frame>
              <header className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-2 rounded-lg border border-border bg-surface px-3 py-2">
                <span className="flex items-center gap-1.5 text-[12px] font-semibold text-fg">
                  <Home className="size-3.5" aria-hidden />
                  {house}
                </span>
                <span className="label-micro">
                  {block.length > 0 ? `Block ${block} · ` : ""}
                  {date}
                </span>
                <Button
                  size="sm"
                  className="ml-auto"
                  onClick={() => setIndoor(true)}
                  disabled={replayQuery.isPending}
                >
                  <DoorOpen />
                  Enter indoor
                </Button>
              </header>
              <div className="shrink-0">
                <MetricStrip replay={replayQuery.data} isPending={replayQuery.isPending} />
              </div>
              <div className="min-h-0 flex-1">
                <ObserveDetail />
              </div>
            </Frame>
          )
        ) : null}

        {layer === 4 ? (
          replayQuery.isError ? (
            <Notice
              title="No replay for this household"
              body={`Could not read ${house} on ${date}: ${errorMessage(replayQuery.error)}`}
              action={
                <span className="flex items-center gap-2">
                  <Button variant="outline" size="xs" onClick={() => void replayQuery.refetch()}>
                    Retry
                  </Button>
                  <Button variant="ghost" size="xs" onClick={() => setIndoor(false)}>
                    Back to house
                  </Button>
                </span>
              }
            />
          ) : (
            <Frame>
              <header className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-2 rounded-lg border border-border bg-surface px-3 py-2">
                <span className="flex items-center gap-1.5 text-[12px] font-semibold text-fg">
                  <Building2 className="size-3.5" aria-hidden />
                  Indoors · {house}
                </span>
                <span className="label-micro">{date}</span>
                <span className="label-latin ml-auto">
                  Rooms, occupants, appliances and live load follow the play bar
                </span>
                <Button variant="outline" size="sm" onClick={() => setIndoor(false)}>
                  <ArrowLeft />
                  Back to house
                </Button>
              </header>
              <div className="min-h-0 flex-1">
                <HouseFloorplan replay={replayQuery.data} className="h-full min-h-0" />
              </div>
            </Frame>
          )
        ) : null}
      </div>

      <footer className="glass shrink-0 rounded-lg border border-border px-3 py-2.5">
        <TimeController />
      </footer>
    </div>
  )
}
