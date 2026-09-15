import { SCENE_PADDING } from "./types.ts"
import type {
  BuildLayout,
  Point,
  RoomInput,
  RoomLayout,
  RoomRect,
  SceneSize,
} from "./types.ts"

const EPSILON = 1e-6

interface WeightedRoom {
  index: number
  weight: number
}

interface Box {
  x: number
  y: number
  w: number
  h: number
}

interface Neighbor {
  room: string
  door: Point
}

const validSize = (size: number | null | undefined): number | null =>
  typeof size === "number" && Number.isFinite(size) && size > 0 ? size : null

const normalizeWeights = (rooms: RoomInput[]): number[] => {
  const valid: number[] = []
  for (const room of rooms) {
    const size = validSize(room.size)
    if (size !== null) valid.push(size)
  }
  const fallback =
    valid.length > 0 ? valid.reduce((sum, value) => sum + value, 0) / valid.length : 1
  return rooms.map((room) => validSize(room.size) ?? fallback)
}

const partition = (items: WeightedRoom[], box: Box, out: Box[]): void => {
  const first = items[0]
  if (first === undefined) return
  if (items.length === 1) {
    out[first.index] = box
    return
  }
  const total = items.reduce((sum, item) => sum + item.weight, 0)
  const half = total / 2
  let splitAt = 1
  let best = Number.POSITIVE_INFINITY
  let cumulative = 0
  for (let i = 0; i < items.length - 1; i += 1) {
    cumulative += items[i]?.weight ?? 0
    const diff = Math.abs(cumulative - half)
    if (diff < best) {
      best = diff
      splitAt = i + 1
    }
  }
  const head = items.slice(0, splitAt)
  const tail = items.slice(splitAt)
  const headWeight = head.reduce((sum, item) => sum + item.weight, 0)
  const ratio = total > 0 ? headWeight / total : head.length / items.length
  if (box.w >= box.h) {
    const headWidth = box.w * ratio
    partition(head, { x: box.x, y: box.y, w: headWidth, h: box.h }, out)
    partition(tail, { x: box.x + headWidth, y: box.y, w: box.w - headWidth, h: box.h }, out)
    return
  }
  const headHeight = box.h * ratio
  partition(head, { x: box.x, y: box.y, w: box.w, h: headHeight }, out)
  partition(tail, { x: box.x, y: box.y + headHeight, w: box.w, h: box.h - headHeight }, out)
}

const sharedDoor = (a: RoomRect, b: RoomRect): Point | null => {
  const top = Math.max(a.y, b.y)
  const bottom = Math.min(a.y + a.h, b.y + b.h)
  const left = Math.max(a.x, b.x)
  const right = Math.min(a.x + a.w, b.x + b.w)
  if (bottom - top > EPSILON) {
    if (Math.abs(a.x + a.w - b.x) <= EPSILON) {
      return { x: a.x + a.w, y: (top + bottom) / 2 }
    }
    if (Math.abs(b.x + b.w - a.x) <= EPSILON) {
      return { x: b.x + b.w, y: (top + bottom) / 2 }
    }
  }
  if (right - left > EPSILON) {
    if (Math.abs(a.y + a.h - b.y) <= EPSILON) {
      return { x: (left + right) / 2, y: a.y + a.h }
    }
    if (Math.abs(b.y + b.h - a.y) <= EPSILON) {
      return { x: (left + right) / 2, y: b.y + b.h }
    }
  }
  return null
}

const doorKey = (a: string, b: string): string => `${a}\u0000${b}`

export const buildLayout: BuildLayout = (
  rooms: RoomInput[],
  size: SceneSize,
): RoomLayout => {
  const width = size.width
  const height = size.height
  const box: Box = {
    x: SCENE_PADDING,
    y: SCENE_PADDING,
    w: Math.max(0, width - SCENE_PADDING * 2),
    h: Math.max(0, height - SCENE_PADDING * 2),
  }

  const weights = normalizeWeights(rooms)
  const order: WeightedRoom[] = rooms.map((_room, index) => ({
    index,
    weight: weights[index] ?? 0,
  }))
  order.sort((a, b) => b.weight - a.weight || a.index - b.index)

  const boxes: Box[] = new Array<Box>(rooms.length)
  partition(order, box, boxes)

  const rects: RoomRect[] = rooms.map((room, index) => {
    const placed = boxes[index] ?? { x: box.x, y: box.y, w: 0, h: 0 }
    return { room: room.name, x: placed.x, y: placed.y, w: placed.w, h: placed.h }
  })

  const rectByName = new Map<string, RoomRect>()
  const centerByName = new Map<string, Point>()
  for (const rect of rects) {
    if (!rectByName.has(rect.room)) rectByName.set(rect.room, rect)
    if (!centerByName.has(rect.room)) {
      centerByName.set(rect.room, { x: rect.x + rect.w / 2, y: rect.y + rect.h / 2 })
    }
  }

  const graph = new Map<string, Neighbor[]>()
  for (const rect of rects) {
    if (!graph.has(rect.room)) graph.set(rect.room, [])
  }
  const doors = new Map<string, Point>()
  for (let i = 0; i < rects.length; i += 1) {
    for (let j = i + 1; j < rects.length; j += 1) {
      const a = rects[i]
      const b = rects[j]
      if (a === undefined || b === undefined) continue
      const door = sharedDoor(a, b)
      if (door === null) continue
      doors.set(doorKey(a.room, b.room), door)
      doors.set(doorKey(b.room, a.room), door)
      graph.get(a.room)?.push({ room: b.room, door })
      graph.get(b.room)?.push({ room: a.room, door })
    }
  }

  const pathBetween = (from: string, to: string): Point[] => {
    const start = centerByName.get(from)
    const end = centerByName.get(to)
    if (start === undefined || end === undefined) {
      return [start ?? { x: 0, y: 0 }, end ?? { x: 0, y: 0 }]
    }
    const queue: string[] = [from]
    const seen = new Set<string>([from])
    const previous = new Map<string, string>()
    let reached = from === to
    while (!reached && queue.length > 0) {
      const current = queue.shift()
      if (current === undefined) break
      for (const neighbor of graph.get(current) ?? []) {
        if (seen.has(neighbor.room)) continue
        seen.add(neighbor.room)
        previous.set(neighbor.room, current)
        if (neighbor.room === to) {
          reached = true
          break
        }
        queue.push(neighbor.room)
      }
    }
    if (!reached) return [start, end]
    const chain: string[] = [to]
    let cursor = to
    while (cursor !== from) {
      const parent = previous.get(cursor)
      if (parent === undefined) return [start, end]
      chain.push(parent)
      cursor = parent
    }
    chain.reverse()
    const points: Point[] = [start]
    for (let i = 0; i + 1 < chain.length; i += 1) {
      const a = chain[i]
      const b = chain[i + 1]
      if (a === undefined || b === undefined) continue
      const door = doors.get(doorKey(a, b))
      if (door !== undefined) points.push(door)
    }
    points.push(end)
    return points
  }

  return {
    rects,
    width,
    height,
    rectOf: (room: string): RoomRect | undefined => rectByName.get(room),
    centerOf: (room: string): Point | undefined => centerByName.get(room),
    pathBetween,
  }
}
