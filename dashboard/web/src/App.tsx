import { Fragment, useEffect } from "react"

import { Moon, Sun } from "lucide-react"

import { GenerateWizard } from "@/components/GenerateWizard"
import { JobsPanel } from "@/components/JobsPanel"
import { MetricStrip } from "@/components/MetricStrip"
import { ObserveDetail, ObserveGrid, ObserveScene } from "@/components/ObserveViews"
import { RunPicker } from "@/components/RunPicker"
import { SettingsPanel } from "@/components/SettingsPanel"
import { SimulateForm } from "@/components/SimulateForm"
import { TimeController } from "@/components/TimeController"
import { WorldWorkspace } from "@/components/WorldWorkspace"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { useBootstrapSelection } from "@/hooks/useBootstrapSelection"
import { useDayReplay } from "@/hooks/useDayData"
import { usePlayback } from "@/hooks/usePlayback"
import { useTheme } from "@/hooks/useTheme"
import { useUrlSync } from "@/hooks/useUrlSync"
import { cn } from "@/lib/utils"
import { useTimeStore, type ViewKey } from "@/store/time"

const VIEWS: ReadonlyArray<{
  key: ViewKey
  label: string
  hint: string
  group: "observe" | "control"
}> = [
  { key: "scene", label: "小镇", hint: "俯瞰各户，进屋看人和电器逐格走动", group: "observe" },
  { key: "grid", label: "住户网格", hint: "每个方格是一户，点击查看成员", group: "observe" },
  { key: "detail", label: "住户详情", hint: "逐格查看每人每台电器", group: "observe" },
  { key: "generate", label: "生成", hint: "可控生成世界（消耗额度）", group: "control" },
  {
    key: "build",
    label: "世界",
    hint: "世界工作台：构建 → 模拟 → 观看（观看内含小镇 / 网格 / 详情）",
    group: "control",
  },
  { key: "simulate", label: "模拟", hint: "逐户逐天推进模拟（消耗额度）", group: "control" },
  { key: "jobs", label: "任务", hint: "作业状态与实时日志", group: "control" },
  { key: "settings", label: "设置", hint: "LLM 运行参数（模型 / 温度 / 超时 / 重试）", group: "control" },
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
          LLMWorld 研究控制台
        </span>
        <span className="label-latin">household energy replay</span>
      </span>
    </div>
  )
}

function ViewSwitcher({ view, onChange }: { view: ViewKey; onChange: (next: ViewKey) => void }) {
  return (
    <nav
      className="flex items-center gap-0.5 rounded-md border border-border bg-surface-2 p-0.5"
      aria-label="工作区"
    >
      {VIEWS.map((item, index) => {
        const previous = VIEWS[index - 1]
        const boundary = previous !== undefined && previous.group !== item.group
        return (
          <Fragment key={item.key}>
            {boundary ? (
              <span className="mx-1 h-4 w-px shrink-0 self-center bg-border-strong" aria-hidden />
            ) : null}
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  onClick={() => onChange(item.key)}
                  aria-current={view === item.key ? "page" : undefined}
                  className={cn(
                    "rounded-sm px-2.5 py-1 text-[12px] font-medium transition-colors",
                    view === item.key
                      ? "bg-brand-soft text-brand"
                      : "text-fg-muted hover:bg-surface-3 hover:text-fg",
                  )}
                >
                  {item.label}
                </button>
              </TooltipTrigger>
              <TooltipContent>{item.hint}</TooltipContent>
            </Tooltip>
          </Fragment>
        )
      })}
    </nav>
  )
}

export default function App() {
  const { theme, toggleTheme } = useTheme()
  const view = useTimeStore((state) => state.view)
  const mode = useTimeStore((state) => state.mode)
  const setView = useTimeStore((state) => state.setView)
  const setHouse = useTimeStore((state) => state.setHouse)
  const setSelectedMember = useTimeStore((state) => state.setSelectedMember)
  const replayQuery = useDayReplay()

  usePlayback()
  useBootstrapSelection()
  useUrlSync()

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void import("@/scene/views/SceneView")
    }, 1200)
    return () => window.clearTimeout(timer)
  }, [])

  const replay = replayQuery.data
  const showToolbar =
    view === "scene" || view === "grid" || view === "detail" || (view === "build" && mode === "watch")

  const openHouse = (house: string) => {
    setHouse(house)
    setView("detail")
  }

  return (
    <div className="flex h-full min-h-0 flex-col bg-bg">
      <header className="glass sticky top-0 z-30 shrink-0 border-b border-border">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3 px-4 py-2.5">
          <BrandMark />
          <ViewSwitcher view={view} onChange={setView} />
          <div className="flex flex-1 justify-start lg:justify-center">
            {showToolbar ? <RunPicker /> : null}
          </div>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon-sm"
                onClick={toggleTheme}
                aria-label={theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
              >
                {theme === "dark" ? <Sun /> : <Moon />}
              </Button>
            </TooltipTrigger>
            <TooltipContent>{theme === "dark" ? "浅色主题" : "深色主题"}</TooltipContent>
          </Tooltip>
        </div>
        {showToolbar ? (
          <div className="border-t border-border px-4 py-3">
            <MetricStrip replay={replay} isPending={replayQuery.isPending} />
          </div>
        ) : null}
      </header>

      <main className="min-h-0 flex-1 overflow-hidden p-3">
        {view === "scene" ? (
          <ObserveScene
            onOpenPipeline={(memberId) => {
              setSelectedMember(memberId)
              setView("detail")
            }}
          />
        ) : null}

        {view === "grid" ? <ObserveGrid onOpen={openHouse} /> : null}

        {view === "detail" ? <ObserveDetail /> : null}

        {view === "generate" ? (
          <div className="mx-auto h-full w-full max-w-3xl overflow-y-auto rounded-lg border border-border bg-surface">
            <GenerateWizard />
          </div>
        ) : null}

        {view === "build" ? <WorldWorkspace /> : null}

        {view === "simulate" ? (
          <div className="mx-auto h-full w-full max-w-4xl overflow-y-auto rounded-lg border border-border bg-surface">
            <SimulateForm />
          </div>
        ) : null}

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

      {showToolbar ? (
        <footer className="glass sticky bottom-0 z-30 shrink-0 border-t border-border px-4 py-3">
          <TimeController />
        </footer>
      ) : null}
    </div>
  )
}
