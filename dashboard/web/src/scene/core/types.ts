export interface Point {
  x: number
  y: number
}

export interface SceneSize {
  width: number
  height: number
}

export interface RoomInput {
  name: string
  size?: number | null
}

export interface RoomRect {
  room: string
  x: number
  y: number
  w: number
  h: number
}

export interface RoomLayout {
  rects: RoomRect[]
  width: number
  height: number
  rectOf(room: string): RoomRect | undefined
  centerOf(room: string): Point | undefined
  pathBetween(from: string, to: string): Point[]
}

export type BuildLayout = (rooms: RoomInput[], size: SceneSize) => RoomLayout

export type ApplianceVisualState = "active" | "baseload" | "standby" | "off"

export interface CharacterPose {
  memberId: string
  color: string
  initial: string
  room: string | null
  pos: Point
  isOut: boolean
  sleeping: boolean
  selected: boolean
}

export interface AppliancePose {
  uniqueId: string
  label: string
  room: string
  pos: Point
  watts: number
  state: ApplianceVisualState
  cycling: boolean
}

export interface RoomPose {
  room: string
  rect: RoomRect
  watts: number
  occupants: string[]
}

export interface LightingState {
  night: number
  tint: string
  peakWindow: boolean
  lampRooms: string[]
}

export interface SceneState {
  minute: number
  house: string
  householdType: string
  layout: RoomLayout
  rooms: RoomPose[]
  characters: CharacterPose[]
  appliances: AppliancePose[]
  lighting: LightingState
  outMembers: string[]
  totalWatts: number
  maxWatts: number
}

export interface TownHouse {
  house: string
  householdType: string
  memberCount: number
  totalWatts: number
  maxWatts: number
  homeCount: number
  outMembers: string[]
  profile: number[]
  x: number
  y: number
  w: number
  h: number
}

export interface TownLayout {
  houses: TownHouse[]
  width: number
  height: number
}

export const SCENE_PADDING = 28
export const ROOM_GAP = 4
export const CHARACTER_RADIUS = 12
export const APPLIANCE_RADIUS = 5
export const APPLIANCE_SLOTS_PER_ROOM = 6
export const TOWN_HOUSE_WIDTH = 190
export const TOWN_HOUSE_HEIGHT = 140
export const TOWN_GAP_X = 56
export const TOWN_GAP_Y = 72

export const PEAK_WINDOW_START = 1020
export const PEAK_WINDOW_END = 1200
