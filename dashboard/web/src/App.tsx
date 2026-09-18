import { useState } from "react"

import { Plus, Settings } from "lucide-react"

import { FloatingJobsWindow } from "@/components/FloatingJobsWindow"
import { NewWorldSheet } from "@/components/NewWorldSheet"
import { SettingsPanel } from "@/components/SettingsPanel"
import { WatchView } from "@/components/WatchView"
import { WorldDetail } from "@/components/WorldDetail"
import { WorldsList } from "@/components/WorldsList"
import { ScreenChromeProvider, useScreenChromeValue } from "@/components/primitives/ScreenChrome"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { useUrlSync } from "@/hooks/useUrlSync"
import { useWorlds } from "@/hooks/useWorldBuild"
import { useTimeStore } from "@/store/time"

function ScreenChromeTitle() {
  const { title } = useScreenChromeValue()

  if (!title) return null

  return <h1 className="t-title flex min-w-0 items-center gap-2">{title}</h1>
}

function ScreenChromeActions() {
  const { actions } = useScreenChromeValue()

  if (!actions) return null

  return <span className="flex items-center gap-1.5">{actions}</span>
}

export default function App() {
  return (
    <ScreenChromeProvider>
      <AppShell />
    </ScreenChromeProvider>
  )
}

function AppShell() {
  const view = useTimeStore((state) => state.view)
  const worldsView = useTimeStore((state) => state.worldsView)
  const setView = useTimeStore((state) => state.setView)
  const setWorld = useTimeStore((state) => state.setWorld)
  const setJobsOpen = useTimeStore((state) => state.setJobsOpen)
  const worldsQuery = useWorlds()
  const [createOpen, setCreateOpen] = useState(false)

  useUrlSync()

  const worlds = worldsQuery.data ?? []

  const openWorld = (worldId: string) => {
    setWorld(worldId)
    setView("world")
  }

  const effectiveView = view === "jobs" ? worldsView : view
  const settingsOpen = effectiveView === "settings"

  const closeJobs = () => {
    setJobsOpen(false)
    if (view === "jobs") setView(effectiveView)
  }

  const toggleSettings = () => {
    setView(settingsOpen ? worldsView : "settings")
  }

  return (
    <div className="flex h-full min-h-0 flex-col bg-bg">
      <header className="glass sticky top-0 z-30 shrink-0 rounded-none border-b border-border">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3 px-4 py-2.5 lg:px-5">
          <div className="flex flex-1 flex-wrap items-center justify-start gap-1.5">
            <ScreenChromeTitle />
            <Button size="sm" variant="outline" onClick={() => setCreateOpen(true)}>
              <Plus />
              New world
            </Button>
          </div>

          <div className="flex flex-1 items-center justify-center gap-2">
            <span
              aria-hidden
              className="flex size-8 items-center justify-center rounded-lg bg-brand text-brand-fg shadow-1"
            >
              <span className="t-title text-brand-fg">W</span>
            </span>
            <span className="t-title">LLMWorld Research Console</span>
          </div>

          <div className="flex flex-1 flex-wrap items-center justify-end gap-1.5">
            <ScreenChromeActions />
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={settingsOpen ? "default" : "ghost"}
                  size="icon-sm"
                  onClick={toggleSettings}
                  aria-pressed={settingsOpen}
                  aria-label={settingsOpen ? "Close settings" : "Open settings"}
                >
                  <Settings />
                </Button>
              </TooltipTrigger>
              <TooltipContent>{settingsOpen ? "Close settings" : "Settings"}</TooltipContent>
            </Tooltip>
          </div>
        </div>
      </header>

      <main className="min-h-0 flex-1 overflow-y-auto p-3 lg:p-4">
        {effectiveView === "worlds" ? <WorldsList /> : null}

        {effectiveView === "world" ? <WorldDetail /> : null}

        {effectiveView === "watch" ? <WatchView /> : null}

        {effectiveView === "settings" ? (
          <div className="card h-full overflow-y-auto">
            <SettingsPanel />
          </div>
        ) : null}
      </main>

      <FloatingJobsWindow onClose={closeJobs} />

      <NewWorldSheet
        worldIds={worlds.map((info) => info.world_id)}
        open={createOpen}
        onOpenChange={setCreateOpen}
        onCreated={openWorld}
      />
    </div>
  )
}
