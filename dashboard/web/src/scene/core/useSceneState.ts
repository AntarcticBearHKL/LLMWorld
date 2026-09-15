import { useMemo } from "react"

import type { DayReplay, HouseholdInfo } from "@/api/types"
import { categorizeActivity } from "@/lib/activity"
import { roomOf, stateAt, wattsAt } from "@/lib/appliance"
import { memberColorVar, memberInitial } from "@/lib/members"
import { useTimeStore } from "@/store/time"
import { applianceSlot } from "./appliances"
import { buildLayout } from "./layout"
import { lightingFor } from "./lighting"
import type {
  AppliancePose,
  CharacterPose,
  Point,
  RoomInput,
  RoomPose,
  RoomRect,
  SceneSize,
  SceneState,
} from "./types"
import { ROOM_GAP } from "./types"

export const roomInputsOf = (household: HouseholdInfo): RoomInput[] => {
  if (household.room_meta.length > 0) {
    return household.room_meta.map((room) => ({ name: room.name, size: room.size }))
  }
  return household.rooms.map((name) => ({ name, size: null }))
}

const isLitLabel = (label: string): boolean => {
  const lower = label.toLowerCase()
  return lower.includes("light") || lower.includes("lamp")
}

const ringOffset = (index: number, count: number, radius: number): Point => {
  if (count <= 1) return { x: 0, y: 0 }
  const angle = (index / count) * Math.PI * 2 - Math.PI / 2
  return { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius }
}

const OUT_BAND_HEIGHT = 56

export const outBandOf = (size: SceneSize): RoomRect => ({
  room: "外出",
  x: ROOM_GAP + 6,
  y: Math.max(ROOM_GAP + 6, size.height - OUT_BAND_HEIGHT - ROOM_GAP),
  w: Math.min(340, Math.max(140, size.width - (ROOM_GAP + 6) * 2)),
  h: OUT_BAND_HEIGHT,
})

export function useSceneState(replay: DayReplay | undefined, size: SceneSize): SceneState | null {
  const minute = useTimeStore((state) => state.minute)

  const layout = useMemo(() => {
    if (replay === undefined) return null
    const inputs = roomInputsOf(replay.household)
    if (inputs.length === 0) return null
    return buildLayout(inputs, size)
  }, [replay, size.width, size.height])

  return useMemo(() => {
    if (replay === undefined || layout === null) return null
    const household = replay.household
    const memberIds = replay.members.map((member) => member.id)
    const outBand = outBandOf(size)

    const locationOf = (memberId: string): string | null => {
      const member = replay.members.find((item) => item.id === memberId)
      if (member === undefined) return null
      const segment = member.activities.find((item) => minute >= item.start && minute < item.end)
      if (segment === undefined) return null
      return layout.rectOf(segment.location) === undefined ? null : segment.location
    }

    const placements = replay.appliances.map((appliance, index) => {
      const roomName = roomOf(appliance.info)
      const rect = layout.rectOf(roomName)
      const slotIndex = replay.appliances
        .slice(0, index)
        .filter((item) => roomOf(item.info) === roomName).length
      return {
        appliance,
        rect,
        pos: rect === undefined ? undefined : applianceSlot(slotIndex, rect),
      }
    })

    const roomPoses: RoomPose[] = layout.rects.map((rect) => {
      const owned = placements.filter((entry) => entry.rect?.room === rect.room)
      const watts = owned.reduce((sum, entry) => sum + wattsAt(entry.appliance, minute), 0)
      return {
        room: rect.room,
        rect,
        watts,
        occupants: memberIds.filter((id) => locationOf(id) === rect.room),
      }
    })

    const appliances: AppliancePose[] = []
    for (const entry of placements) {
      if (entry.pos === undefined || entry.rect === undefined) continue
      const info = entry.appliance.info
      const state = stateAt(entry.appliance, minute)
      appliances.push({
        uniqueId: entry.appliance.unique_id,
        label: info.name,
        room: entry.rect.room,
        pos: entry.pos,
        watts: wattsAt(entry.appliance, minute),
        state,
        cycling: state === "active" && (info.type === "cycle" || info.type === "charging"),
      })
    }

    const roomCounts = new Map<string, number>()
    for (const id of memberIds) {
      const room = locationOf(id)
      if (room === null) continue
      roomCounts.set(room, (roomCounts.get(room) ?? 0) + 1)
    }

    let outIndex = 0
    const outStep = Math.max(30, (outBand.w - 80) / Math.max(1, memberIds.length))
    const characters: CharacterPose[] = replay.members.map((member) => {
      const segment = member.activities.find((item) => minute >= item.start && minute < item.end)
      const room = locationOf(member.id)
      let pos: Point
      if (room === null) {
        pos = { x: outBand.x + 56 + outIndex * outStep, y: outBand.y + outBand.h / 2 }
        outIndex += 1
      } else {
        const center = layout.centerOf(room) ?? { x: outBand.x, y: outBand.y }
        const index = memberIds.filter((id) => locationOf(id) === room).indexOf(member.id)
        const count = roomCounts.get(room) ?? 1
        const offset = ringOffset(index < 0 ? 0 : index, count, 20)
        pos = { x: center.x + offset.x, y: center.y + offset.y }
      }
      return {
        memberId: member.id,
        color: memberColorVar(member.id, memberIds),
        initial: memberInitial(member.id),
        room,
        pos,
        isOut: room === null,
        sleeping:
          segment !== undefined &&
          categorizeActivity(segment.activity, segment.location) === "sleep",
      }
    })

    const litRooms = appliances
      .filter((pose) => pose.state === "active" && isLitLabel(pose.label))
      .map((pose) => pose.room)

    const profile = replay.total_watts
    const safeMinute = Math.min(Math.max(0, profile.length - 1), Math.max(0, minute))

    return {
      minute,
      house: replay.house,
      householdType: household.household_type,
      layout,
      rooms: roomPoses,
      characters,
      appliances,
      lighting: lightingFor(
        minute,
        roomPoses.filter((item) => item.occupants.length > 0).map((item) => item.room),
        litRooms,
      ),
      outMembers: characters.filter((item) => item.isOut).map((item) => item.memberId),
      totalWatts: profile[safeMinute] ?? 0,
      maxWatts: profile.reduce((max, value) => Math.max(max, value), 0) || 1,
    }
  }, [replay, layout, minute])
}
