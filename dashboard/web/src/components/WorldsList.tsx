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

const FIELD_CLASS = "h-8 px-2.5 text-[12px]"

function WorldCard({ info, onOpen }: { info: WorldInfo; onOpen: () => void }) {
  const remove = useDeleteWorld()
  const [pendingDelete, setPendingDelete] = useState(false)

  return (
    <article className="card card-lift flex h-full flex-col overflow-hidden hover:-translate-y-0.5 hover:border-border-strong hover:shadow-2">
      <button
        type="button"
        onClick={onOpen}
        className="flex min-w-0 flex-col gap-2.5 px-4 py-3.5 text-left"
      >
        <span className="flex min-w-0 items-center gap-2">
          <span className="num truncate text-[14px] font-semibold tracking-[-0.01em] text-fg">
            {info.world_id}
          </span>
          <WorldBadge frozen={info.frozen} />
        </span>

        <span className="chip max-w-full">
          <span className="num truncate text-[10px]">
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

      <div className="mt-auto flex flex-col gap-1.5 border-t border-border px-3 py-2">
        {pendingDelete ? (
          <>
            <p className="text-[10px] text-energy">
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
          <p className="text-[10px] text-danger">Delete failed: {errorMessage(remove.error)}</p>
        ) : null}
      </div>
    </article>
  )
}

export function WorldsList() {
  const worldsQuery = useWorlds()
  const create = useCreateWorld()
  const setWorld = useTimeStore((state) => state.setWorld)
  const setView = useTimeStore((state) => state.setView)
  const [draft, setDraft] = useState("")

  const worlds = worldsQuery.data ?? []

  const openWorld = (world: string) => {
    setWorld(world)
    setView("world")
  }

  const onCreate = () => {
    const worldId = draft.trim().length > 0 ? draft.trim() : randomWorldId()
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
    <div className="mx-auto flex h-full min-h-0 w-full max-w-6xl flex-col gap-3">
      <section className="chrome flex shrink-0 flex-col gap-3 px-4 py-3.5">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="text-[15px] font-bold tracking-[-0.01em] text-fg">
            Worlds <span className="num text-[12px] font-medium text-fg-muted">{worlds.length}</span>
          </span>
          <span className="label-micro text-fg-muted">
            Households are a world&apos;s fixed physics — spacetimes are runs that read them.
          </span>
          <Button
            variant="outline"
            size="icon-sm"
            className="ml-auto"
            aria-label="Refresh worlds"
            onClick={() => void worldsQuery.refetch()}
          >
            <RefreshCw />
          </Button>
        </div>

        <div className="flex flex-wrap items-end gap-2">
          <div className="flex min-w-[200px] flex-1 flex-col gap-1">
            <Label htmlFor="new-world-id" className="label-micro text-fg-muted">
              World ID (blank = auto-generate)
            </Label>
            <Input
              id="new-world-id"
              value={draft}
              placeholder="world_9f3a1c"
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !create.isPending) onCreate()
              }}
              className={cn(FIELD_CLASS, "num")}
            />
          </div>
          <Button size="sm" onClick={onCreate} disabled={create.isPending}>
            {create.isPending ? <Loader2 className="animate-spin" /> : <Plus />}
            New blank world
          </Button>
          {create.isError ? (
            <p className="w-full text-[10px] text-danger">Create failed: {errorMessage(create.error)}</p>
          ) : null}
        </div>
      </section>

      <div className="min-h-0 flex-1 overflow-y-auto pb-1">
        {worldsQuery.isPending ? (
          <p className="px-1 py-6 text-[11px] text-fg-subtle">Loading worlds…</p>
        ) : worldsQuery.isError ? (
          <div className="card flex flex-col items-start gap-2 px-4 py-6">
            <p className="text-[11px] text-danger">
              Failed to load worlds: {errorMessage(worldsQuery.error)}
            </p>
            <Button variant="outline" size="xs" onClick={() => void worldsQuery.refetch()}>
              Retry
            </Button>
          </div>
        ) : worlds.length === 0 ? (
          <div className="card px-4 py-8 text-center">
            <p className="text-[13px] font-semibold text-fg">No worlds yet</p>
            <p className="mx-auto mt-1 max-w-[420px] text-[11px] leading-relaxed text-fg-muted">
              Enter a world ID (or leave it blank) and click New blank world to create an empty shell
              — no LLM calls.
            </p>
          </div>
        ) : (
          <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {worlds.map((info, index) => (
              <li
                key={info.world_id}
                className="enter min-w-0"
                style={{ "--enter-index": index } as CSSProperties}
              >
                <WorldCard info={info} onOpen={() => openWorld(info.world_id)} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
