import { Group, Rect, Text } from "react-konva"

import { formatWatts } from "@/lib/time"
import { useSceneTokens } from "./tokens"
import type { TownHouse } from "./types"
import { TOWN_HOUSE_HEIGHT, TOWN_HOUSE_WIDTH } from "./types"

interface HouseBuildingProps {
  town: TownHouse
  selected: boolean
  onEnter: (house: string) => void
}

const WINDOW_COLUMNS = 4
const WINDOW_ROWS = 2

export function HouseBuilding({ town, selected, onEnter }: HouseBuildingProps) {
  const tokens = useSceneTokens()
  const load = Math.max(0, Math.min(1, town.totalWatts / Math.max(1, town.maxWatts)))
  const litWindows = Math.round(load * WINDOW_COLUMNS * WINDOW_ROWS)
  const bodyX = town.x + (town.w - TOWN_HOUSE_WIDTH) / 2
  const bodyY = town.y + 26
  const bodyW = TOWN_HOUSE_WIDTH
  const bodyH = TOWN_HOUSE_HEIGHT - 26

  return (
    <Group onClick={() => onEnter(town.house)} onTap={() => onEnter(town.house)}>
      <Rect
        x={bodyX - 6}
        y={town.y + 6}
        width={bodyW + 12}
        height={bodyH + 32}
        fill={selected ? tokens.brand : tokens.surface}
        opacity={selected ? 0.18 : 0.5}
        cornerRadius={10}
      />

      <Rect
        x={bodyX + 10}
        y={town.y + 8}
        width={bodyW - 20}
        height={22}
        fill={tokens.borderStrong}
        cornerRadius={4}
      />

      <Rect
        x={bodyX}
        y={bodyY}
        width={bodyW}
        height={bodyH - 18}
        fill={tokens.surface2}
        stroke={selected ? tokens.brand : tokens.borderStrong}
        strokeWidth={selected ? 2 : 1}
        cornerRadius={6}
      />

      {Array.from({ length: WINDOW_COLUMNS * WINDOW_ROWS }).map((_unused, index) => {
        const column = index % WINDOW_COLUMNS
        const row = Math.floor(index / WINDOW_COLUMNS)
        const lit = index < litWindows
        const cellW = (bodyW - 28) / WINDOW_COLUMNS
        return (
          <Rect
            key={`window-${town.house}-${index}`}
            x={bodyX + 14 + column * cellW}
            y={bodyY + 12 + row * 22}
            width={Math.max(6, cellW - 8)}
            height={13}
            fill={lit ? tokens.energy : tokens.surface3}
            opacity={lit ? 0.45 + 0.55 * load : 1}
            cornerRadius={2}
          />
        )
      })}

      <Rect
        x={bodyX + 14}
        y={bodyY + bodyH - 26}
        width={bodyW - 28}
        height={6}
        fill={tokens.surface3}
        cornerRadius={3}
      />
      <Rect
        x={bodyX + 14}
        y={bodyY + bodyH - 26}
        width={Math.max(2, (bodyW - 28) * load)}
        height={6}
        fill={tokens.energy}
        cornerRadius={3}
      />

      <Text
        x={bodyX}
        y={town.y - 18}
        width={bodyW}
        align="center"
        text={`${town.house} · ${town.memberCount} 人 · ${formatWatts(town.totalWatts)}`}
        fontSize={11}
        fontStyle="bold"
        fill={load > 0.7 ? tokens.energy : tokens.fg}
      />
      <Text
        x={bodyX}
        y={town.y - 6}
        width={bodyW}
        align="center"
        text={`在家 ${town.homeCount} · 外出 ${town.outMembers.length}`}
        fontSize={9}
        fill={tokens.fgSubtle}
      />

      {town.outMembers.length > 0 ? (
        <Group>
          <Rect
            x={bodyX + bodyW - 4}
            y={town.y + 4}
            width={46}
            height={14}
            fill={tokens.surface3}
            stroke={tokens.borderStrong}
            strokeWidth={1}
            cornerRadius={7}
          />
          <Text
            x={bodyX + bodyW - 4}
            y={town.y + 7}
            width={46}
            align="center"
            text="OUT"
            fontSize={8}
            fill={tokens.fgMuted}
          />
        </Group>
      ) : null}
    </Group>
  )
}
