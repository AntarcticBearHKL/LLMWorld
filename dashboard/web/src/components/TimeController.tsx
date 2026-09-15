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
  { until: 360, label: "Night" },
  { until: 720, label: "Morning" },
  { until: 840, label: "Midday" },
  { until: 1080, label: "Afternoon" },
  { until: 1320, label: "Evening" },
  { until: DAY_MINUTES + 1, label: "Late night" },
]

const dayRunLabel = (preset: number): string => {
  const seconds = DAY_MINUTES / preset
  return seconds < 60 ? `${Math.round(seconds)} s` : formatMinutesAsDuration(seconds / 60)
}

const PLAY_MODES: ReadonlyArray<{ value: PlayMode; label: string }> = [
  { value: "continuous", label: "Continuous" },
  { value: "autoStep", label: "Auto-step" },
]

const formatDwell = (ms: number): string =>
  ms >= 1000 ? `${Number((ms / 1000).toFixed(1))} s` : `${ms} ms`

const speedHint = (preset: number, playMode: PlayMode): string =>
  playMode === "autoStep"
    ? `step every ${formatDwell(dwellMsFor(preset))}`
    : `full day in ${dayRunLabel(preset)}`

const phaseOf = (minute: number): string =>
  PHASES.find((phase) => minute < phase.until)?.label ?? "Late night"

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
        <TransportButton label="Back to 00:00 (Home)" onClick={() => setMinute(0)}>
          <ChevronsLeft />
        </TransportButton>
        <TransportButton
          label={`Previous step · back ${stepMinutes} min (←)`}
          onClick={() => jump(-1)}
        >
          <StepBack />
        </TransportButton>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              size="icon"
              onClick={togglePlay}
              aria-label={isPlaying ? "Pause" : "Play"}
              className="size-9 shadow-[inset_0_1px_0_rgb(255_255_255/0.08)]"
            >
              {isPlaying ? <Pause className="size-4" /> : <Play className="size-4" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent>{isPlaying ? "Pause (Space)" : "Play (Space)"}</TooltipContent>
        </Tooltip>
        <TransportButton
          label={`Next step · forward ${stepMinutes} min (→)`}
          onClick={() => jump(1)}
        >
          <StepForward />
        </TransportButton>
        <TransportButton label="Jump to 24:00 (End)" onClick={() => setMinute(DAY_MINUTES)}>
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
            Step {currentStep}/{totalSteps}
          </span>
        </span>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="num gap-1.5 px-2.5">
            {stepMinutes} min/step
            <ChevronDown className="size-3 opacity-60" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="min-w-[172px]">
          <DropdownMenuLabel className="label-latin">Step size</DropdownMenuLabel>
          <DropdownMenuRadioGroup
            value={String(stepMinutes)}
            onValueChange={(value) => setStepMinutes(Number(value))}
          >
            {STEP_PRESETS.map((preset) => (
              <DropdownMenuRadioItem key={preset} value={String(preset)} className="num">
                {preset} min / step
                <span className="ml-2 text-[10px] text-fg-subtle">
                  full day: {stepCount(preset)} steps
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
          aria-label="Day timeline"
          className="grow"
        />
        <span className="num shrink-0 text-[10px] text-fg-subtle">
          {progress.toFixed(1)}% · {formatMinutesAsDuration(remaining)} left
        </span>
      </div>

      <div className="flex items-center gap-2">
        <div
          className="flex items-center gap-0.5 rounded-md border border-border bg-surface-2 p-0.5"
          role="group"
          aria-label="Playback mode"
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
            Step every {formatDwell(dwellMsFor(speed))}
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
            <DropdownMenuLabel className="label-latin">Playback speed</DropdownMenuLabel>
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
        <Key>Space</Key>
        <span className="text-[10px] text-fg-subtle">play</span>
        <Key>←</Key>
        <Key>→</Key>
        <span className="text-[10px] text-fg-subtle">±1 step</span>
        <Key>Shift</Key>
        <span className="text-[10px] text-fg-subtle">±60 min</span>
        <Key>Home</Key>
        <Key>End</Key>
      </div>
    </div>
  )
}
