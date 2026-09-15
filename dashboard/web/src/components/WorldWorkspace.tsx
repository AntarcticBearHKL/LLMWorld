import { useState } from "react"

import { Layers } from "lucide-react"

import { ObserveDetail, ObserveGrid, ObserveScene } from "@/components/ObserveViews"
import {
  SegmentedControl,
  type SegmentedOption,
} from "@/components/primitives/SegmentedControl"
import { SimulateForm } from "@/components/SimulateForm"
import { WorldBuilder } from "@/components/WorldBuilder"
import { useTimeStore } from "@/store/time"

type WorldMode = "build" | "simulate" | "watch"

type WatchDensity = "town" | "grid" | "detail"

const MODES: ReadonlyArray<SegmentedOption<WorldMode>> = [
  {
    value: "build",
    label: "Build",
    hint: "Build the world step by step: types → personas → household → assemble",
  },
  {
    value: "simulate",
    label: "Simulate",
    hint: "Advance one household at a time (spends API credits)",
  },
  {
    value: "watch",
    label: "Watch",
    hint: "Replay a simulated day: town / grid / detail",
  },
]

const DENSITIES: ReadonlyArray<SegmentedOption<WatchDensity>> = [
  {
    value: "town",
    label: "Town",
    hint: "Overhead view of every household; enter one to watch people and appliances",
  },
  { value: "grid", label: "Grid", hint: "One cell per household; click to see its members" },
  { value: "detail", label: "Detail", hint: "Inspect every member and appliance" },
]

export function WorldWorkspace() {
  const world = useTimeStore((state) => state.world)
  const [mode, setMode] = useState<WorldMode>("build")
  const [density, setDensity] = useState<WatchDensity>("town")
  const setHouse = useTimeStore((state) => state.setHouse)
  const setSelectedMember = useTimeStore((state) => state.setSelectedMember)

  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      <header className="flex shrink-0 flex-wrap items-center gap-x-4 gap-y-2 rounded-lg border border-border bg-surface px-3 py-2">
        <span className="label-micro flex items-center gap-1.5">
          <Layers className="size-3" aria-hidden />
          World workspace
        </span>
        <SegmentedControl
          options={MODES}
          value={mode}
          onChange={setMode}
          label="World workspace mode"
        />
        {mode === "watch" ? (
          <SegmentedControl
            options={DENSITIES}
            value={density}
            onChange={setDensity}
            label="Watch density"
          />
        ) : null}
        <span className="num ml-auto text-[11px] text-fg-muted">
          {world.length > 0 ? world : "no world selected"}
        </span>
      </header>

      <div className="flex min-h-0 flex-1 flex-col">
        {mode === "build" ? <WorldBuilder /> : null}

        {mode === "simulate" ? (
          <div className="mx-auto h-full w-full max-w-4xl overflow-y-auto rounded-lg border border-border bg-surface">
            <SimulateForm lockedWorld={world} />
          </div>
        ) : null}

        {mode === "watch" && density === "town" ? (
          <ObserveScene
            onOpenPipeline={(memberId) => {
              setSelectedMember(memberId)
              setDensity("detail")
            }}
          />
        ) : null}

        {mode === "watch" && density === "grid" ? (
          <ObserveGrid
            onOpen={(next) => {
              setHouse(next)
              setDensity("detail")
            }}
          />
        ) : null}

        {mode === "watch" && density === "detail" ? <ObserveDetail /> : null}
      </div>
    </div>
  )
}
