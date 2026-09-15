import { Loader2 } from "lucide-react"

import { cn } from "@/lib/utils"

const TILE_COUNT = 12
const PANEL_ROWS = 4

export function SceneFallback() {
  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface">
      <header className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-2 border-b border-border px-3 py-2">
        <span className="text-[13px] font-semibold text-fg">场景</span>
        <span className="flex items-center gap-1.5 rounded-md border border-border bg-surface-2 px-2 py-1">
          <Loader2 className="size-3 animate-spin text-brand" aria-hidden />
          <span className="label-micro">正在加载场景画布</span>
        </span>
        <span className="label-micro ml-auto">首次需下载 react-konva（≈350 kB），之后秒开</span>
      </header>

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 p-3 lg:grid-cols-[minmax(0,1fr)_260px]">
        <div className="grid min-h-0 grid-cols-4 grid-rows-3 gap-2">
          {Array.from({ length: TILE_COUNT }).map((_unused, index) => (
            <div
              key={index}
              className={cn(
                "animate-pulse rounded-md border border-border bg-surface-2",
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
              className="animate-pulse rounded-md border border-border bg-surface-2"
              style={{ height: 64, animationDelay: `${index * 60}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
