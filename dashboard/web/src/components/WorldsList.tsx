import { useState } from "react"

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

const FIELD_CLASS =
  "h-8 rounded-md border-border-strong bg-surface-2 px-2.5 text-[12px] text-fg focus-visible:border-brand"

function WorldCard({ info, onOpen }: { info: WorldInfo; onOpen: () => void }) {
  const remove = useDeleteWorld()
  const [pendingDelete, setPendingDelete] = useState(false)

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-lg border border-border bg-surface transition-colors hover:border-border-strong">
      <button type="button" onClick={onOpen} className="flex min-w-0 flex-col gap-2 px-4 py-3 text-left">
        <span className="flex min-w-0 items-center gap-2">
          <span className="num truncate text-[12px] font-medium text-fg">{info.world_id}</span>
          <WorldBadge frozen={info.frozen} />
        </span>
        <span className="label-micro">
          {countLabel(info.districts.length, "block")} ·{" "}
          {countLabel(info.houses.length, "household")} ·{" "}
          {countLabel(info.spacetimes.length, "spacetime")}
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
                className="label-micro rounded-sm border border-danger/50 px-1.5 py-0.5 text-danger disabled:opacity-50"
              >
                Confirm delete
              </button>
              <button
                type="button"
                onClick={() => setPendingDelete(false)}
                className="label-micro rounded-sm border border-border-strong px-1.5 py-0.5 text-fg-muted"
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
              className="ml-auto text-fg-muted hover:text-danger"
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
    <div className="mx-auto flex h-full min-h-0 w-full max-w-5xl flex-col gap-3">
      <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-border bg-surface">
        <header className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-1 border-b border-border px-4 py-2.5">
          <span className="text-[13px] font-semibold text-fg">
            Worlds <span className="num text-[11px] text-fg-subtle">{worlds.length}</span>
          </span>
          <span className="label-micro">
            Households are a world&apos;s fixed physics — spacetimes are runs that read them.
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
        </header>

        <div className="flex shrink-0 flex-wrap items-end gap-2 border-b border-border px-3 py-2.5">
          <div className="flex min-w-[200px] flex-1 flex-col gap-1">
            <Label htmlFor="new-world-id" className="label-micro">
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

        <div className="min-h-0 flex-1 overflow-y-auto p-3">
          {worldsQuery.isPending ? (
            <p className="px-1 py-6 text-[11px] text-fg-subtle">Loading worlds…</p>
          ) : worldsQuery.isError ? (
            <div className="flex flex-col items-start gap-2 px-1 py-6">
              <p className="text-[11px] text-danger">
                Failed to load worlds: {errorMessage(worldsQuery.error)}
              </p>
              <Button variant="outline" size="xs" onClick={() => void worldsQuery.refetch()}>
                Retry
              </Button>
            </div>
          ) : worlds.length === 0 ? (
            <p className="px-1 py-6 text-[11px] text-fg-subtle">
              No worlds yet. Enter a world ID (or leave it blank) and click New blank world to create
              an empty shell — no LLM calls.
            </p>
          ) : (
            <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {worlds.map((info) => (
                <li key={info.world_id} className="min-w-0">
                  <WorldCard info={info} onOpen={() => openWorld(info.world_id)} />
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  )
}
