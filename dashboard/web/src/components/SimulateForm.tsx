import { useState } from "react"

import { useQuery } from "@tanstack/react-query"
import { House, Play } from "lucide-react"

import { USE_MOCK, listWorlds } from "@/api/client"
import type { JobRequest } from "@/api/types"
import { JobSubmitBar } from "@/components/JobSubmitBar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { useRunMeta, useRuns } from "@/hooks/useDayData"

const FIELD_CLASS =
  "h-8 rounded-md border-border-strong bg-surface-2 px-2.5 text-[12px] text-fg focus-visible:border-brand"

const TRIGGER_CLASS =
  "h-8 w-full rounded-md border-border-strong bg-surface-2 px-2.5 text-[12px] text-fg hover:bg-surface-3"

const POLICIES: ReadonlyArray<{ value: string; label: string }> = [
  { value: "__none__", label: "不注入政策" },
  { value: "tou", label: "tou · 分时电价" },
  { value: "tou_soft", label: "tou_soft · 分时电价（软）" },
  { value: "cpp", label: "cpp · 尖峰电价" },
  { value: "cpp_soft", label: "cpp_soft · 尖峰电价（软）" },
  { value: "cpr", label: "cpr · 尖峰返利" },
  { value: "nudge", label: "nudge · 社会助推" },
  { value: "nudge_loss", label: "nudge_loss · 损失框架" },
  { value: "subsidy", label: "subsidy · 补贴" },
  { value: "peak_demand", label: "peak_demand · 需量电费" },
  { value: "night_setback", label: "night_setback · 夜间温控" },
  { value: "in_home_display", label: "in_home_display · 家庭显示" },
]

const EVENT_TEMPLATES = [
  "heatwave",
  "cold_snap",
  "storm",
  "price_hike",
  "energy_crisis",
  "ac_tax",
  "rebate",
  "blackout_risk",
  "solar_incentive",
  "lockdown",
  "holiday",
  "wfh",
  "transport_strike",
]

const todayIso = (): string => {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, "0")
  const day = String(now.getDate()).padStart(2, "0")
  return `${now.getFullYear()}-${month}-${day}`
}

const toLines = (text: string): string[] =>
  text
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

interface SimulateFormProps {
  lockedWorld?: string
}

export function SimulateForm({ lockedWorld = "" }: SimulateFormProps) {
  const worldsQuery = useQuery({ queryKey: ["worlds"], queryFn: listWorlds, staleTime: 300_000 })
  const runsQuery = useRuns()

  const [world, setWorld] = useState(lockedWorld)
  const [house, setHouse] = useState("__all__")
  const [member, setMember] = useState("")
  const [date, setDate] = useState(todayIso())
  const [days, setDays] = useState(1)
  const [policy, setPolicy] = useState("__none__")
  const [templates, setTemplates] = useState("")
  const [customEvents, setCustomEvents] = useState("")
  const [s4Only, setS4Only] = useState(false)
  const [costContext, setCostContext] = useState(false)
  const [naturalEv, setNaturalEv] = useState(false)
  const [peerNudge, setPeerNudge] = useState(false)
  const [workers, setWorkers] = useState(4)

  const locked = lockedWorld.length > 0
  const effectiveWorld = locked ? lockedWorld : world
  const metaQuery = useRunMeta(effectiveWorld)
  const worldOptions = (worldsQuery.data ?? []).map((item) => item.world_id)
  const runOptions = (runsQuery.data ?? []).map((item) => item.run)
  const options = [
    ...new Set([...(locked ? [lockedWorld] : []), ...worldOptions, ...runOptions]),
  ].sort()
  const houses = metaQuery.data?.houses ?? []

  const payload: JobRequest = {
    kind: "simulate",
    world: effectiveWorld.length > 0 ? effectiveWorld : null,
    house: house === "__all__" ? null : house,
    member: member.trim().length > 0 ? member.trim() : null,
    date,
    days,
    policy: policy === "__none__" ? null : policy,
    event_template: toLines(templates),
    event: toLines(customEvents),
    s4_only: s4Only,
    cost_context: costContext,
    natural_ev: naturalEv,
    peer_nudge: peerNudge,
    workers,
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <header className="flex items-start gap-2">
        <Play className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden />
        <div className="flex flex-col gap-1">
          <h2 className="text-[13px] font-semibold text-fg">逐户模拟</h2>
          <p className="text-[11px] text-fg-muted">
            对应 <span className="num">run.py --mode simulate</span>：可指定世界、住户、成员、日期区间、
            政策与事件，逐个住户逐天推进 s1 → s4。日期务必显式指定（默认今天）。
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <div className="flex flex-col gap-1.5">
          <Label className="label-micro">
            世界 / 运行{locked ? "（锁定为当前世界）" : ""}
          </Label>
          <Select
            value={effectiveWorld}
            onValueChange={(next) => {
              setWorld(next)
              setHouse("__all__")
            }}
            disabled={locked}
          >
            <SelectTrigger className={TRIGGER_CLASS} aria-label="选择世界">
              <SelectValue placeholder={worldsQuery.isPending ? "载入中…" : "选择世界"} />
            </SelectTrigger>
            <SelectContent>
              {options.map((item) => (
                <SelectItem key={item} value={item}>
                  <span className="num">{item}</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label className="label-micro">住户</Label>
          <Select value={house} onValueChange={setHouse} disabled={effectiveWorld.length === 0}>
            <SelectTrigger className={TRIGGER_CLASS} aria-label="选择住户">
              <SelectValue placeholder="选择住户" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">全部住户</SelectItem>
              {houses.map((item) => (
                <SelectItem key={item} value={item}>
                  <span className="num">{item}</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="sim-member" className="label-micro">
            成员（名称或序号，留空=全部）
          </Label>
          <Input
            id="sim-member"
            value={member}
            placeholder="Member 1 或 0"
            onChange={(event) => setMember(event.target.value)}
            className={FIELD_CLASS}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="sim-date" className="label-micro">
            起始日期
          </Label>
          <Input
            id="sim-date"
            type="date"
            value={date}
            onChange={(event) => setDate(event.target.value)}
            className={FIELD_CLASS}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="sim-days" className="label-micro">
            天数
          </Label>
          <Input
            id="sim-days"
            type="number"
            min={1}
            max={3}
            value={days}
            onChange={(event) => {
              const next = Number(event.target.value)
              setDays(Number.isFinite(next) ? Math.min(3, Math.max(1, Math.trunc(next))) : 1)
            }}
            className={FIELD_CLASS}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label className="label-micro">政策</Label>
          <Select value={policy} onValueChange={setPolicy}>
            <SelectTrigger className={TRIGGER_CLASS} aria-label="选择政策">
              <SelectValue placeholder="选择政策" />
            </SelectTrigger>
            <SelectContent>
              {POLICIES.map((item) => (
                <SelectItem key={item.value} value={item.value}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="sim-templates" className="label-micro">
            事件模板（每行 <span className="num">日期|模板</span>）
          </Label>
          <textarea
            id="sim-templates"
            rows={3}
            value={templates}
            placeholder={`${date}|heatwave`}
            onChange={(event) => setTemplates(event.target.value)}
            className="num rounded-md border border-border-strong bg-surface-2 px-2.5 py-1.5 text-[11px] text-fg focus-visible:border-brand"
          />
          <div className="flex flex-wrap gap-1">
            {EVENT_TEMPLATES.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setTemplates((previous) => `${previous}${previous.length > 0 && !previous.endsWith("\n") ? "\n" : ""}${date}|${item}`)}
                className="num rounded-sm border border-border-strong px-1.5 py-px text-[9px] text-fg-muted hover:border-brand/60 hover:text-fg"
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="sim-events" className="label-micro">
            自定义事件（每行 <span className="num">日期|标题|内容</span>）
          </Label>
          <textarea
            id="sim-events"
            rows={3}
            value={customEvents}
            placeholder={`${date}|突发停电通知|今晚 18:00-20:00 计划停电`}
            onChange={(event) => setCustomEvents(event.target.value)}
            className="num rounded-md border border-border-strong bg-surface-2 px-2.5 py-1.5 text-[11px] text-fg focus-visible:border-brand"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="sim-workers" className="label-micro">
            并发线程
          </Label>
          <Input
            id="sim-workers"
            type="number"
            min={1}
            max={8}
            value={workers}
            onChange={(event) => {
              const next = Number(event.target.value)
              setWorkers(Number.isFinite(next) ? Math.min(8, Math.max(1, Math.trunc(next))) : 4)
            }}
            className={FIELD_CLASS}
          />
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 rounded-md border border-border bg-surface px-4 py-3">
        <span className="label-micro flex items-center gap-1.5">
          <House className="size-3" aria-hidden />
          高级选项
        </span>
        {[
          { id: "opt-s4", label: "仅重跑 s4（--s4-only）", value: s4Only, set: setS4Only },
          { id: "opt-cost", label: "注入具体成本（--cost-context）", value: costContext, set: setCostContext },
          { id: "opt-ev", label: "自然 EV 基线（--natural-ev）", value: naturalEv, set: setNaturalEv },
          { id: "opt-peer", label: "社会助推（--peer-nudge）", value: peerNudge, set: setPeerNudge },
        ].map((item) => (
          <div key={item.id} className="flex items-center gap-2">
            <Switch id={item.id} checked={item.value} onCheckedChange={item.set} />
            <Label htmlFor={item.id} className="text-[11px] text-fg-muted">
              {item.label}
            </Label>
          </div>
        ))}
      </div>

      <JobSubmitBar
        payload={payload}
        disabled={USE_MOCK || effectiveWorld.length === 0}
        disabledReason={
          USE_MOCK
            ? "当前是 mock 模式（VITE_USE_MOCK=1），不会真正提交。请用 VITE_USE_MOCK=0 启动前端以连接后端。"
            : "请先选择世界。"
        }
      />
    </div>
  )
}
