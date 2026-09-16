import { WorldDetail } from "@/components/WorldDetail"
import { WorldsList } from "@/components/WorldsList"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

export function WorldsWorkspace() {
  const world = useTimeStore((state) => state.world)
  const selected = world.length > 0

  return (
    <div className="grid h-full min-h-0 grid-rows-[minmax(0,1fr)] gap-3 lg:grid-cols-[minmax(300px,360px)_minmax(0,1fr)]">
      <div className={cn("flex min-h-0 flex-col", selected && "max-lg:hidden")}>
        <WorldsList />
      </div>
      <div className={cn("flex min-h-0 flex-col", !selected && "max-lg:hidden")}>
        <WorldDetail />
      </div>
    </div>
  )
}
