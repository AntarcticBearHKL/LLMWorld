import { Button } from "@/components/ui/button"
import { useTimeStore, type ViewKey, type WorldTab } from "@/store/time"

type Level = "world" | "scenarios"

const levelFor = (view: ViewKey, tab: WorldTab): Level | null => {
  if (view === "world" || view === "watch") return tab === "household" ? "world" : "scenarios"
  return null
}

function LevelPill({
  label,
  active,
  onClick,
}: {
  label: string
  active: boolean
  onClick: () => void
}) {
  return (
    <Button
      variant={active ? "default" : "ghost"}
      size="sm"
      className="rounded-full"
      aria-current={active ? "location" : undefined}
      onClick={onClick}
    >
      {label}
    </Button>
  )
}

export function LevelPills() {
  const view = useTimeStore((state) => state.view)
  const worldsView = useTimeStore((state) => state.worldsView)
  const world = useTimeStore((state) => state.world)
  const tab = useTimeStore((state) => state.tab)
  const setView = useTimeStore((state) => state.setView)
  const setTab = useTimeStore((state) => state.setTab)

  const base = view === "jobs" ? worldsView : view
  const active = levelFor(base, tab)

  if (world.length === 0) return null

  return (
    <nav aria-label="Levels" className="flex flex-wrap items-center gap-1">
      <LevelPill
        label={world}
        active={active === "world"}
        onClick={() => {
          setView("world")
          setTab("household")
        }}
      />
      <LevelPill
        label="Scenarios"
        active={active === "scenarios"}
        onClick={() => {
          setView("world")
          setTab("scenarios")
        }}
      />
    </nav>
  )
}
