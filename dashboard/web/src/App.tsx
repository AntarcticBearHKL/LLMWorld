import { Settings } from "lucide-react"

import { FloatingJobsWindow } from "@/components/FloatingJobsWindow"
import { SettingsPanel } from "@/components/SettingsPanel"
import { WatchView } from "@/components/WatchView"
import { WorldDetail } from "@/components/WorldDetail"
import { WorldsList } from "@/components/WorldsList"
import { LevelPills } from "@/components/primitives/LevelPills"
import { ScreenChromeProvider, useScreenChromeValue } from "@/components/primitives/ScreenChrome"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { useUrlSync } from "@/hooks/useUrlSync"
import { useTimeStore } from "@/store/time"

function ScreenChromeZone() {
  const { title, actions } = useScreenChromeValue()

  if (!title && !actions) return null

  return (
    <div className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-2">
      {title ? <span className="t-title flex min-w-0 items-center gap-2">{title}</span> : null}
      {actions ? <span className="flex items-center gap-1.5">{actions}</span> : null}
    </div>
  )
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
  const setJobsOpen = useTimeStore((state) => state.setJobsOpen)

  useUrlSync()

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
          <LevelPills />
          <ScreenChromeZone />
          <div className="ml-auto flex items-center gap-1.5">
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
    </div>
  )
}
