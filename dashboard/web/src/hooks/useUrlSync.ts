import { useEffect } from "react"

import { useTimeStore } from "@/store/time"

const PARAM_ORDER = [
  "view",
  "world",
  "mode",
  "density",
  "step",
  "run",
  "date",
  "house",
  "policy",
  "minute",
] as const

/**
 * view / world / mode / density / step / run / date / house / policy / minute 双向绑定 URL，
 * 便于把某一时刻的研究现场（含当前工作区、模式与密度、构建步骤）作为链接分享出去。
 */
export function useUrlSync(): void {
  const view = useTimeStore((state) => state.view)
  const world = useTimeStore((state) => state.world)
  const mode = useTimeStore((state) => state.mode)
  const density = useTimeStore((state) => state.density)
  const step = useTimeStore((state) => state.step)
  const run = useTimeStore((state) => state.run)
  const date = useTimeStore((state) => state.date)
  const house = useTimeStore((state) => state.house)
  const policy = useTimeStore((state) => state.policy)
  const minute = useTimeStore((state) => state.minute)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const values: Record<(typeof PARAM_ORDER)[number], string> = {
      view,
      world,
      mode,
      density,
      step,
      run,
      date,
      house,
      policy,
      minute: String(minute),
    }
    for (const key of PARAM_ORDER) {
      const value = values[key]
      if (value.length > 0) params.set(key, value)
      else params.delete(key)
    }
    const query = params.toString()
    const next = `${window.location.pathname}${query.length > 0 ? `?${query}` : ""}`
    const current = `${window.location.pathname}${window.location.search}`
    if (next !== current) window.history.replaceState(null, "", next)
  }, [view, world, mode, density, step, run, date, house, policy, minute])
}
