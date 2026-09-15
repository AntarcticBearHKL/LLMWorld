import { ChevronRight, Users } from "lucide-react"

import { useSnapshot } from "@/hooks/useDayData"
import { memberColorVar, memberInitial } from "@/lib/members"
import { formatHHMM, formatWatts } from "@/lib/time"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

interface MultiHouseGridProps {
  onOpen: (house: string) => void
}

/**
 * 住户网格：一张卡片 = 一个家庭。显示该户此刻每个成员在做什么、用电多少。
 * 点击卡片进入该户详情（成员卡片 + 平面图 + 时间轴）。
 */
export function MultiHouseGrid({ onOpen }: MultiHouseGridProps) {
  const minute = useTimeStore((state) => state.minute)
  const house = useTimeStore((state) => state.house)
  const snapshotQuery = useSnapshot()
  const snapshot = snapshotQuery.data

  if (snapshotQuery.isPending) {
    return <p className="p-6 text-[11px] text-fg-subtle">载入住户快照…</p>
  }

  if (snapshot === undefined || snapshot.houses.length === 0) {
    return <p className="p-6 text-[11px] text-fg-subtle">该时刻没有可用的住户数据。</p>
  }

  const peak = snapshot.houses.reduce((max, item) => Math.max(max, item.total_watts), 0) || 1

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-baseline gap-3 border-b border-border px-4 py-2.5">
        <span className="text-[13px] font-semibold text-fg">住户网格</span>
        <span className="num text-[11px] text-fg-subtle">
          {snapshot.houses.length} 户 · {formatHHMM(minute)}
        </span>
        <span className="label-latin ml-auto">点击任一住户查看成员</span>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-1 content-start gap-3 overflow-y-auto p-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
        {snapshot.houses.map((item) => {
          const memberIds = item.people.map((person) => person.member)
          const running = item.powered.filter((appliance) => appliance.watts > 0)
          const isCurrent = item.house === house
          return (
            <button
              key={item.house}
              type="button"
              onClick={() => onOpen(item.house)}
              className={cn(
                "enter flex min-h-[236px] flex-col gap-2.5 rounded-lg border bg-surface p-3.5 text-left transition-colors",
                isCurrent
                  ? "border-brand/50 bg-brand-soft"
                  : "border-border hover:border-brand/40 hover:bg-surface-2",
              )}
            >
              <div className="flex items-center gap-2">
                <span className="num text-[13px] font-semibold text-fg">{item.house}</span>
                <ChevronRight className="size-3.5 shrink-0 text-fg-subtle" aria-hidden />
                <span className="num ml-auto text-[15px] font-medium text-energy">
                  {formatWatts(item.total_watts)}
                </span>
              </div>

              <div className="flex items-baseline gap-2">
                <span className="label-micro min-w-0 flex-1 truncate">{item.household_type}</span>
                <span className="label-micro flex shrink-0 items-center gap-1">
                  <Users className="size-3" aria-hidden />
                  {item.people.length}
                </span>
              </div>

              <div className="h-1 w-full overflow-hidden rounded-full bg-surface-3">
                <div
                  className="h-full rounded-full bg-energy"
                  style={{ width: `${Math.round((item.total_watts / peak) * 100)}%` }}
                />
              </div>

              <ul className="flex flex-col gap-1.5">
                {item.people.slice(0, 5).map((person) => (
                  <li key={person.member} className="flex items-start gap-1.5">
                    <span
                      className="num mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full text-[8px] font-semibold"
                      style={{
                        backgroundColor: memberColorVar(person.member, memberIds),
                        color: "var(--bg)",
                      }}
                    >
                      {memberInitial(person.member)}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="num text-[10px] text-fg">{person.member}</span>
                      <span className="ml-1.5 text-[10px] text-fg-subtle">{person.location}</span>
                      <span className="mt-px line-clamp-2 block text-[10px] leading-snug text-fg-muted">
                        {person.activity}
                      </span>
                    </span>
                  </li>
                ))}
                {item.people.length > 5 ? (
                  <li className="num text-[10px] text-fg-subtle">
                    还有 {item.people.length - 5} 名成员
                  </li>
                ) : null}
              </ul>

              <div className="mt-auto flex flex-wrap items-center gap-1 border-t border-border pt-2">
                {running.length === 0 ? (
                  <span className="text-[10px] text-fg-subtle">没有设备在用电</span>
                ) : (
                  <>
                    <span className="label-micro shrink-0">用电 {running.length}</span>
                    {running.slice(0, 3).map((appliance) => (
                      <span
                        key={appliance.unique_id}
                        className="num truncate rounded-sm border border-border-strong px-1.5 py-px text-[9px] text-fg-muted"
                      >
                        {appliance.name}
                      </span>
                    ))}
                    {running.length > 3 ? (
                      <span className="num text-[9px] text-fg-subtle">+{running.length - 3}</span>
                    ) : null}
                  </>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
