import { buildLayout } from "./layout.ts"
import { SCENE_PADDING } from "./types.ts"
import type { Point, RoomInput, RoomLayout, RoomRect, SceneSize } from "./types.ts"

declare const process: { exitCode: number | undefined }

let passed = 0
let failed = 0

const check = (label: string, ok: boolean, detail = ""): void => {
  if (ok) {
    passed += 1
    console.log(`PASS  ${label}`)
    return
  }
  failed += 1
  console.log(`FAIL  ${label}${detail.length > 0 ? ` :: ${detail}` : ""}`)
}

const SCENE: SceneSize = { width: 960, height: 640 }
const NARROW_SCENE: SceneSize = { width: 900, height: 600 }

const HOUSE_838587_0001: RoomInput[] = [
  { name: "Bedroom 1", size: 9 },
  { name: "Bedroom 2", size: 10 },
  { name: "Bedroom 3", size: 11 },
  { name: "Bedroom 4", size: 12 },
  { name: "Kitchen", size: 15 },
  { name: "Bathroom", size: 6 },
  { name: "Living Room", size: 20 },
]

const HOUSE_143345_0003: RoomInput[] = [
  { name: "Living Room", size: 20 },
  { name: "Kitchen", size: 15 },
  { name: "Bathroom", size: 6 },
  { name: "Dining Room", size: 12 },
  { name: "Study", size: 10 },
  { name: "Laundry", size: 5 },
  { name: "Bedroom 1", size: 12 },
  { name: "Bedroom 2", size: 11 },
  { name: "Bedroom 3", size: 10 },
  { name: "Garage", size: 18 },
]

const THREE_ROOMS: RoomInput[] = [
  { name: "Living Room", size: 20 },
  { name: "Kitchen", size: 15 },
  { name: "Bathroom", size: 6 },
]

const MIXED_SIZES: RoomInput[] = [
  { name: "Living Room", size: 20 },
  { name: "Kitchen", size: null },
  { name: "Bathroom", size: 0 },
  { name: "Study", size: -4 },
  { name: "Hallway" },
]

const areaOf = (rect: RoomRect): number => rect.w * rect.h

const totalArea = (layout: RoomLayout): number =>
  layout.rects.reduce((sum, rect) => sum + areaOf(rect), 0)

const contentArea = (layout: RoomLayout): number =>
  Math.max(0, layout.width - SCENE_PADDING * 2) * Math.max(0, layout.height - SCENE_PADDING * 2)

const overlapArea = (a: RoomRect, b: RoomRect): number => {
  const w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)
  const h = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y)
  return w > 0 && h > 0 ? w * h : 0
}

const maxOverlap = (layout: RoomLayout): number => {
  let worst = 0
  for (let i = 0; i < layout.rects.length; i += 1) {
    for (let j = i + 1; j < layout.rects.length; j += 1) {
      const a = layout.rects[i]
      const b = layout.rects[j]
      if (a === undefined || b === undefined) continue
      worst = Math.max(worst, overlapArea(a, b))
    }
  }
  return worst
}

const signature = (layout: RoomLayout): string => JSON.stringify(layout.rects)

const pointNear = (a: Point, b: Point, tolerance = 1e-6): boolean =>
  Math.abs(a.x - b.x) <= tolerance && Math.abs(a.y - b.y) <= tolerance

const assertCommon = (label: string, rooms: RoomInput[], size: SceneSize): RoomLayout => {
  const layout = buildLayout(rooms, size)
  const repeat = buildLayout(rooms, size)
  check(`${label}: deterministic`, signature(layout) === signature(repeat))

  const worst = maxOverlap(layout)
  check(`${label}: no overlap`, worst <= 1e-6, `maxOverlap=${worst}`)

  const actual = totalArea(layout)
  const expected = contentArea(layout)
  const tiled = expected <= 0 ? actual <= 1e-9 : Math.abs(actual - expected) <= expected * 0.005
  check(`${label}: tiles content box`, tiled, `area=${actual} box=${expected}`)

  const inside = layout.rects.every(
    (rect) =>
      rect.w > 0 &&
      rect.h > 0 &&
      rect.x >= SCENE_PADDING - 1e-6 &&
      rect.y >= SCENE_PADDING - 1e-6 &&
      rect.x + rect.w <= layout.width - SCENE_PADDING + 1e-6 &&
      rect.y + rect.h <= layout.height - SCENE_PADDING + 1e-6,
  )
  check(`${label}: rects inside padding`, inside)

  const lookups = layout.rects.every((rect) => {
    const center = layout.centerOf(rect.room)
    const looked = layout.rectOf(rect.room)
    return (
      center !== undefined &&
      looked !== undefined &&
      pointNear(center, { x: rect.x + rect.w / 2, y: rect.y + rect.h / 2 }) &&
      looked.x === rect.x &&
      looked.y === rect.y &&
      looked.w === rect.w &&
      looked.h === rect.h
    )
  })
  check(`${label}: rectOf/centerOf lookups`, lookups)

  let pathsOk = true
  let pathDetail = ""
  for (const from of layout.rects) {
    for (const to of layout.rects) {
      const path = layout.pathBetween(from.room, to.room)
      const start = layout.centerOf(from.room)
      const end = layout.centerOf(to.room)
      const head = path[0]
      const tail = path[path.length - 1]
      if (
        path.length < 2 ||
        start === undefined ||
        end === undefined ||
        head === undefined ||
        tail === undefined ||
        !pointNear(head, start) ||
        !pointNear(tail, end)
      ) {
        pathsOk = false
        pathDetail = `${from.room} -> ${to.room} length=${path.length}`
        break
      }
    }
    if (!pathsOk) break
  }
  check(`${label}: every pair has a path`, pathsOk, pathDetail)

  return layout
}

console.log("layout selftest")

const empty = buildLayout([], SCENE)
check("empty input: no rects", empty.rects.length === 0)
check("empty input: unknown rooms fall back", empty.pathBetween("a", "b").length === 2)

const single = buildLayout([{ name: "Studio", size: 10 }], NARROW_SCENE)
const singleRect = single.rectOf("Studio")
check(
  "single room: fills content box",
  singleRect !== undefined &&
    singleRect.x === SCENE_PADDING &&
    singleRect.y === SCENE_PADDING &&
    singleRect.w === NARROW_SCENE.width - SCENE_PADDING * 2 &&
    singleRect.h === NARROW_SCENE.height - SCENE_PADDING * 2,
)

const three = assertCommon("three-room", THREE_ROOMS, NARROW_SCENE)
const threeTotalSize = THREE_ROOMS.reduce((sum, room) => sum + (room.size ?? 0), 0)
const threeTotalArea = totalArea(three)
for (const room of THREE_ROOMS) {
  const rect = three.rectOf(room.name)
  const expectedRatio = (room.size ?? 0) / threeTotalSize
  const actualRatio = rect === undefined ? 0 : areaOf(rect) / threeTotalArea
  check(
    `three-room: area ratio ${room.name}`,
    Math.abs(actualRatio - expectedRatio) <= expectedRatio * 0.05,
    `actual=${actualRatio} expected=${expectedRatio}`,
  )
}

const fixtureA = assertCommon("world_838587/house_0001", HOUSE_838587_0001, SCENE)
const fixtureB = assertCommon("world_143345/house_0003", HOUSE_143345_0003, SCENE)
check("world_838587/house_0001: 7 rooms placed", fixtureA.rects.length === 7)
check("world_143345/house_0003: 10 rooms placed", fixtureB.rects.length === 10)

const mixed = assertCommon("missing sizes", MIXED_SIZES, SCENE)
const fallbackAreas = MIXED_SIZES.filter(
  (room) => !(typeof room.size === "number" && room.size > 0),
).map((room) => {
  const rect = mixed.rectOf(room.name)
  return rect === undefined ? 0 : areaOf(rect)
})
const spread =
  fallbackAreas.length === 0 ? 0 : Math.max(...fallbackAreas) - Math.min(...fallbackAreas)
check(
  "missing sizes: invalid sizes share equal area",
  fallbackAreas.length === 4 && spread <= totalArea(mixed) * 1e-6,
  `spread=${spread}`,
)

const unknownPath = mixed.pathBetween("Attic", "Kitchen")
check("unknown room: fallback polyline", unknownPath.length === 2, `length=${unknownPath.length}`)

console.log(`\n${passed} passed, ${failed} failed`)
if (failed > 0) process.exitCode = 1
