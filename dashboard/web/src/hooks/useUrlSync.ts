import { useEffect } from "react"

import { useTimeStore } from "@/store/time"

const PARAM_ORDER = [
  "view",
  "world",
  "tab",
  "run",
  "date",
  "block",
  "house",
  "indoor",
  "policy",
  "minute",
] as const

export function useUrlSync(): void {
  const view = useTimeStore((state) => state.view)
  const world = useTimeStore((state) => state.world)
  const tab = useTimeStore((state) => state.tab)
  const run = useTimeStore((state) => state.run)
  const date = useTimeStore((state) => state.date)
  const block = useTimeStore((state) => state.block)
  const house = useTimeStore((state) => state.house)
  const indoor = useTimeStore((state) => state.indoor)
  const policy = useTimeStore((state) => state.policy)
  const minute = useTimeStore((state) => state.minute)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const values: Record<(typeof PARAM_ORDER)[number], string> = {
      view,
      world,
      tab,
      run,
      date,
      block,
      house,
      indoor: indoor ? "1" : "",
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
  }, [view, world, tab, run, date, block, house, indoor, policy, minute])
}
