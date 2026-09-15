import { useLayoutEffect, useRef, useState } from "react"

import Konva from "konva"
import { Circle, Group, Layer, Line, Text } from "react-konva"

import { useTimeStore } from "@/store/time"
import { prefersReducedMotion, useSceneTokens } from "./tokens"
import type { Point, SceneState } from "./types"
import { CHARACTER_RADIUS } from "./types"
import { outBandOf } from "./useSceneState"

interface CharacterLayerProps {
  state: SceneState
  showTrail?: boolean
}

const pointAlong = (points: Point[], t: number): Point => {
  const first = points[0]
  if (first === undefined) return { x: 0, y: 0 }
  if (points.length === 1) return first
  const lengths: number[] = []
  let total = 0
  for (let index = 0; index + 1 < points.length; index += 1) {
    const a = points[index]
    const b = points[index + 1]
    if (a === undefined || b === undefined) continue
    const length = Math.hypot(b.x - a.x, b.y - a.y)
    lengths.push(length)
    total += length
  }
  if (total <= 0) return points[points.length - 1] ?? first
  let remaining = t * total
  for (let index = 0; index < lengths.length; index += 1) {
    const length = lengths[index] ?? 0
    const a = points[index]
    const b = points[index + 1]
    if (a === undefined || b === undefined) continue
    if (remaining <= length || index === lengths.length - 1) {
      const ratio = length <= 0 ? 1 : Math.min(1, remaining / length)
      return { x: a.x + (b.x - a.x) * ratio, y: a.y + (b.y - a.y) * ratio }
    }
    remaining -= length
  }
  return points[points.length - 1] ?? first
}

const walkDuration = (stepMinutes: number): number =>
  Math.min(600, Math.max(160, stepMinutes * 40))

export function CharacterLayer({ state, showTrail = false }: CharacterLayerProps) {
  const tokens = useSceneTokens()
  const stepMinutes = useTimeStore((store) => store.stepMinutes)
  const setSelectedMember = useTimeStore((store) => store.setSelectedMember)
  const nodes = useRef<Map<string, Konva.Group>>(new Map())
  const animations = useRef<Map<string, Konva.Animation>>(new Map())
  const roomMemo = useRef<Map<string, string | null>>(new Map())
  const [trails, setTrails] = useState<Record<string, Point[]>>({})
  const reduced = prefersReducedMotion()
  const outBand = outBandOf({ width: state.layout.width, height: state.layout.height })

  useLayoutEffect(() => {
    const additions: Record<string, Point[]> = {}
    for (const pose of state.characters) {
      const node = nodes.current.get(pose.memberId)
      if (node === undefined) continue
      const previous = roomMemo.current.get(pose.memberId)
      if (previous === pose.room && previous !== undefined) continue
      roomMemo.current.set(pose.memberId, pose.room)

      if (previous !== undefined) additions[pose.memberId] = [pose.pos]

      if (previous === undefined) {
        node.position(pose.pos)
        continue
      }

      animations.current.get(pose.memberId)?.stop()
      animations.current.delete(pose.memberId)

      if (reduced) {
        node.position(pose.pos)
        continue
      }

      const from = { x: node.x(), y: node.y() }
      const raw =
        previous !== null && pose.room !== null
          ? state.layout.pathBetween(previous, pose.room)
          : [from, pose.pos]
      const polyline: Point[] = raw.length > 1 ? [from, ...raw.slice(1)] : [from, pose.pos]
      const duration = walkDuration(stepMinutes)
      const startedAt = performance.now()

      const animation = new Konva.Animation((frame) => {
        const elapsed = (frame?.time ?? performance.now()) - startedAt
        const t = Math.min(1, elapsed / duration)
        node.position(pointAlong(polyline, t * t * (3 - 2 * t)))
        if (t >= 1) {
          animations.current.delete(pose.memberId)
          animation.stop()
        }
      }, node.getLayer())
      animations.current.set(pose.memberId, animation)
      animation.start()
    }

    const keys = Object.keys(additions)
    if (keys.length > 0) {
      setTrails((previous) => {
        const next: Record<string, Point[]> = { ...previous }
        for (const key of keys) {
          const added = additions[key]
          if (added === undefined) continue
          next[key] = [...(previous[key] ?? []), ...added]
        }
        return next
      })
    }
  }, [state, stepMinutes, reduced])

  useLayoutEffect(() => {
    const running = animations.current
    return () => {
      for (const animation of running.values()) animation.stop()
      running.clear()
    }
  }, [])

  return (
    <Layer>
      {showTrail
        ? state.characters.map((pose) => {
            const points = trails[pose.memberId] ?? []
            if (points.length < 2) return null
            const flat: number[] = []
            for (const point of points) flat.push(point.x, point.y)
            return (
              <Line
                key={`trail-${pose.memberId}`}
                points={flat}
                stroke={pose.color}
                strokeWidth={1}
                dash={[4, 4]}
                opacity={0.35}
                listening={false}
              />
            )
          })
        : null}

      {state.characters.map((pose) => (
        <Group
          key={pose.memberId}
          ref={(node) => {
            if (node === null) nodes.current.delete(pose.memberId)
            else nodes.current.set(pose.memberId, node)
          }}
          opacity={pose.isOut ? 0.55 : 1}
          onClick={() => setSelectedMember(pose.selected ? null : pose.memberId)}
          onTap={() => setSelectedMember(pose.selected ? null : pose.memberId)}
        >
          <Circle
            radius={CHARACTER_RADIUS}
            fill={pose.color}
            stroke={pose.selected ? tokens.fg : tokens.border}
            strokeWidth={pose.selected ? 2 : 1}
          />
          <Text
            x={-CHARACTER_RADIUS}
            y={-5}
            width={CHARACTER_RADIUS * 2}
            align="center"
            text={pose.initial}
            fontSize={11}
            fontStyle="bold"
            fill={tokens.bg}
            listening={false}
          />
          {pose.sleeping ? (
            <Text
              x={CHARACTER_RADIUS - 2}
              y={-CHARACTER_RADIUS - 10}
              text="Z"
              fontSize={10}
              fill={tokens.fgMuted}
              listening={false}
            />
          ) : null}
          {pose.isOut ? (
            <Text
              x={-18}
              y={CHARACTER_RADIUS + 2}
              width={36}
              align="center"
              text="OUT"
              fontSize={8}
              fill={tokens.fgMuted}
              listening={false}
            />
          ) : null}
        </Group>
      ))}

      <Text
        x={outBand.x + 12}
        y={outBand.y + 6}
        text={state.outMembers.length > 0 ? `${state.outMembers.length} 人外出` : ""}
        fontSize={9}
        fill={tokens.fgSubtle}
        listening={false}
      />
    </Layer>
  )
}
