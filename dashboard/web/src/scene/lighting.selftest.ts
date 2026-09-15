import { interpolateTint, lightingFor, nightLevel } from './lighting.ts'
import { PEAK_WINDOW_END, PEAK_WINDOW_START } from './types.ts'

let passed = 0
let failed = 0

function check(label: string, ok: boolean): void {
  if (ok) {
    passed += 1
    console.log(`PASS ${label}`)
  } else {
    failed += 1
    console.log(`FAIL ${label}`)
  }
}

interface Rgba {
  r: number
  g: number
  b: number
  a: number
}

const RGBA_PATTERN = /^rgba\((\d+), (\d+), (\d+), ([0-9]+(?:\.[0-9]+)?)\)$/

function parseRgba(value: string): Rgba | null {
  const match = RGBA_PATTERN.exec(value)
  if (match === null) return null
  const r = Number(match[1])
  const g = Number(match[2])
  const b = Number(match[3])
  const a = Number(match[4])
  if (!Number.isFinite(r) || !Number.isFinite(g) || !Number.isFinite(b) || !Number.isFinite(a)) {
    return null
  }
  return { r, g, b, a }
}

function sameMembers(a: readonly string[], b: readonly string[]): boolean {
  if (a.length !== b.length) return false
  const set = new Set(a)
  return b.every((item) => set.has(item))
}

check('PEAK_WINDOW_START is 1020', PEAK_WINDOW_START === 1020)
check('PEAK_WINDOW_END is 1200', PEAK_WINDOW_END === 1200)

check('night is 0 at minute 720 (noon)', lightingFor(720, []).night === 0)
check('night is 1 at minute 60 (deep night)', lightingFor(60, []).night === 1)
check('night is 1 at minute 1380 (deep night)', lightingFor(1380, []).night === 1)

let duskMonotone = true
let previousDusk = nightLevel(1080)
for (let m = 1081; m <= 1320; m += 1) {
  const current = nightLevel(m)
  if (current < previousDusk) duskMonotone = false
  previousDusk = current
}
check('night is non-decreasing across 1080..1320 (dusk ramp)', duskMonotone)

let dawnMonotone = true
let previousDawn = nightLevel(240)
for (let m = 241; m <= 420; m += 1) {
  const current = nightLevel(m)
  if (current > previousDawn) dawnMonotone = false
  previousDawn = current
}
check('night is non-increasing across 240..420 (dawn ramp)', dawnMonotone)

let maxStep = 0
let maxStepMinute = 0
for (let m = 0; m < 1440; m += 1) {
  const step = Math.abs(nightLevel((m + 1) % 1440) - nightLevel(m))
  if (step > maxStep) {
    maxStep = step
    maxStepMinute = m
  }
}
check(`night max 1-minute step ${maxStep.toFixed(5)} at minute ${maxStepMinute} is < 0.01`, maxStep < 0.01)

let tintProblem = ''
for (let m = 0; m < 1440; m += 1) {
  const tint = lightingFor(m, []).tint
  const rgba = parseRgba(tint)
  const inRange =
    rgba !== null &&
    rgba.r >= 0 &&
    rgba.r <= 255 &&
    rgba.g >= 0 &&
    rgba.g <= 255 &&
    rgba.b >= 0 &&
    rgba.b <= 255 &&
    rgba.a >= 0 &&
    rgba.a <= 1
  if (!inRange) {
    tintProblem = `minute ${m}: ${tint}`
    break
  }
}
check(`tint is valid rgba(...) with alpha in 0..1 for every minute${tintProblem === '' ? '' : ` (bad: ${tintProblem})`}`, tintProblem === '')

let peakProblem = -1
for (let m = 0; m < 1440; m += 1) {
  const expected = m >= PEAK_WINDOW_START && m < PEAK_WINDOW_END
  if (lightingFor(m, []).peakWindow !== expected) {
    peakProblem = m
    break
  }
}
check(`peakWindow is true exactly for ${PEAK_WINDOW_START}..${PEAK_WINDOW_END - 1}${peakProblem < 0 ? '' : ` (bad at ${peakProblem})`}`, peakProblem < 0)

const occupied = ['kitchen', 'living', 'kitchen']
const lit = ['living', 'bedroom']

const noon = lightingFor(720, occupied, lit)
check('lampRooms is empty at noon', noon.lampRooms.length === 0)

const deepNight = lightingFor(1320, occupied, lit)
check(
  'lampRooms at night equals the deduped union of occupied and lit',
  sameMembers(deepNight.lampRooms, ['kitchen', 'living', 'bedroom']),
)
check('lampRooms contains no duplicates', new Set(deepNight.lampRooms).size === deepNight.lampRooms.length)
check('inputs are not mutated', occupied.length === 3 && occupied[2] === 'kitchen' && lit.length === 2)

const nightNoLit = lightingFor(1320, occupied)
check('lampRooms with litRooms omitted is the deduped occupied set', sameMembers(nightNoLit.lampRooms, ['kitchen', 'living']))

const deterministicA = lightingFor(1140, occupied, lit)
const deterministicB = lightingFor(1140, occupied, lit)
check('determinism: identical inputs produce identical output', JSON.stringify(deterministicA) === JSON.stringify(deterministicB))

const duskRgba = parseRgba(interpolateTint(nightLevel(1140), 1140))
const nightRgba = parseRgba(interpolateTint(nightLevel(60), 60))
check('dusk tint is warm (red channel exceeds blue)', duskRgba !== null && duskRgba.r > duskRgba.b)
check('night tint is cool (blue channel exceeds red)', nightRgba !== null && nightRgba.b > nightRgba.r)

console.log(`\n${passed} passed, ${failed} failed`)
if (failed > 0) {
  console.log('SELFTEST FAILED')
  throw new Error(`${failed} assertion(s) failed`)
}
console.log('SELFTEST PASSED')
