import { useEffect } from "react"

import type { RunInfo } from "@/api/types"
import { useRunMeta, useRuns } from "@/hooks/useDayData"
import { useTimeStore } from "@/store/time"

const isPlayable = (item: RunInfo): boolean =>
  item.has_baseline && item.dates.length > 0 && item.houses.length > 0

const pickDefaultRun = (runs: RunInfo[]): RunInfo | undefined => {
  const withBaseline = runs.filter(isPlayable)
  const pool =
    withBaseline.length > 0
      ? withBaseline
      : runs.filter((item) => item.dates.length > 0 && item.houses.length > 0)
  return [...pool].sort(
    (a, b) =>
      Number(b.has_analysis) - Number(a.has_analysis) ||
      b.member_count - a.member_count ||
      b.houses.length - a.houses.length ||
      b.dates.length - a.dates.length,
  )[0]
}

/**
 * URL 里的选择可能指向不存在的数据，或首次打开时完全没有参数。
 * 这里在数据到达后把选择收敛到合法值。
 */
export function useBootstrapSelection(): void {
  const runsQuery = useRuns()
  const run = useTimeStore((state) => state.run)
  const setSelection = useTimeStore((state) => state.setSelection)
  const metaQuery = useRunMeta(run)

  useEffect(() => {
    const runs = runsQuery.data
    if (runs === undefined || runs.length === 0) return
    const known = runs.some((item) => item.run === run)
    if (known) return
    const target = pickDefaultRun(runs)
    if (target === undefined) return
    setSelection({
      run: target.run,
      date: target.dates[0] ?? "",
      house: target.houses[0] ?? "",
    })
  }, [runsQuery.data, run, setSelection])

  useEffect(() => {
    const meta = metaQuery.data
    if (meta === undefined) return
    const state = useTimeStore.getState()
    const patch: { date?: string; house?: string } = {}
    if (!meta.dates.includes(state.date)) patch.date = meta.dates[0] ?? ""
    if (!meta.houses.includes(state.house)) patch.house = meta.houses[0] ?? ""
    if (patch.date !== undefined || patch.house !== undefined) setSelection(patch)
  }, [metaQuery.data, setSelection])
}
