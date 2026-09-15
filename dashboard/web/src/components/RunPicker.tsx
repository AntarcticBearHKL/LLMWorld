import { useEffect, useState } from "react"

import { CalendarDays, Database, Home, Search, Shield } from "lucide-react"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { useRunMeta, useRuns } from "@/hooks/useDayData"
import { USE_MOCK } from "@/api/client"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

const MAX_RUN_ITEMS = 60

function Field({
  icon,
  label,
  children,
  className,
}: {
  icon: React.ReactNode
  label: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <label className={cn("flex min-w-0 flex-col gap-1", className)}>
      <span className="label-micro flex items-center gap-1.5 whitespace-nowrap">
        <span className="text-fg-subtle" aria-hidden>
          {icon}
        </span>
        {label}
      </span>
      {children}
    </label>
  )
}

const triggerClass =
  "h-8 w-full min-w-[136px] rounded-md border-border-strong bg-surface-2 px-2.5 text-[12px] font-medium text-fg hover:bg-surface-3 focus-visible:border-brand"

export function RunPicker() {
  const [query, setQuery] = useState("")
  const [keyword, setKeyword] = useState("")

  useEffect(() => {
    const timer = window.setTimeout(() => setKeyword(query.trim()), 250)
    return () => window.clearTimeout(timer)
  }, [query])

  const runsQuery = useRuns(keyword, MAX_RUN_ITEMS)
  const run = useTimeStore((state) => state.run)
  const date = useTimeStore((state) => state.date)
  const house = useTimeStore((state) => state.house)
  const policy = useTimeStore((state) => state.policy)
  const setSelection = useTimeStore((state) => state.setSelection)
  const metaQuery = useRunMeta(run)

  const runs = runsQuery.data ?? []
  const dates = metaQuery.data?.dates ?? []
  const houses = metaQuery.data?.houses ?? []
  const policyOptions = ["baseline", ...(metaQuery.data?.policies ?? [])]

  const onRunChange = (nextRun: string) => {
    setSelection({ run: nextRun, date: "", house: "" })
  }

  return (
    <div className="flex flex-wrap items-end gap-2.5">
      <Field icon={<Search className="size-3" />} label="搜索" className="min-w-[132px]">
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="关键词过滤"
          aria-label="关键词过滤运行"
          className="h-8 w-full min-w-[132px] rounded-md border-border-strong bg-surface-2 px-2.5 text-[12px]"
        />
      </Field>

      <Field icon={<Database className="size-3" />} label="运行" className="min-w-[168px]">
        <Select value={run} onValueChange={onRunChange} disabled={runs.length === 0}>
          <SelectTrigger className={triggerClass} aria-label="选择运行">
            <SelectValue placeholder={runsQuery.isPending ? "载入中…" : "选择运行"} />
          </SelectTrigger>
          <SelectContent>
            {runs.map((item) => (
              <SelectItem key={item.run} value={item.run}>
                <span className="num">{item.run}</span>
                <span className="ml-2 text-[11px] text-fg-subtle">
                  {item.house_count} 户 · {item.date_count} 天
                </span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </Field>

      {runs.length >= MAX_RUN_ITEMS ? (
        <span className="label-micro mb-2 whitespace-nowrap text-energy">
          仅列前 {MAX_RUN_ITEMS} 个，请用搜索缩小范围
        </span>
      ) : null}

      <Field icon={<CalendarDays className="size-3" />} label="日期" className="min-w-[136px]">
        <Select
          value={date}
          onValueChange={(next) => setSelection({ date: next })}
          disabled={dates.length === 0}
        >
          <SelectTrigger className={triggerClass} aria-label="选择日期">
            <SelectValue placeholder="选择日期" />
          </SelectTrigger>
          <SelectContent>
            {dates.map((item) => (
              <SelectItem key={item} value={item}>
                <span className="num">{item}</span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </Field>

      <Field icon={<Home className="size-3" />} label="住户" className="min-w-[136px]">
        <Select
          value={house}
          onValueChange={(next) => setSelection({ house: next })}
          disabled={houses.length === 0}
        >
          <SelectTrigger className={triggerClass} aria-label="选择住户">
            <SelectValue placeholder="选择住户" />
          </SelectTrigger>
          <SelectContent>
            {houses.map((item) => (
              <SelectItem key={item} value={item}>
                <span className="num">{item}</span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </Field>

      <Field icon={<Shield className="size-3" />} label="策略" className="min-w-[128px]">
        <Select value={policy} onValueChange={(next) => setSelection({ policy: next })}>
          <SelectTrigger className={triggerClass} aria-label="选择策略">
            <SelectValue placeholder="选择策略" />
          </SelectTrigger>
          <SelectContent>
            {policyOptions.map((item) => (
              <SelectItem key={item} value={item}>
                {item === "baseline" ? "基线策略" : item}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </Field>

      {USE_MOCK ? (
        <span
          className="mb-1.5 rounded-sm border border-energy/40 bg-energy-soft px-1.5 py-0.5 text-[10px] font-semibold tracking-[0.1em] text-energy uppercase"
          title="VITE_USE_MOCK=1：数据来自 src/mocks 夹具，不是真实后端"
        >
          mock
        </span>
      ) : null}
    </div>
  )
}
