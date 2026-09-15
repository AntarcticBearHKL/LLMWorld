import { useState } from "react"

import { CalendarClock, CheckCircle2, Plus, RefreshCw } from "lucide-react"

import type { Spacetime } from "@/api/types"
import { SpacetimeWizard } from "@/components/SpacetimeWizard"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useDeleteSpacetime, useSpacetimes } from "@/hooks/useSpacetimes"
import { errorMessage } from "@/lib/errors"
import { countLabel } from "@/lib/format"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

const statusClass = (status: string): string => {
  if (status === "failed" || status === "error") return "border-danger/40 bg-danger/10 text-danger"
  if (status === "queued" || status === "running") {
    return "border-energy/40 bg-energy-soft text-energy"
  }
  if (status === "done" || status === "complete" || status === "completed") {
    return "border-success/40 bg-success/10 text-success"
  }
  return "border-border-strong bg-surface-2 text-fg-muted"
}

function SpacetimeRow({
  world,
  item,
  highlighted,
  onOpen,
}: {
  world: string
  item: Spacetime
  highlighted: boolean
  onOpen: () => void
}) {
  const remove = useDeleteSpacetime(world)
  const [pendingDelete, setPendingDelete] = useState(false)

  return (
    <li
      className={cn(
        "card card-lift flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center",
        highlighted
          ? "border-brand-ring bg-brand-soft"
          : "hover:border-border-strong hover:shadow-2",
      )}
    >
      <button type="button" onClick={onOpen} className="flex min-w-0 flex-1 flex-col gap-1 text-left">
        <span className="flex min-w-0 flex-wrap items-center gap-2">
          <span className="num truncate text-[13px] font-semibold tracking-[-0.01em] text-fg">
            {item.name}
          </span>
          <Badge variant="outline" className={cn("label-latin", statusClass(item.status))}>
            {item.status}
          </Badge>
          <span className="label-micro">
            {item.days} {item.days === 1 ? "day" : "days"} · policy {item.policy ?? "baseline"}
          </span>
        </span>
        <span className="label-micro">
          {countLabel(item.events.length, "event")} · {countLabel(item.notices.length, "notice")} ·{" "}
          {countLabel(item.date_count, "date")} · {countLabel(item.house_count, "household")}
        </span>
        <span className="label-micro flex items-center gap-1.5">
          <CalendarClock className="size-3" aria-hidden />
          Start {item.start_date ?? "—"} · created {item.created_at ?? "—"}
        </span>
      </button>

      <span className="flex shrink-0 flex-wrap items-center gap-1.5">
        {pendingDelete ? (
          <>
            <span className="text-[10px] text-energy">Moves to output/_trash/ (recoverable).</span>
            <button
              type="button"
              onClick={() => remove.mutate(item.name, { onSuccess: () => setPendingDelete(false) })}
              disabled={remove.isPending}
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
          </>
        ) : (
          <>
            <Button variant="outline" size="xs" onClick={onOpen}>
              Open in watch
            </Button>
            <Button
              variant="ghost"
              size="xs"
              className="text-fg-muted hover:text-danger"
              title="Moves to output/_trash/ (recoverable)"
              onClick={() => setPendingDelete(true)}
            >
              Delete
            </Button>
          </>
        )}
        {remove.isError ? (
          <span className="text-[10px] text-danger">{errorMessage(remove.error)}</span>
        ) : null}
      </span>
    </li>
  )
}

export function SpacetimeList({ world }: { world: string }) {
  const query = useSpacetimes(world)
  const setSelection = useTimeStore((state) => state.setSelection)
  const setView = useTimeStore((state) => state.setView)
  const [wizardOpen, setWizardOpen] = useState(false)
  const [created, setCreated] = useState<Spacetime | null>(null)

  const items = query.data ?? []

  const openWatch = (name: string) => {
    setSelection({ run: name, date: "", house: "" })
    setView("watch")
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-4 py-3">
        <span className="text-[14px] font-bold tracking-[-0.01em] text-fg">
          Spacetimes <span className="num text-[11px] font-medium text-fg-subtle">{items.length}</span>
        </span>
        <Button
          variant="ghost"
          size="icon-sm"
          className="ml-auto"
          aria-label="Refresh spacetimes"
          onClick={() => void query.refetch()}
        >
          <RefreshCw />
        </Button>
        <Button size="sm" onClick={() => setWizardOpen((open) => !open)}>
          <Plus />
          New spacetime
        </Button>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {wizardOpen ? (
          <div className="p-3 pb-1">
            <SpacetimeWizard
              world={world}
              onCancel={() => setWizardOpen(false)}
              onCreated={(item) => {
                setCreated(item)
                setWizardOpen(false)
              }}
            />
          </div>
        ) : null}

        {created !== null ? (
          <div className="mx-3 mt-3 flex flex-wrap items-center gap-2 rounded-xl border border-success/40 bg-success/10 px-3.5 py-2">
            <CheckCircle2 className="size-3.5 shrink-0 text-success" aria-hidden />
            <span className="text-[11px] text-fg">
              Created spacetime <span className="num">{created.name}</span> — status {created.status} ·{" "}
              {created.days} {created.days === 1 ? "day" : "days"} from {created.start_date ?? "—"}
            </span>
            <Button variant="outline" size="xs" className="ml-auto" onClick={() => openWatch(created.name)}>
              Open in watch
            </Button>
          </div>
        ) : null}

        {query.isPending ? (
          <p className="px-4 py-6 text-[11px] text-fg-subtle">Loading spacetimes…</p>
        ) : query.isError ? (
          <div className="m-3 card flex flex-col items-start gap-2 px-4 py-5">
            <p className="text-[11px] text-danger">
              Failed to load spacetimes: {errorMessage(query.error)}
            </p>
            <Button variant="outline" size="xs" onClick={() => void query.refetch()}>
              Retry
            </Button>
          </div>
        ) : items.length === 0 ? (
          <p className="px-4 py-6 text-[11px] text-fg-subtle">
            No spacetimes yet. This world is still a draft — households stay editable until its first
            spacetime is created.
          </p>
        ) : (
          <ul className="flex flex-col gap-2.5 p-3">
            {items.map((item) => (
              <SpacetimeRow
                key={item.name}
                world={world}
                item={item}
                highlighted={created?.name === item.name}
                onOpen={() => openWatch(item.name)}
              />
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
