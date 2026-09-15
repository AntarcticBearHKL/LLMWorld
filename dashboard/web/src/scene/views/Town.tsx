import { useEffect, useMemo, useRef, useState } from "react"

import Konva from "konva"
import { Layer, Stage, Text } from "react-konva"

import { useSnapshot } from "@/hooks/useDayData"
import { formatHHMM } from "@/lib/time"
import { useTimeStore } from "@/store/time"
import { HouseBuilding } from "./HouseBuilding"
import { useSceneTokens } from "../core/tokens"
import type { TownHouse, TownLayout } from "../core/types"
import {
  SCENE_PADDING,
  TOWN_GAP_X,
  TOWN_GAP_Y,
  TOWN_HOUSE_HEIGHT,
  TOWN_HOUSE_WIDTH,
} from "../core/types"

interface TownProps {
  onEnter: (house: string) => void
}

const COLUMNS = 3

const isOut = (location: string): boolean => location.toLowerCase().includes("out")

export function Town({ onEnter }: TownProps) {
  const tokens = useSceneTokens()
  const snapshotQuery = useSnapshot()
  const minute = useTimeStore((store) => store.minute)
  const house = useTimeStore((store) => store.house)
  const wrapRef = useRef<HTMLDivElement>(null)
  const stageRef = useRef<Konva.Stage>(null)
  const [size, setSize] = useState({ width: 0, height: 0 })

  useEffect(() => {
    const wrap = wrapRef.current
    if (wrap === null) return
    const measure = () => setSize({ width: wrap.clientWidth, height: wrap.clientHeight })
    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(wrap)
    return () => observer.disconnect()
  }, [])

  const layout = useMemo<TownLayout | null>(() => {
    const houses = snapshotQuery.data?.houses
    if (houses === undefined || houses.length === 0) return null
    const peak = Math.max(1, ...houses.map((item) => item.total_watts))
    const list: TownHouse[] = houses.map((item, index) => {
      const column = index % COLUMNS
      const row = Math.floor(index / COLUMNS)
      const outMembers = item.people.filter((person) => isOut(person.location)).map((person) => person.member)
      return {
        house: item.house,
        householdType: item.household_type,
        memberCount: item.people.length,
        totalWatts: item.total_watts,
        maxWatts: peak,
        homeCount: item.people.length - outMembers.length,
        outMembers,
        profile: [],
        x: SCENE_PADDING + column * (TOWN_HOUSE_WIDTH + TOWN_GAP_X),
        y: SCENE_PADDING + row * (TOWN_HOUSE_HEIGHT + TOWN_GAP_Y) + 24,
        w: TOWN_HOUSE_WIDTH,
        h: TOWN_HOUSE_HEIGHT,
      }
    })
    const rows = Math.ceil(list.length / COLUMNS)
    return {
      houses: list,
      width: SCENE_PADDING * 2 + COLUMNS * TOWN_HOUSE_WIDTH + (COLUMNS - 1) * TOWN_GAP_X,
      height: SCENE_PADDING * 2 + rows * (TOWN_HOUSE_HEIGHT + TOWN_GAP_Y) + 24,
    }
  }, [snapshotQuery.data])

  useEffect(() => {
    const stage = stageRef.current
    if (stage === null || layout === null || size.width === 0 || size.height === 0) return
    const available = Math.min(
      (size.width - SCENE_PADDING) / Math.max(1, layout.width),
      (size.height - SCENE_PADDING) / Math.max(1, layout.height),
    )
    const scale = Math.max(0.3, Math.min(1.8, available))
    stage.scale({ x: scale, y: scale })
    stage.position({
      x: (size.width - layout.width * scale) / 2,
      y: (size.height - layout.height * scale) / 2,
    })
    stage.batchDraw()
  }, [layout, size.width, size.height])

  const onWheel = (event: Konva.KonvaEventObject<WheelEvent>) => {
    event.evt.preventDefault()
    const stage = stageRef.current
    if (stage === null) return
    const pointer = stage.getPointerPosition()
    if (pointer === null) return
    const previous = stage.scaleX()
    const next = Math.min(2.5, Math.max(0.3, previous * (event.evt.deltaY > 0 ? 1 / 1.1 : 1.1)))
    const anchor = { x: (pointer.x - stage.x()) / previous, y: (pointer.y - stage.y()) / previous }
    stage.scale({ x: next, y: next })
    stage.position({ x: pointer.x - anchor.x * next, y: pointer.y - anchor.y * next })
    stage.batchDraw()
  }

  return (
    <div
      ref={wrapRef}
      className="relative h-full w-full overflow-hidden"
      style={{ backgroundColor: tokens.bg }}
    >
      {layout !== null && size.width > 0 ? (
        <Stage ref={stageRef} width={size.width} height={size.height} draggable onWheel={onWheel}>
          <Layer>
            <Text
              x={SCENE_PADDING}
              y={8}
              text={`Town · ${formatHHMM(minute)} · ${layout.houses.length} households`}
              fontSize={12}
              fill={tokens.fgMuted}
            />
            {layout.houses.map((town) => (
              <HouseBuilding
                key={town.house}
                town={town}
                selected={town.house === house}
                onEnter={onEnter}
              />
            ))}
          </Layer>
        </Stage>
      ) : null}

      <div className="chip num pointer-events-none absolute bottom-3 right-3 text-[10px]">
        Scroll to zoom · drag to pan · select a house
      </div>
    </div>
  )
}
