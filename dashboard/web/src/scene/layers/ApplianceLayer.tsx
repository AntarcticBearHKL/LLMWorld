import { useEffect, useRef, useState } from "react"

import Konva from "konva"
import { Circle, Label, Layer, Tag, Text } from "react-konva"

import { APPLIANCE_STATE_LABELS } from "@/lib/appliance"
import { formatWatts } from "@/lib/time"
import {
  applianceGlyph,
  appliancePulseName,
  applianceToneKey,
  type ToneKey,
} from "../core/appliances"
import { prefersReducedMotion, useSceneTokens, type SceneTokens } from "../core/tokens"
import type { SceneState } from "../core/types"
import { APPLIANCE_RADIUS } from "../core/types"

interface ApplianceLayerProps {
  state: SceneState
  highlighted?: string | null
}

const RADIUS = APPLIANCE_RADIUS + 3

const toneColor = (key: ToneKey, tokens: SceneTokens): string => {
  if (key === "energy") return tokens.energy
  if (key === "brand") return tokens.brand
  if (key === "fgMuted") return tokens.fgMuted
  if (key === "fgSubtle") return tokens.fgSubtle
  if (key === "bg") return tokens.bg
  return tokens.borderStrong
}

export function ApplianceLayer({ state, highlighted = null }: ApplianceLayerProps) {
  const tokens = useSceneTokens()
  const layerRef = useRef<Konva.Layer>(null)
  const [hovered, setHovered] = useState<string | null>(null)
  const reduced = prefersReducedMotion()
  const hasActive = state.appliances.some((pose) => pose.state === "active")

  useEffect(() => {
    const layer = layerRef.current
    if (layer === null || reduced || !hasActive) return
    const animation = new Konva.Animation((frame) => {
      const time = (frame?.time ?? 0) / 1000
      for (const node of layer.getChildren()) {
        const name = node.name()
        if (name === "pulse-active") node.opacity(0.7 + 0.3 * Math.sin(time * 2.4))
        else if (name === "pulse-cycling") node.opacity(0.45 + 0.55 * Math.abs(Math.sin(time * 3.2)))
      }
    }, layer)
    animation.start()
    return () => {
      animation.stop()
    }
  }, [reduced, hasActive, state.house])

  const hoverPose = state.appliances.find((pose) => pose.uniqueId === hovered)

  return (
    <>
      <Layer ref={layerRef} listening={false}>
        {state.appliances.map((pose) => {
          const tone = toneColor(applianceToneKey(pose.state, pose.cycling), tokens)
          const live = pose.state === "active" || pose.state === "baseload"
          return (
            <Circle
              key={pose.uniqueId}
              name={appliancePulseName(pose.state, pose.cycling)}
              x={pose.pos.x}
              y={pose.pos.y}
              radius={RADIUS}
              fill={tone}
              opacity={live ? 0.92 : 0.32}
              stroke={tone}
              strokeWidth={pose.cycling ? 2 : 1}
              perfectDrawEnabled={false}
              shadowForStrokeEnabled={false}
            />
          )
        })}
      </Layer>

      <Layer>
        {state.appliances.map((pose) => (
          <Circle
            key={`${pose.uniqueId}-hit`}
            x={pose.pos.x}
            y={pose.pos.y}
            radius={RADIUS + 6}
            fill="transparent"
            onMouseEnter={() => setHovered(pose.uniqueId)}
            onMouseLeave={() => setHovered((current) => (current === pose.uniqueId ? null : current))}
          />
        ))}

        {state.appliances.map((pose) => (
          <Text
            key={`${pose.uniqueId}-glyph`}
            x={pose.pos.x - RADIUS}
            y={pose.pos.y - 5}
            width={RADIUS * 2}
            align="center"
            text={applianceGlyph(pose.label, "")}
            fontSize={9}
            fill={pose.state === "active" || pose.state === "baseload" ? tokens.bg : tokens.fgSubtle}
            listening={false}
          />
        ))}

        {state.appliances
          .filter((pose) => pose.uniqueId === highlighted)
          .map((pose) => (
            <Circle
              key={`${pose.uniqueId}-halo`}
              x={pose.pos.x}
              y={pose.pos.y}
              radius={RADIUS + 4}
              stroke={tokens.brand}
              strokeWidth={2}
              listening={false}
            />
          ))}

        {hoverPose !== undefined ? (
          <Label x={hoverPose.pos.x + RADIUS + 4} y={hoverPose.pos.y - 22} listening={false}>
            <Tag fill={tokens.surface2} stroke={tokens.borderStrong} strokeWidth={1} cornerRadius={4} />
            <Text
              text={`${hoverPose.label} · ${formatWatts(hoverPose.watts)} · ${APPLIANCE_STATE_LABELS[hoverPose.state]}`}
              fontSize={10}
              padding={4}
              fill={tokens.fg}
            />
          </Label>
        ) : null}
      </Layer>
    </>
  )
}
