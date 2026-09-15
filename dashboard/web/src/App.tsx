import { Moon, Sun } from "lucide-react"

import { JobsPanel } from "@/components/JobsPanel"
import { SettingsPanel } from "@/components/SettingsPanel"
import { WatchPlaceholder } from "@/components/WatchPlaceholder"
import { WorldDetail } from "@/components/WorldDetail"
import { WorldsList } from "@/components/WorldsList"
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
  { key: "jobs", label: "Jobs", hint: "Job queue and live logs" },
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
        className="flex size-7 items-center justify-center rounded-md border border-brand/40 bg-brand-soft"
      >
        <span className="num text-[11px] font-bold text-brand">W</span>
      </span>
      <span className="flex flex-col leading-tight">
        <span className="text-[13px] font-semibold tracking-[-0.01em] text-fg">
          LLMWorld Research Console
        </span>
        <span className="label-latin">household energy replay</span>
      </span>
    </div>
  )
}

function NavTabs({ active, onChange }: { active: ViewKey; onChange: (next: ViewKey) => void }) {
  return (
    <nav
      className="flex items-center gap-0.5 rounded-md border border-border bg-surface-2 p-0.5"
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
                "rounded-sm px-3 py-1 text-[12px] font-medium transition-colors",
                active === item.key
                  ? "bg-brand-soft text-brand"
                  : "text-fg-muted hover:bg-surface-3 hover:text-fg",
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

export default function App() {
  const { theme, toggleTheme } = useTheme()
  const view = useTimeStore((state) => state.view)
  const setView = useTimeStore((state) => state.setView)

  useUrlSync()

  const active: ViewKey = view === "world" || view === "watch" ? "worlds" : view

  return (
    <div className="flex h-full min-h-0 flex-col bg-bg">
      <header className="glass sticky top-0 z-30 shrink-0 border-b border-border">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3 px-4 py-2.5">
          <BrandMark />
          <NavTabs active={active} onChange={setView} />
          <div className="ml-auto">
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

      <main className="min-h-0 flex-1 overflow-hidden p-3">
        {view === "worlds" ? <WorldsList /> : null}

        {view === "world" ? <WorldDetail /> : null}

        {view === "watch" ? <WatchPlaceholder /> : null}

        {view === "jobs" ? (
          <div className="flex h-full min-h-0 flex-col">
            <JobsPanel />
          </div>
        ) : null}

        {view === "settings" ? (
          <div className="mx-auto h-full w-full max-w-3xl overflow-y-auto rounded-lg border border-border bg-surface">
            <SettingsPanel />
          </div>
        ) : null}
      </main>
    </div>
  )
}
