import { Suspense, lazy } from "react"

import { ActivityTimeline } from "@/components/ActivityTimeline"
import { EnergyChart } from "@/components/EnergyChart"
import { HouseFloorplan } from "@/components/HouseFloorplan"
import { HouseSwitcher } from "@/components/HouseSwitcher"
import { MemberCards } from "@/components/MemberCards"
import { MultiHouseGrid } from "@/components/MultiHouseGrid"
import { PipelineDrawer } from "@/components/PipelineDrawer"
import { SnapshotPanel } from "@/components/SnapshotPanel"
import { useDayReplay } from "@/hooks/useDayData"
import { SceneFallback } from "@/scene/views/SceneFallback"

const SceneView = lazy(() =>
  import("@/scene/views/SceneView").then((module) => ({ default: module.SceneView })),
)

interface ObserveSceneProps {
  onOpenPipeline?: (memberId: string) => void
}

export function ObserveScene({ onOpenPipeline }: ObserveSceneProps) {
  return (
    <div className="h-full min-h-0">
      <Suspense fallback={<SceneFallback />}>
        <SceneView onOpenPipeline={onOpenPipeline} />
      </Suspense>
    </div>
  )
}

interface ObserveGridProps {
  onOpen: (house: string) => void
}

export function ObserveGrid({ onOpen }: ObserveGridProps) {
  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface">
      <MultiHouseGrid onOpen={onOpen} />
    </div>
  )
}

export function ObserveDetail() {
  const replayQuery = useDayReplay()
  const replay = replayQuery.data

  return (
    <div className="grid h-full min-h-0 grid-cols-1 gap-3 lg:grid-cols-2 xl:grid-cols-[minmax(0,300px)_minmax(0,1fr)_minmax(0,320px)]">
      <div className="flex min-h-0 flex-col gap-3 overflow-y-auto">
        <HouseFloorplan replay={replay} />
        <EnergyChart replay={replay} />
      </div>

      <div className="flex min-h-0 flex-col gap-3">
        <MemberCards replay={replay} />
        <ActivityTimeline
          replay={replay}
          isPending={replayQuery.isPending}
          error={replayQuery.error}
        />
      </div>

      <div className="flex min-h-0 flex-col gap-3 overflow-y-auto lg:col-span-2 xl:col-span-1">
        <SnapshotPanel />
        <HouseSwitcher />
        <PipelineDrawer />
      </div>
    </div>
  )
}
