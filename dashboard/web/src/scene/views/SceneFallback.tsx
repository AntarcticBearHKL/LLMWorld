import { Loader2 } from "lucide-react"

import { cn } from "@/lib/utils"

const TILE_COUNT = 12
const PANEL_ROWS = 4

export function SceneFallback() {
  return (
    <div className="card flex h-full min-h-0 flex-col overflow-hidden">
      <header className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-2 border-b border-border px-3.5 py-2.5">
        <span className="t-caption font-bold tracking-[-0.01em] text-fg">Scene</span>
        <span className="chip">
          <Loader2 className="size-3 animate-spin text-brand" aria-hidden />
          <span className="t-caption text-fg-muted">Loading the scene canvas</span>
        </span>
        <span className="t-caption ml-auto">
          react-konva (~350 kB) downloads once, then it opens instantly
        </span>
      </header>

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 p-3 lg:grid-cols-[minmax(0,1fr)_260px]">
        <div className="grid min-h-0 grid-cols-4 grid-rows-3 gap-2">
          {Array.from({ length: TILE_COUNT }).map((_unused, index) => (
            <div
              key={index}
              className={cn(
                "animate-pulse rounded-xl border border-border bg-surface-2",
                (index === 0 || index === 5) && "col-span-2 row-span-2",
              )}
              style={{ animationDelay: `${index * 60}ms` }}
            />
          ))}
        </div>
        <div className="flex flex-col gap-2">
          {Array.from({ length: PANEL_ROWS }).map((_unused, index) => (
            <div
              key={index}
              className="animate-pulse rounded-xl border border-border bg-surface-2"
              style={{ height: 64, animationDelay: `${index * 60}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
