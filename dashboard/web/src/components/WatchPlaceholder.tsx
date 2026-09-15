import { ArrowLeft } from "lucide-react"

import { PlaceholderBadge } from "@/components/primitives/Placeholder"
import { Button } from "@/components/ui/button"
import { useTimeStore } from "@/store/time"

export function WatchPlaceholder() {
  const world = useTimeStore((state) => state.world)
  const run = useTimeStore((state) => state.run)
  const setView = useTimeStore((state) => state.setView)

  return (
    <div className="mx-auto flex h-full w-full max-w-3xl items-start">
      <section className="flex w-full flex-col gap-3 rounded-lg border border-border bg-surface p-4">
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="ghost"
            size="xs"
            onClick={() => setView(world.length > 0 ? "world" : "worlds")}
          >
            <ArrowLeft />
            {world.length > 0 ? "Back to world" : "All worlds"}
          </Button>
          <PlaceholderBadge milestone="part 2" className="ml-auto" />
        </div>

        <header className="flex flex-col gap-1">
          <h2 className="text-[13px] font-semibold text-fg">Watch</h2>
          <p className="text-[11px] text-fg-muted">
            The four-layer drill-down (world → block → house → indoor) is not built yet. It will replay
            one spacetime of one world: the town overview, then block, house, and indoor rooms with
            occupants.
          </p>
        </header>

        <p className="label-micro">
          World <span className="num text-fg-muted">{world.length > 0 ? world : "—"}</span> · spacetime{" "}
          <span className="num text-fg-muted">{run.length > 0 ? run : "—"}</span>
        </p>
      </section>
    </div>
  )
}
