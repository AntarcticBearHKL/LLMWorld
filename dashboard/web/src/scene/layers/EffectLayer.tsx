import { useEffect, useRef } from "react"

import Konva from "konva"
import { Circle, Layer, Rect } from "react-konva"

import { effectFor, effectSlots, type EffectKind } from "../core/effects"
import { prefersReducedMotion, useSceneTokens } from "../core/tokens"
import type { SceneState } from "../core/types"
import { APPLIANCE_RADIUS } from "../core/types"

interface EffectLayerProps {
  state: SceneState
  enabled?: boolean
}

interface EffectNode {
  kind: EffectKind
  slot: number
  x: number
  y: number
  intensity: number
}

const SEP = "\u0000"

export function EffectLayer({ state, enabled = true }: EffectLayerProps) {
  const tokens = useSceneTokens()
  const layerRef = useRef<Konva.Layer>(null)
  const reduced = prefersReducedMotion()

  const nodes: EffectNode[] = []
  for (const pose of state.appliances) {
    const effect = effectFor(pose, state.lighting)
    if (effect.kind === "none") continue
    const slots = effectSlots(effect.kind)
    for (let slot = 0; slot < slots; slot += 1) {
      nodes.push({
        kind: effect.kind,
        slot,
        x: pose.pos.x,
        y: pose.pos.y,
        intensity: effect.intensity,
      })
    }
  }

  const nodeKey = `${state.house}:${state.minute}:${nodes.length}`

  useEffect(() => {
    const layer = layerRef.current
    if (layer === null || reduced || nodes.length === 0) return
    const meta = new Map<string, EffectNode>()
    for (const node of nodes) {
      meta.set(`${node.kind}${SEP}${node.slot}${SEP}${node.x}${SEP}${node.y}`, node)
    }
    const animation = new Konva.Animation((frame) => {
      const time = (frame?.time ?? 0) / 1000
      for (const child of layer.getChildren()) {
        const name = child.name()
        const parts = name.split(SEP)
        const kind = parts[0] as EffectKind | undefined
        const slot = Number(parts[1] ?? "0")
        const baseX = Number(parts[2] ?? "0")
        const baseY = Number(parts[3] ?? "0")
        const entry = meta.get(name)
        const intensity = entry?.intensity ?? 0.5
        if (kind === "steam") {
          const phase = (time * 0.7 + slot * 0.33) % 1
          child.y(baseY - APPLIANCE_RADIUS - 6 - phase * 18)
          child.opacity((1 - phase) * 0.7 * intensity)
        } else if (kind === "airflow") {
          const phase = (time * 0.8 + slot * 0.5) % 1
          const direction = slot % 2 === 0 ? 1 : -1
          child.x(baseX + direction * (APPLIANCE_RADIUS + phase * 22))
          child.opacity((1 - phase) * 0.6 * intensity)
        } else if (kind === "screen") {
          child.opacity(0.18 + 0.12 * Math.abs(Math.sin(time * 2.1)) * intensity)
        } else if (kind === "ring") {
          const pulse = 0.5 + 0.5 * Math.sin(time * 3)
          const ringScale = (APPLIANCE_RADIUS + 3 + pulse * 4) / (APPLIANCE_RADIUS + 3)
          child.scale({ x: ringScale, y: ringScale })
          child.opacity(0.35 + 0.45 * (1 - pulse) * intensity)
        } else if (kind === "drum") {
          child.rotation((time * 140) % 360)
        } else if (kind === "glow") {
          child.opacity((0.08 + 0.05 * Math.abs(Math.sin(time * 1.2))) * intensity)
        }
      }
    }, layer)
    animation.start()
    return () => {
      animation.stop()
    }
  }, [reduced, nodeKey, nodes.length])

  if (!enabled) return <Layer listening={false} />

  return (
    <Layer ref={layerRef} listening={false}>
      {nodes.map((node) => {
        const name = `${node.kind}${SEP}${node.slot}${SEP}${node.x}${SEP}${node.y}`
        if (node.kind === "steam") {
          return (
            <Circle
              key={name}
              name={name}
              x={node.x}
              y={node.y - APPLIANCE_RADIUS - 6}
              radius={2}
              fill={tokens.fgMuted}
              opacity={0}
            />
          )
        }
        if (node.kind === "airflow") {
          return (
            <Circle
              key={name}
              name={name}
              x={node.x}
              y={node.y}
              radius={1.5}
              fill={tokens.fgSubtle}
              opacity={0}
            />
          )
        }
        if (node.kind === "screen") {
          return (
            <Rect
              key={name}
              name={name}
              x={node.x - APPLIANCE_RADIUS - 1}
              y={node.y - APPLIANCE_RADIUS - 1}
              width={(APPLIANCE_RADIUS + 1) * 2}
              height={(APPLIANCE_RADIUS + 1) * 2}
              fill={tokens.brand}
              cornerRadius={3}
              opacity={0}
            />
          )
        }
        if (node.kind === "ring") {
          return (
            <Circle
              key={name}
              name={name}
              x={node.x}
              y={node.y}
              radius={APPLIANCE_RADIUS + 3}
              stroke={tokens.danger}
              strokeWidth={1.5}
              opacity={0}
            />
          )
        }
        if (node.kind === "drum") {
          return (
            <Rect
              key={name}
              name={name}
              x={node.x - 2}
              y={node.y - 2}
              width={4}
              height={4}
              fill={tokens.brand}
              offsetX={2}
              offsetY={2}
              cornerRadius={1}
              opacity={0.8}
            />
          )
        }
        return (
          <Circle
            key={name}
            name={name}
            x={node.x}
            y={node.y}
            radius={APPLIANCE_RADIUS * 3}
            fill={tokens.energy}
            opacity={0}
          />
        )
      })}
    </Layer>
  )
}
