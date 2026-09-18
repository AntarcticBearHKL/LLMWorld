import { useEffect, useState } from "react"

import { Clock3, Loader2, Plus, RefreshCw, Trash2 } from "lucide-react"

import type { WorldInfo } from "@/api/types"
import { CloneWorldButton } from "@/components/CloneWorldButton"
import { NewWorldSheet } from "@/components/NewWorldSheet"
import { useScreenChrome } from "@/components/primitives/ScreenChrome"
import { WorldBadge } from "@/components/primitives/WorldBadge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useDeleteWorld, useWorlds } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { formatMtime } from "@/lib/format"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

const HEAD_CLASS = "h-8 px-2.5 t-micro text-fg-faint"

const HEAD_NUM_CLASS = cn(HEAD_CLASS, "text-right")

const CELL_NUM_CLASS = "num text-right t-body"

function WorldRow({
  info,
  selected,
  onOpen,
  onDeleted,
}: {
  info: WorldInfo
  selected: boolean
  onOpen: () => void
  onDeleted: () => void
}) {
  const remove = useDeleteWorld()
  const [armed, setArmed] = useState(false)

  useEffect(() => {
    if (!armed) return
    const timer = window.setTimeout(() => setArmed(false), 6000)
    return () => window.clearTimeout(timer)
  }, [armed])

  return (
    <>
      <TableRow
        aria-selected={selected}
        tabIndex={0}
        onClick={onOpen}
        onKeyDown={(event) => {
          if (event.target !== event.currentTarget) return
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault()
            onOpen()
          }
        }}
        className={cn(
          "h-10 cursor-pointer border-b border-border/60 hover:bg-item-hover",
          selected && "bg-item-selected",
        )}
      >
        <TableCell className="align-middle">
          <div className="flex min-w-0 flex-col gap-0.5">
            <div className="flex min-w-0 items-center gap-2">
              <button
                type="button"
                onClick={onOpen}
                title={info.world_id}
                className="num t-title min-w-0 truncate text-left"
              >
                {info.world_id}
              </button>
              <WorldBadge frozen={info.frozen} className="shrink-0" />
            </div>
            <span className="t-caption flex min-w-0 items-center gap-1">
              <Clock3 className="size-3 shrink-0" aria-hidden />
              <span className="truncate" title={formatMtime(info.latest_mtime)}>
                {formatMtime(info.latest_mtime)}
              </span>
            </span>
          </div>
        </TableCell>

        <TableCell className={CELL_NUM_CLASS}>{info.districts.length}</TableCell>
        <TableCell className={CELL_NUM_CLASS}>{info.houses.length}</TableCell>
        <TableCell className={CELL_NUM_CLASS}>{info.spacetimes.length}</TableCell>

        <TableCell
          className="text-right whitespace-nowrap"
          onClick={(event) => event.stopPropagation()}
        >
          <span className="inline-flex items-center gap-1">
            <CloneWorldButton world={info.world_id} label="Clone world" />
            <Button
              variant="ghost"
              size={armed ? "xs" : "icon-xs"}
              disabled={remove.isPending}
              aria-label="Delete world"
              title={
                armed
                  ? "Click again to delete"
                  : "Delete this world (moves to output/_trash/, recoverable)"
              }
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => {
                if (!armed) {
                  setArmed(true)
                  return
                }
                remove.mutate(info.world_id, { onSuccess: onDeleted })
              }}
              className={cn(armed && "bg-danger/10 text-danger hover:bg-danger/15 hover:text-danger")}
            >
              {remove.isPending ? <Loader2 className="animate-spin" /> : <Trash2 />}
              {armed ? "Confirm delete" : null}
            </Button>
          </span>
        </TableCell>
      </TableRow>

      {remove.isError ? (
        <TableRow className="border-b border-border/60 hover:bg-transparent">
          <TableCell colSpan={5} className="px-2.5 py-1.5 t-body text-danger">
            Delete failed: {errorMessage(remove.error)}
          </TableCell>
        </TableRow>
      ) : null}
    </>
  )
}

export function WorldsList() {
  const worldsQuery = useWorlds()
  const world = useTimeStore((state) => state.world)
  const setWorld = useTimeStore((state) => state.setWorld)
  const setView = useTimeStore((state) => state.setView)
  const [createOpen, setCreateOpen] = useState(false)
  const setChrome = useScreenChrome()

  const worlds = worldsQuery.data ?? []

  const openWorld = (worldId: string) => {
    setWorld(worldId)
    setView("world")
  }

  const refetch = worldsQuery.refetch

  useEffect(
    () =>
      setChrome({
        title: (
          <>
            Worlds <span className="num t-micro">{worlds.length}</span>
          </>
        ),
        actions: (
          <>
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="Refresh worlds"
              onClick={() => void refetch()}
            >
              <RefreshCw />
            </Button>
            <Button size="sm" onClick={() => setCreateOpen(true)}>
              <Plus />
              New world
            </Button>
          </>
        ),
      }),
    [refetch, setChrome, worlds.length],
  )

  return (
    <section className="card flex w-full flex-col overflow-hidden border-t border-border first:border-t-0">
      <Table className="w-full">
        <TableHeader>
          <TableRow className="border-b border-border hover:bg-transparent">
            <TableHead className={HEAD_CLASS}>World</TableHead>
            <TableHead className={HEAD_NUM_CLASS}>Districts</TableHead>
            <TableHead className={HEAD_NUM_CLASS}>Households</TableHead>
            <TableHead className={HEAD_NUM_CLASS}>Scenarios</TableHead>
            <TableHead className={HEAD_CLASS}>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {worldsQuery.isPending ? (
            <TableRow className="hover:bg-transparent">
              <TableCell colSpan={5} className="p-6 text-center t-body text-fg-subtle">
                Loading worlds…
              </TableCell>
            </TableRow>
          ) : worldsQuery.isError ? (
            <TableRow className="hover:bg-transparent">
              <TableCell colSpan={5} className="p-6 text-center t-body text-fg-subtle">
                <span className="flex flex-col items-center gap-2">
                  <span className="t-body text-danger">
                    Failed to load worlds: {errorMessage(worldsQuery.error)}
                  </span>
                  <Button variant="outline" size="xs" onClick={() => void worldsQuery.refetch()}>
                    Retry
                  </Button>
                </span>
              </TableCell>
            </TableRow>
          ) : worlds.length === 0 ? (
            <TableRow className="hover:bg-transparent">
              <TableCell colSpan={5} className="p-6 text-center t-body text-fg-subtle">
                <span className="flex flex-col items-center gap-1.5">
                  <span className="t-body text-fg">No worlds yet</span>
                  <span className="t-caption leading-relaxed text-fg-muted">
                    Click New world to create an empty shell — no LLM calls.
                  </span>
                </span>
              </TableCell>
            </TableRow>
          ) : (
            worlds.map((info) => (
              <WorldRow
                key={info.world_id}
                info={info}
                selected={world === info.world_id}
                onOpen={() => openWorld(info.world_id)}
                onDeleted={() => {
                  if (world === info.world_id) setWorld("")
                }}
              />
            ))
          )}
        </TableBody>
      </Table>

      <NewWorldSheet
        worldIds={worlds.map((info) => info.world_id)}
        open={createOpen}
        onOpenChange={setCreateOpen}
        onCreated={openWorld}
      />
    </section>
  )
}
