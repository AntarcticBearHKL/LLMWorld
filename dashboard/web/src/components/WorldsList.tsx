import { useEffect, useMemo, useState } from "react"

import { Clock3, Loader2, Plus, RefreshCw, Trash2 } from "lucide-react"

import type { WorldInfo } from "@/api/types"
import { CloneWorldButton } from "@/components/CloneWorldButton"
import { WorldBadge } from "@/components/primitives/WorldBadge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useCreateWorld, useDeleteWorld, useWorlds } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { formatMtime } from "@/lib/format"
import { cn } from "@/lib/utils"
import { randomWorldId } from "@/lib/world"
import { useTimeStore } from "@/store/time"

const FIELD_CLASS = "h-8 px-2.5 text-[14px]"

const HEAD_CLASS = "h-8 px-2.5 text-[11px] font-semibold uppercase tracking-[0.04em] text-fg-muted"

const HEAD_NUM_CLASS = cn(HEAD_CLASS, "text-right")

const CELL_NUM_CLASS = "num text-right tabular-nums text-fg-muted"

function WorldRow({
  info,
  selected,
  onSelect,
  onDeleted,
}: {
  info: WorldInfo
  selected: boolean
  onSelect: () => void
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
        onClick={onSelect}
        onKeyDown={(event) => {
          if (event.target !== event.currentTarget) return
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault()
            onSelect()
          }
        }}
        className={cn(
          "h-10 cursor-pointer border-b border-border/60 hover:bg-item-hover",
          selected && "bg-item-selected",
        )}
      >
        <TableCell className="max-w-[180px] align-middle">
          <div className="flex max-w-[160px] min-w-0 flex-col gap-0.5">
            <div className="flex min-w-0 items-center gap-2">
              <button
                type="button"
                onClick={onSelect}
                title={info.world_id}
                className="num min-w-0 truncate text-left text-[13px] font-semibold tracking-[-0.01em] text-fg"
              >
                {info.world_id}
              </button>
              <WorldBadge frozen={info.frozen} className="shrink-0" />
            </div>
            <span className="flex min-w-0 items-center gap-1 text-[11px] text-fg-subtle">
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
            <CloneWorldButton world={info.world_id} label="" />
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
          <TableCell colSpan={5} className="px-2.5 py-1.5 text-[12px] text-danger">
            Delete failed: {errorMessage(remove.error)}
          </TableCell>
        </TableRow>
      ) : null}
    </>
  )
}

export function WorldsList() {
  const worldsQuery = useWorlds()
  const create = useCreateWorld()
  const world = useTimeStore((state) => state.world)
  const setWorld = useTimeStore((state) => state.setWorld)
  const [draft, setDraft] = useState("")

  const worlds = worldsQuery.data ?? []
  const takenKey = worlds.map((item) => item.world_id).join("|")
  const suggested = useMemo(
    () => randomWorldId(takenKey === "" ? [] : takenKey.split("|")),
    [takenKey],
  )

  const openWorld = (worldId: string) => setWorld(worldId)

  const onCreate = () => {
    const worldId = draft.trim().length > 0 ? draft.trim() : suggested
    create.mutate(
      { world_id: worldId },
      {
        onSuccess: (result) => {
          setDraft("")
          openWorld(result.world_id)
        },
      },
    )
  }

  return (
    <section className="card flex h-full min-h-0 w-full flex-col overflow-hidden">
      <header className="flex shrink-0 flex-col gap-2.5 border-b border-border px-3.5 py-3">
        <div className="flex items-center gap-2">
          <span className="text-[15px] font-bold tracking-[-0.01em] text-fg">
            Worlds <span className="num text-[14px] font-medium text-fg-muted">{worlds.length}</span>
          </span>
          <Button
            variant="ghost"
            size="icon-sm"
            className="ml-auto"
            aria-label="Refresh worlds"
            onClick={() => void worldsQuery.refetch()}
          >
            <RefreshCw />
          </Button>
        </div>

        <p className="label-micro">
          Households are a world&apos;s fixed physics — scenarios replay them under their own policy and dates.
        </p>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="new-world-id" className="label-micro text-fg-muted">
            World ID (blank = use the suggested id)
          </Label>
          <Input
            id="new-world-id"
            value={draft}
            placeholder={suggested}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !create.isPending) onCreate()
            }}
            className={cn(FIELD_CLASS, "num")}
          />
          <Button size="sm" className="w-full" onClick={onCreate} disabled={create.isPending}>
            {create.isPending ? <Loader2 className="animate-spin" /> : <Plus />}
            New blank world
          </Button>
        </div>

        {create.isError ? (
          <p className="text-[12px] text-danger">Create failed: {errorMessage(create.error)}</p>
        ) : null}
      </header>

      <div className="min-h-0 flex-1 overflow-auto">
        <Table className="w-full text-[13px]">
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
                <TableCell colSpan={5} className="p-6 text-center text-[13px] text-fg-subtle">
                  Loading worlds…
                </TableCell>
              </TableRow>
            ) : worldsQuery.isError ? (
              <TableRow className="hover:bg-transparent">
                <TableCell colSpan={5} className="p-6 text-center text-[13px] text-fg-subtle">
                  <span className="flex flex-col items-center gap-2">
                    <span className="text-[13px] text-danger">
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
                <TableCell colSpan={5} className="p-6 text-center text-[13px] text-fg-subtle">
                  <span className="flex flex-col items-center gap-1.5">
                    <span className="text-[15px] font-semibold text-fg">No worlds yet</span>
                    <span className="text-[13px] leading-relaxed text-fg-muted">
                      Enter a world ID (or leave it blank) and click New blank world to create an
                      empty shell — no LLM calls.
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
                  onSelect={() => openWorld(info.world_id)}
                  onDeleted={() => {
                    if (world === info.world_id) setWorld("")
                  }}
                />
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </section>
  )
}
