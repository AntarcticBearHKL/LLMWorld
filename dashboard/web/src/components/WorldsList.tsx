import { useEffect, useMemo, useState, type CSSProperties } from "react"

import { Clock3, Loader2, Plus, RefreshCw, Trash2 } from "lucide-react"

import type { WorldInfo } from "@/api/types"
import { CloneWorldButton } from "@/components/CloneWorldButton"
import { WorldBadge } from "@/components/primitives/WorldBadge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useCreateWorld, useDeleteWorld, useWorlds } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { formatMtime } from "@/lib/format"
import { cn } from "@/lib/utils"
import { randomWorldId } from "@/lib/world"
import { useTimeStore } from "@/store/time"

const FIELD_CLASS = "h-8 px-2.5 text-[14px]"

function Stat({ value, word }: { value: number; word: string }) {
  return (
    <span className="whitespace-nowrap">
      <span className="num font-semibold text-fg-muted">{value}</span>{" "}
      {value === 1 ? word : `${word}s`}
    </span>
  )
}

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
    <article
      className={cn(
        "card card-lift overflow-hidden",
        selected ? "border-brand-ring" : "hover:border-border-strong",
      )}
    >
      <button
        type="button"
        onClick={onSelect}
        aria-current={selected ? "true" : undefined}
        className={cn(
          "flex w-full min-w-0 flex-col gap-1.5 px-3.5 py-2.5 text-left transition-colors",
          selected ? "bg-item-selected" : "hover:bg-item-hover",
        )}
      >
        <span className="flex min-w-0 items-center gap-2">
          <span className="num truncate text-[15px] font-semibold tracking-[-0.01em] text-fg">
            {info.world_id}
          </span>
          <WorldBadge frozen={info.frozen} />
          <span className="label-micro ml-auto flex shrink-0 items-center gap-1 whitespace-nowrap">
            <Clock3 className="size-3" aria-hidden />
            {formatMtime(info.latest_mtime)}
          </span>
        </span>

        <span className="flex flex-wrap items-center gap-x-1.5 gap-y-0.5 text-[12px] text-fg-subtle">
          <Stat value={info.districts.length} word="block" />
          <span aria-hidden>·</span>
          <Stat value={info.houses.length} word="household" />
          <span aria-hidden>·</span>
          <Stat value={info.spacetimes.length} word="scenario" />
        </span>
      </button>

      <div className="flex items-center justify-between gap-2 border-t border-border/60 px-2 py-1.5">
        <CloneWorldButton world={info.world_id} />
        <Button
          variant="ghost"
          size="xs"
          disabled={remove.isPending}
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
          {armed ? "Confirm delete" : "Delete"}
        </Button>
      </div>

      {remove.isError ? (
        <p className="border-t border-border/60 px-3.5 py-1.5 text-[12px] text-danger">
          Delete failed: {errorMessage(remove.error)}
        </p>
      ) : null}
    </article>
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

      <div className="min-h-0 flex-1 overflow-y-auto p-2.5">
        {worldsQuery.isPending ? (
          <p className="px-1 py-4 text-[13px] text-fg-subtle">Loading worlds…</p>
        ) : worldsQuery.isError ? (
          <div className="flex flex-col items-start gap-2 px-1 py-4">
            <p className="text-[13px] text-danger">
              Failed to load worlds: {errorMessage(worldsQuery.error)}
            </p>
            <Button variant="outline" size="xs" onClick={() => void worldsQuery.refetch()}>
              Retry
            </Button>
          </div>
        ) : worlds.length === 0 ? (
          <div className="flex flex-col gap-1.5 px-1 py-4">
            <p className="text-[15px] font-semibold text-fg">No worlds yet</p>
            <p className="text-[13px] leading-relaxed text-fg-muted">
              Enter a world ID (or leave it blank) and click New blank world to create an empty shell
              — no LLM calls.
            </p>
          </div>
        ) : (
          <ul className="flex flex-col gap-2">
            {worlds.map((info, index) => (
              <li
                key={info.world_id}
                className="enter min-w-0"
                style={{ "--enter-index": index } as CSSProperties}
              >
                <WorldRow
                  info={info}
                  selected={world === info.world_id}
                  onSelect={() => openWorld(info.world_id)}
                  onDeleted={() => {
                    if (world === info.world_id) setWorld("")
                  }}
                />
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
