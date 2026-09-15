import { useCallback, useEffect, useRef, useState, type ReactNode } from "react"

import Konva from "konva"
import { Layer, Rect, Stage } from "react-konva"

import { useTimeStore } from "@/store/time"
import { RoomLayer } from "../layers/RoomLayer"
import { useSceneTokens } from "../core/tokens"
import type { SceneState } from "../core/types"
import { SCENE_PADDING } from "../core/types"

interface SceneStageProps {
  state: SceneState
  children?: ReactNode
}

export function SceneStage({ state, children }: SceneStageProps) {
  const tokens = useSceneTokens()
  const wrapRef = useRef<HTMLDivElement>(null)
  const stageRef = useRef<Konva.Stage>(null)
  const [size, setSize] = useState({ width: 0, height: 0 })
  const [dragging, setDragging] = useState(false)
  const setSelectedMember = useTimeStore((store) => store.setSelectedMember)

  useEffect(() => {
    const wrap = wrapRef.current
    if (wrap === null) return
    const measure = () => setSize({ width: wrap.clientWidth, height: wrap.clientHeight })
    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(wrap)
    return () => observer.disconnect()
  }, [])

  const fit = useCallback(() => {
    const stage = stageRef.current
    if (stage === null || size.width === 0 || size.height === 0) return
    const available = Math.min(
      (size.width - SCENE_PADDING * 2) / Math.max(1, state.layout.width),
      (size.height - SCENE_PADDING * 2) / Math.max(1, state.layout.height),
    )
    const scale = Math.max(0.2, Math.min(2.4, available))
    stage.scale({ x: scale, y: scale })
    stage.position({
      x: (size.width - state.layout.width * scale) / 2,
      y: (size.height - state.layout.height * scale) / 2,
    })
    stage.batchDraw()
  }, [size.width, size.height, state.layout.width, state.layout.height])

  useEffect(() => {
    fit()
  }, [fit, state.house])

  const onWheel = (event: Konva.KonvaEventObject<WheelEvent>) => {
    event.evt.preventDefault()
    const stage = stageRef.current
    if (stage === null) return
    const pointer = stage.getPointerPosition()
    if (pointer === null) return
    const previous = stage.scaleX()
    const factor = event.evt.deltaY > 0 ? 1 / 1.1 : 1.1
    const next = Math.min(3, Math.max(0.5, previous * factor))
    const anchor = {
      x: (pointer.x - stage.x()) / previous,
      y: (pointer.y - stage.y()) / previous,
    }
    stage.scale({ x: next, y: next })
    stage.position({ x: pointer.x - anchor.x * next, y: pointer.y - anchor.y * next })
    stage.batchDraw()
  }

  return (
    <div
      ref={wrapRef}
      className="relative h-full w-full overflow-hidden"
      role="img"
      aria-label={`住户室内场景：${state.rooms.length} 个房间、${state.appliances.length} 台电器、${state.characters.length} 名成员`}
      style={{ backgroundColor: tokens.bg, cursor: dragging ? "grabbing" : "grab" }}
    >
      {size.width > 0 && size.height > 0 ? (
        <Stage
          ref={stageRef}
          width={size.width}
          height={size.height}
          draggable
          onWheel={onWheel}
          onDragStart={() => setDragging(true)}
          onDragEnd={() => setDragging(false)}
          onDblClick={fit}
          onClick={(event) => {
            if (event.target === event.target.getStage()) setSelectedMember(null)
          }}
        >
          <RoomLayer state={state} />
          {children}
          <Layer listening={false}>
            <Rect
              x={0}
              y={0}
              width={state.layout.width}
              height={state.layout.height}
              fill={state.lighting.tint}
              listening={false}
            />
            {state.lighting.peakWindow ? (
              <Rect
                x={0}
                y={0}
                width={state.layout.width}
                height={4}
                fill={tokens.energy}
                listening={false}
              />
            ) : null}
          </Layer>
        </Stage>
      ) : null}

      <div className="pointer-events-none absolute bottom-2 right-3 flex items-center gap-2 text-[10px] text-fg-subtle">
        <span className="num">滚轮缩放 · 拖拽平移 · 双击复位 · 点击小人看详情</span>
      </div>
    </div>
  )
}
