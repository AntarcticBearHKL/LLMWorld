import { Layers } from "lucide-react"

import { ObserveDetail, ObserveGrid, ObserveScene } from "@/components/ObserveViews"
import {
  SegmentedControl,
  type SegmentedOption,
} from "@/components/primitives/SegmentedControl"
import { SimulateForm } from "@/components/SimulateForm"
import { WorldBuilder } from "@/components/WorldBuilder"
import { useTimeStore, type WatchDensity, type WorldMode } from "@/store/time"

const MODES: ReadonlyArray<SegmentedOption<WorldMode>> = [
  { value: "build", label: "构建", hint: "手动分步构建世界：类型 → 人格 → 家庭 → 装配" },
  { value: "simulate", label: "模拟", hint: "逐户逐天推进模拟（消耗额度）" },
  { value: "watch", label: "观看", hint: "回放模拟结果：小镇 / 网格 / 详情" },
]

const DENSITIES: ReadonlyArray<SegmentedOption<WatchDensity>> = [
  { value: "town", label: "小镇", hint: "俯瞰各户，进屋看人和电器逐格走动" },
  { value: "grid", label: "网格", hint: "每个方格是一户，点击查看成员" },
  { value: "detail", label: "详情", hint: "逐格查看每人每台电器" },
]

export function WorldWorkspace() {
  const world = useTimeStore((state) => state.world)
  const mode = useTimeStore((state) => state.mode)
  const density = useTimeStore((state) => state.density)
  const setMode = useTimeStore((state) => state.setMode)
  const setDensity = useTimeStore((state) => state.setDensity)
  const setHouse = useTimeStore((state) => state.setHouse)
  const setSelectedMember = useTimeStore((state) => state.setSelectedMember)

  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      <header className="flex shrink-0 flex-wrap items-center gap-x-4 gap-y-2 rounded-lg border border-border bg-surface px-3 py-2">
        <span className="label-micro flex items-center gap-1.5">
          <Layers className="size-3" aria-hidden />
          世界工作区
        </span>
        <SegmentedControl options={MODES} value={mode} onChange={setMode} label="世界工作区模式" />
        {mode === "watch" ? (
          <SegmentedControl
            options={DENSITIES}
            value={density}
            onChange={setDensity}
            label="观看密度"
          />
        ) : null}
        <span className="num ml-auto text-[11px] text-fg-muted">
          {world.length > 0 ? world : "未选择世界"}
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
