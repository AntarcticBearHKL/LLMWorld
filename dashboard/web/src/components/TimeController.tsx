import {
  ChevronsLeft,
  ChevronsRight,
  Pause,
  Play,
  SlidersHorizontal,
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
    <kbd className="num rounded-md border border-border-strong bg-surface-2 px-1.5 py-px text-[12px] text-fg-muted">
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
    <div className="pointer-events-none fixed inset-x-0 bottom-4 z-30 flex justify-center px-4">
      <div className="chrome-lg pointer-events-auto grid w-[min(760px,calc(100vw-2rem))] grid-cols-[128px_minmax(0,1fr)_316px] items-center gap-4 px-5 py-2.5 shadow-3">
        <div className="num t-body tabular-nums">
          <div className="flex items-baseline gap-2">
          <span className="num tabular-nums text-[34px] leading-none font-medium tracking-[-0.02em] text-fg">
            {formatHHMM(minute)}
          </span>
          <span className="flex flex-col leading-tight">
            <span className="label-micro text-fg-muted">{phaseOf(minute)}</span>
            <span className="num tabular-nums text-[12px] text-fg-muted">
              Step {currentStep}/{totalSteps}
            </span>
          </span>
        </div>
        </div>

        <div className="flex items-center justify-center gap-1.5">
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
                className="size-9"
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

        <div className="flex items-center justify-end gap-3">
        <div className="flex items-center gap-2.5 px-1">
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
            className="w-[120px] sm:w-[200px]"
          />
          <span className="num shrink-0 tabular-nums text-[12px] text-fg-muted">
            {progress.toFixed(1)}% · {formatMinutesAsDuration(remaining)} left
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="num tabular-nums text-[12px] text-fg-muted">
            ×{speed} · {stepMinutes} min/step
          </span>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon-xs" aria-label="Playback settings">
                <SlidersHorizontal />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="min-w-[240px]">
              <DropdownMenuLabel className="label-latin">Step size</DropdownMenuLabel>
              <DropdownMenuRadioGroup
                value={String(stepMinutes)}
                onValueChange={(value) => setStepMinutes(Number(value))}
              >
                {STEP_PRESETS.map((preset) => (
                  <DropdownMenuRadioItem key={preset} value={String(preset)} className="num">
                    {preset} min / step
                    <span className="ml-2 text-[12px] text-fg-muted">
                      full day: {stepCount(preset)} steps
                    </span>
                  </DropdownMenuRadioItem>
                ))}
              </DropdownMenuRadioGroup>

              <DropdownMenuLabel className="label-latin">Mode</DropdownMenuLabel>
              <DropdownMenuRadioGroup
                value={playMode}
                onValueChange={(value) => {
                  const next = PLAY_MODES.find((item) => item.value === value)
                  if (next !== undefined) setPlayMode(next.value)
                }}
              >
                {PLAY_MODES.map((item) => (
                  <DropdownMenuRadioItem key={item.value} value={item.value}>
                    {item.label}
                  </DropdownMenuRadioItem>
                ))}
              </DropdownMenuRadioGroup>

              <DropdownMenuLabel className="label-latin">Playback speed</DropdownMenuLabel>
              <DropdownMenuRadioGroup
                value={String(speed)}
                onValueChange={(value) => setSpeed(Number(value))}
              >
                {SPEED_PRESETS.map((preset) => (
                  <DropdownMenuRadioItem key={preset} value={String(preset)} className="num">
                    ×{preset}
                    <span className="ml-2 text-[12px] text-fg-muted">
                      {speedHint(preset, playMode)}
                    </span>
                  </DropdownMenuRadioItem>
                ))}
              </DropdownMenuRadioGroup>

              <DropdownMenuLabel className="label-latin">Shortcuts</DropdownMenuLabel>
              <div className="flex flex-wrap items-center gap-1.5 px-2 py-1.5">
                <Key>Space</Key>
                <span className="text-[12px] text-fg-muted">play</span>
                <Key>←</Key>
                <Key>→</Key>
                <span className="text-[12px] text-fg-muted">±1 step</span>
                <Key>Shift</Key>
                <span className="text-[12px] text-fg-muted">±60 min</span>
                <Key>Home</Key>
                <Key>End</Key>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        </div>
      </div>
    </div>
  )
}
