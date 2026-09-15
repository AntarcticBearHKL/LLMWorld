import { Group, Layer, Rect, Text } from "react-konva"

import { formatWatts } from "@/lib/time"
import { useSceneTokens, type SceneTokens } from "../core/tokens"
import type { SceneState } from "../core/types"
import { outBandOf } from "../core/useSceneState"

interface RoomLayerProps {
  state: SceneState
}

const roomFill = (room: string, tokens: SceneTokens): string => {
  const lower = room.toLowerCase()
  if (lower.includes("kitchen") || lower.includes("bathroom") || lower.includes("laundry")) {
    return tokens.surface3
  }
  if (lower.includes("living") || lower.includes("dining")) return tokens.surface
  return tokens.surface2
}

export function RoomLayer({ state }: RoomLayerProps) {
  const tokens = useSceneTokens()
  const outBand = outBandOf({ width: state.layout.width, height: state.layout.height })

  return (
    <Layer listening={false}>
      {state.rooms.map((pose) => {
        const { rect } = pose
        const occupied = pose.occupants.length > 0
        const fill = roomFill(pose.room, tokens)
        return (
          <Group key={pose.room}>
            <Rect
              x={rect.x}
              y={rect.y}
              width={rect.w}
              height={rect.h}
              fill={fill}
              stroke={occupied ? tokens.brand : tokens.borderStrong}
              strokeWidth={occupied ? 1.5 : 1}
              cornerRadius={6}
            />
            {occupied ? (
              <Rect
                x={rect.x}
                y={rect.y}
                width={rect.w}
                height={rect.h}
                fill={tokens.brand}
                opacity={0.08}
                cornerRadius={6}
                listening={false}
              />
            ) : null}
            <Text
              x={rect.x + 8}
              y={rect.y + 6}
              width={Math.max(24, rect.w - 16)}
              text={pose.room}
              fontSize={11}
              fontStyle="bold"
              fill={tokens.fg}
              listening={false}
            />
            {pose.watts > 0 ? (
              <Text
                x={rect.x + 8}
                y={rect.y + rect.h - 16}
                width={Math.max(24, rect.w - 16)}
                align="right"
                text={formatWatts(pose.watts)}
                fontSize={10}
                fill={tokens.energy}
                listening={false}
              />
            ) : null}
          </Group>
        )
      })}

      <Group>
        <Rect
          x={outBand.x}
          y={outBand.y}
          width={outBand.w}
          height={outBand.h}
          fill={tokens.surface}
          stroke={tokens.borderStrong}
          strokeWidth={1}
          dash={[6, 4]}
          cornerRadius={8}
          listening={false}
        />
        <Text
          x={outBand.x + 12}
          y={outBand.y + outBand.h / 2 - 6}
          text="外出"
          fontSize={11}
          fill={tokens.fgMuted}
          listening={false}
        />
      </Group>
    </Layer>
  )
}
