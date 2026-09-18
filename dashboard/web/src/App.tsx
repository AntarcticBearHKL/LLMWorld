import { Moon, Sun } from "lucide-react"

import { FloatingJobsWindow } from "@/components/FloatingJobsWindow"
import { SettingsPanel } from "@/components/SettingsPanel"
import { WatchView } from "@/components/WatchView"
import { WorldDetail } from "@/components/WorldDetail"
import { WorldsList } from "@/components/WorldsList"
import { ScreenChromeProvider, useScreenChromeValue } from "@/components/primitives/ScreenChrome"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { useTheme } from "@/hooks/useTheme"
import { useUrlSync } from "@/hooks/useUrlSync"
import { cn } from "@/lib/utils"
import { useTimeStore, type ViewKey } from "@/store/time"

const NAV: ReadonlyArray<{ key: ViewKey; label: string; hint: string }> = [
  {
    key: "worlds",
    label: "Worlds",
    hint: "All worlds — a world is a fixed set of blocks and households",
  },
  {
    key: "settings",
    label: "Settings",
    hint: "LLM runtime parameters (model / temperature / timeout / retries)",
  },
]

function BrandMark() {
  return (
    <div className="flex items-center gap-2.5">
      <span
        aria-hidden
        className="flex size-8 items-center justify-center rounded-lg bg-brand text-brand-fg shadow-1"
      >
        <span className="t-title text-brand-fg">W</span>
      </span>
      <span className="flex flex-col leading-tight">
        <span className="t-title text-fg">
          LLMWorld Research Console
        </span>
        <span className="label-latin text-fg-muted">household energy replay</span>
      </span>
    </div>
  )
}

function NavTabs({ active, onChange }: { active: ViewKey; onChange: (next: ViewKey) => void }) {
  return (
    <nav
      className="flex items-center gap-0.5 rounded-full border border-border bg-surface-2 p-0.5"
      aria-label="Primary"
    >
      {NAV.map((item) => (
        <Tooltip key={item.key}>
          <TooltipTrigger asChild>
            <button
              type="button"
              onClick={() => onChange(item.key)}
              aria-current={active === item.key ? "page" : undefined}
              className={cn(
                "rounded-full px-3.5 py-1 t-caption transition-colors",
                active === item.key
                  ? "bg-brand text-brand-fg shadow-1"
                  : "text-fg-muted hover:bg-item-hover hover:text-fg",
              )}
            >
              {item.label}
            </button>
          </TooltipTrigger>
          <TooltipContent>{item.hint}</TooltipContent>
        </Tooltip>
      ))}
    </nav>
  )
}

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
  const { theme, toggleTheme } = useTheme()
  const view = useTimeStore((state) => state.view)
  const worldsView = useTimeStore((state) => state.worldsView)
  const setView = useTimeStore((state) => state.setView)
  const setJobsOpen = useTimeStore((state) => state.setJobsOpen)

  useUrlSync()

  const effectiveView = view === "jobs" ? worldsView : view
  const active: ViewKey =
    effectiveView === "world" || effectiveView === "watch" ? "worlds" : effectiveView

  const closeJobs = () => {
    setJobsOpen(false)
    if (view === "jobs") setView(effectiveView)
  }

  const onNavChange = (next: ViewKey) => {
    if (next === "worlds") {
      setView("worlds")
      return
    }
    setView(next)
  }

  return (
    <div className="flex h-full min-h-0 flex-col bg-bg">
      <header className="glass sticky top-0 z-30 shrink-0 rounded-none border-b border-border">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3 px-4 py-2.5 lg:px-5">
          <BrandMark />
          <NavTabs active={active} onChange={onNavChange} />
          <ScreenChromeZone />
          <div className="ml-auto flex items-center gap-1.5">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="icon-sm"
                  onClick={toggleTheme}
                  aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
                >
                  {theme === "dark" ? <Sun /> : <Moon />}
                </Button>
              </TooltipTrigger>
              <TooltipContent>{theme === "dark" ? "Light theme" : "Dark theme"}</TooltipContent>
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
