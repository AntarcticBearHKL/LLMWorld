import {
  ChevronDown,
  ChevronsLeft,
  ChevronsRight,
  Pause,
  Play,
  StepBack,
  StepForward,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Slider } from "@/components/ui/slider"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import {
  DAY_MINUTES,
  SPEED_PRESETS,
  STEP_PRESETS,
  formatHHMM,
  formatMinutesAsDuration,
  stepCount,
  stepIndex,
} from "@/lib/time"
import { cn } from "@/lib/utils"
import { dwellMsFor, useTimeStore, type PlayMode } from "@/store/time"

const PHASES: ReadonlyArray<{ until: number; label: string }> = [
  { until: 360, label: "凌晨" },
  { until: 720, label: "上午" },
  { until: 840, label: "中午" },
  { until: 1080, label: "下午" },
  { until: 1320, label: "傍晚" },
  { until: DAY_MINUTES + 1, label: "夜间" },
]

const dayRunLabel = (preset: number): string => {
  const seconds = DAY_MINUTES / preset
  return seconds < 60 ? `${Math.round(seconds)} 秒` : formatMinutesAsDuration(seconds / 60)
}

const PLAY_MODES: ReadonlyArray<{ value: PlayMode; label: string }> = [
  { value: "continuous", label: "连续" },
  { value: "autoStep", label: "跳格" },
]

const formatDwell = (ms: number): string =>
  ms >= 1000 ? `${Number((ms / 1000).toFixed(1))} 秒` : `${ms} ms`

const speedHint = (preset: number, playMode: PlayMode): string =>
  playMode === "autoStep"
    ? `每格 ${formatDwell(dwellMsFor(preset))}`
    : `${dayRunLabel(preset)}跑完全天`

const phaseOf = (minute: number): string =>
  PHASES.find((phase) => minute < phase.until)?.label ?? "夜间"

function Key({ children }: { children: string }) {
  return (
    <kbd className="num rounded-sm border border-border bg-surface-2 px-1 py-px text-[10px] text-fg-muted">
      {children}
    </kbd>
  )
}

function TransportButton({
  label,
  onClick,
  children,
}: {
  label: string
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button variant="outline" size="icon-sm" onClick={onClick} aria-label={label}>
          {children}
        </Button>
      </TooltipTrigger>
      <TooltipContent>{label}</TooltipContent>
    </Tooltip>
  )
}

export function TimeController() {
  const minute = useTimeStore((state) => state.minute)
  const isPlaying = useTimeStore((state) => state.isPlaying)
  const playMode = useTimeStore((state) => state.playMode)
  const speed = useTimeStore((state) => state.speed)
  const stepMinutes = useTimeStore((state) => state.stepMinutes)
  const togglePlay = useTimeStore((state) => state.togglePlay)
  const setMinute = useTimeStore((state) => state.setMinute)
  const stepOnce = useTimeStore((state) => state.stepOnce)
  const setPlaying = useTimeStore((state) => state.setPlaying)
  const setPlayMode = useTimeStore((state) => state.setPlayMode)
  const setStepMinutes = useTimeStore((state) => state.setStepMinutes)
  const setSpeed = useTimeStore((state) => state.setSpeed)

  const jump = (direction: 1 | -1) => {
    setPlaying(false)
    stepOnce(direction)
  }

  const progress = (minute / DAY_MINUTES) * 100
  const remaining = DAY_MINUTES - minute
  const currentStep = stepIndex(minute, stepMinutes)
  const totalSteps = stepCount(stepMinutes)

  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-3">
      <div className="flex items-center gap-1.5">
        <TransportButton label="回到 00:00（Home）" onClick={() => setMinute(0)}>
          <ChevronsLeft />
        </TransportButton>
        <TransportButton label={`上一格 · 后退 ${stepMinutes} 分钟（←）`} onClick={() => jump(-1)}>
          <StepBack />
        </TransportButton>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              size="icon"
              onClick={togglePlay}
              aria-label={isPlaying ? "暂停" : "播放"}
              className="size-9 shadow-[inset_0_1px_0_rgb(255_255_255/0.08)]"
            >
              {isPlaying ? <Pause className="size-4" /> : <Play className="size-4" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent>{isPlaying ? "暂停（空格）" : "播放（空格）"}</TooltipContent>
        </Tooltip>
        <TransportButton label={`下一格 · 前进 ${stepMinutes} 分钟（→）`} onClick={() => jump(1)}>
          <StepForward />
        </TransportButton>
        <TransportButton label="跳到 24:00（End）" onClick={() => setMinute(DAY_MINUTES)}>
          <ChevronsRight />
        </TransportButton>
      </div>

      <div className="flex items-baseline gap-2">
        <span className="num text-[34px] leading-none font-medium tracking-[-0.02em] text-fg">
          {formatHHMM(minute)}
        </span>
        <span className="flex flex-col leading-tight">
          <span className="label-micro">{phaseOf(minute)}</span>
          <span className="num text-[10px] text-fg-subtle">
            第 {currentStep}/{totalSteps} 格
          </span>
        </span>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="num gap-1.5 px-2.5">
            {stepMinutes} 分/格
            <ChevronDown className="size-3 opacity-60" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="min-w-[172px]">
          <DropdownMenuLabel className="label-latin">步长</DropdownMenuLabel>
          <DropdownMenuRadioGroup
            value={String(stepMinutes)}
            onValueChange={(value) => setStepMinutes(Number(value))}
          >
            {STEP_PRESETS.map((preset) => (
              <DropdownMenuRadioItem key={preset} value={String(preset)} className="num">
                {preset} 分钟 / 格
                <span className="ml-2 text-[10px] text-fg-subtle">
                  全天 {stepCount(preset)} 格
                </span>
              </DropdownMenuRadioItem>
            ))}
          </DropdownMenuRadioGroup>
        </DropdownMenuContent>
      </DropdownMenu>

      <div className="flex min-w-[200px] flex-1 items-center gap-3">
        <Slider
          value={[minute]}
          min={0}
          max={DAY_MINUTES}
          step={stepMinutes}
          onValueChange={(value) => {
            const next = value[0]
            if (typeof next === "number") {
              setMinute(next)
              useTimeStore.getState().setPlaying(false)
            }
          }}
          aria-label="全天时间滑块"
          className="grow"
        />
        <span className="num shrink-0 text-[10px] text-fg-subtle">
          {progress.toFixed(1)}% · 余 {formatMinutesAsDuration(remaining)}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <div
          className="flex items-center gap-0.5 rounded-md border border-border bg-surface-2 p-0.5"
          role="group"
          aria-label="播放模式"
        >
          {PLAY_MODES.map((item) => (
            <button
              key={item.value}
              type="button"
              onClick={() => setPlayMode(item.value)}
              aria-pressed={playMode === item.value}
              className={cn(
                "rounded-sm px-2.5 py-1 text-[12px] font-medium transition-colors",
                playMode === item.value
                  ? "bg-brand-soft text-brand"
                  : "text-fg-muted hover:bg-surface-3 hover:text-fg",
              )}
            >
              {item.label}
            </button>
          ))}
        </div>
        {playMode === "autoStep" ? (
          <span className="num text-[10px] text-fg-subtle">
            每格 {formatDwell(dwellMsFor(speed))}
          </span>
        ) : null}
      </div>

      <div className="flex items-center gap-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="num gap-1.5 px-2.5">
              ×{speed}
              <ChevronDown className="size-3 opacity-60" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="min-w-[168px]">
            <DropdownMenuLabel className="label-latin">回放倍速</DropdownMenuLabel>
            <DropdownMenuRadioGroup
              value={String(speed)}
              onValueChange={(value) => setSpeed(Number(value))}
            >
              {SPEED_PRESETS.map((preset) => (
                <DropdownMenuRadioItem key={preset} value={String(preset)} className="num">
                  ×{preset}
                  <span className="ml-2 text-[10px] text-fg-subtle">
                    {speedHint(preset, playMode)}
                  </span>
                </DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="hidden items-center gap-1.5 2xl:flex">
        <Key>空格</Key>
        <span className="text-[10px] text-fg-subtle">播放</span>
        <Key>←</Key>
        <Key>→</Key>
        <span className="text-[10px] text-fg-subtle">±1 格</span>
        <Key>Shift</Key>
        <span className="text-[10px] text-fg-subtle">±60 分</span>
        <Key>Home</Key>
        <Key>End</Key>
      </div>
    </div>
  )
}
