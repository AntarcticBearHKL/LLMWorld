import { useEffect } from "react"

import { useDefaultRun, useRunMeta } from "@/hooks/useDayData"
import { useTimeStore } from "@/store/time"

/**
 * URL 里的选择可能指向不存在的数据，或首次打开时完全没有参数。
 * 这里在数据到达后把选择收敛到合法值。
 */
export function useBootstrapSelection(): void {
  const defaultQuery = useDefaultRun()
  const run = useTimeStore((state) => state.run)
  const setSelection = useTimeStore((state) => state.setSelection)
  const metaQuery = useRunMeta(run)

  useEffect(() => {
    const fallback = defaultQuery.data
    if (fallback === undefined) return
    if (run.length > 0 && !metaQuery.isError) return
    setSelection({ run: fallback.run, date: "", house: "" })
  }, [defaultQuery.data, run, metaQuery.isError, setSelection])

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
