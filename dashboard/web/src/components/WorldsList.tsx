import { useState, type CSSProperties } from "react"

import { Clock3, Loader2, Plus, RefreshCw, Trash2 } from "lucide-react"

import type { WorldInfo } from "@/api/types"
import { CloneWorldButton } from "@/components/CloneWorldButton"
import { WorldBadge } from "@/components/primitives/WorldBadge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useCreateWorld, useDeleteWorld, useWorlds } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { countLabel, formatMtime } from "@/lib/format"
import { cn } from "@/lib/utils"
import { randomWorldId } from "@/lib/world"
import { useTimeStore } from "@/store/time"

const FIELD_CLASS = "h-8 px-2.5 text-[14px]"

function WorldRow({
  info,
  selected,
  onSelect,
}: {
  info: WorldInfo
  selected: boolean
  onSelect: () => void
}) {
  const remove = useDeleteWorld()
  const [pendingDelete, setPendingDelete] = useState(false)

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
          "flex w-full min-w-0 flex-col gap-2 px-3.5 py-3 text-left transition-colors",
          selected ? "bg-item-selected" : "hover:bg-item-hover",
        )}
      >
        <span className="flex min-w-0 items-center gap-2">
          <span className="num truncate text-[14px] font-semibold tracking-[-0.01em] text-fg">
            {info.world_id}
          </span>
          <WorldBadge frozen={info.frozen} />
        </span>

        <span className="chip max-w-full">
          <span className="num truncate text-[12px]">
            {countLabel(info.districts.length, "block")} ·{" "}
            {countLabel(info.houses.length, "household")} ·{" "}
            {countLabel(info.spacetimes.length, "spacetime")}
          </span>
        </span>

        <span className="label-micro flex items-center gap-1.5">
          <Clock3 className="size-3" aria-hidden />
          Last activity {formatMtime(info.latest_mtime)}
        </span>
      </button>

      <div className="flex flex-col gap-1.5 border-t border-border px-2.5 py-2">
        {pendingDelete ? (
          <>
            <p className="text-[12px] text-energy">
              Delete moves <span className="num">{info.world_id}</span> to output/_trash/ (recoverable).
            </p>
            <span className="flex flex-wrap items-center gap-1.5">
              <button
                type="button"
                onClick={() =>
                  remove.mutate(info.world_id, { onSuccess: () => setPendingDelete(false) })
                }
                disabled={remove.isPending}
                title="Moves to output/_trash/ (recoverable)"
                className="label-micro rounded-full border border-danger/50 px-2 py-0.5 text-danger transition-colors hover:bg-danger/10 disabled:opacity-50"
              >
                Confirm delete
              </button>
              <button
                type="button"
                onClick={() => setPendingDelete(false)}
                className="label-micro rounded-full border border-border-strong px-2 py-0.5 text-fg-muted transition-colors hover:bg-item-hover"
              >
                Cancel
              </button>
            </span>
          </>
        ) : (
          <span className="flex flex-wrap items-center gap-1.5">
            <CloneWorldButton world={info.world_id} />
            <Button
              variant="ghost"
              size="xs"
              className="ml-auto hover:text-danger"
              title="Moves to output/_trash/ (recoverable)"
              onClick={() => setPendingDelete(true)}
            >
              <Trash2 />
              Delete
            </Button>
          </span>
        )}
        {remove.isError ? (
          <p className="text-[12px] text-danger">Delete failed: {errorMessage(remove.error)}</p>
        ) : null}
      </div>
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

  const openWorld = (worldId: string) => setWorld(worldId)

  const onCreate = () => {
    const worldId =
      draft.trim().length > 0
        ? draft.trim()
        : randomWorldId(worlds.map((item) => item.world_id))
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
          Households are a world&apos;s fixed physics — spacetimes are runs that read them.
        </p>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="new-world-id" className="label-micro text-fg-muted">
            World ID (blank = auto-generate)
          </Label>
          <Input
            id="new-world-id"
            value={draft}
            placeholder="world_fish"
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
                />
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
