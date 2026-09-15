import { GitBranch, ScrollText } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useStages } from "@/hooks/useDayData"
import { useTimeStore } from "@/store/time"

interface Segment {
  time?: string
  location?: string
  activity?: string
  desc?: string
  operations?: { unique_id?: string; action?: string }[]
}

const STAGES = [
  {
    key: "s1",
    title: "s1 · 宏观计划",
    hint: "整天的时间 / 地点 / 活动",
    listKey: "activities",
  },
  {
    key: "s2",
    title: "s2 · 成员协调",
    hint: "避免共用资源冲突",
    listKey: "coordinated_activities",
  },
  {
    key: "s3",
    title: "s3 · 描述丰富",
    hint: "为每段活动补充细节",
    listKey: "enriched_activities",
  },
  {
    key: "s4",
    title: "s4 · 电器决策",
    hint: "每段的电器操作",
    listKey: "appliance_decisions",
  },
] as const

const readList = (payload: unknown, key: string): Segment[] => {
  if (payload === null || typeof payload !== "object") return []
  const list = (payload as Record<string, unknown>)[key]
  if (!Array.isArray(list)) return []
  return list.filter((item): item is Segment => item !== null && typeof item === "object")
}

const readLog = (logs: Record<string, string> | undefined, key: string): string =>
  logs?.[key] ?? ""

export function PipelineDrawer() {
  const selectedMember = useTimeStore((state) => state.selectedMember)
  const stagesQuery = useStages(selectedMember)
  const stages = stagesQuery.data

  const available = (key: string): boolean => {
    if (stages === undefined) return false
    const payload = (stages as unknown as Record<string, unknown>)[key]
    return payload !== null && payload !== undefined
  }

  return (
    <Sheet>
      <div className="flex flex-col gap-3 rounded-lg border border-border bg-surface px-4 py-3">
        <div className="flex items-center justify-between gap-2">
          <span className="label-micro flex items-center gap-1.5">
            <GitBranch className="size-3" aria-hidden />
            决策流水线
          </span>
          <Badge variant="outline" className="label-latin">
            s1–s4
          </Badge>
        </div>
        <p className="text-[11px] text-fg-muted">
          {selectedMember === null
            ? "在时间轴上点击任一色块以选中成员。"
            : `已选 ${selectedMember}，可查看 s1 → s4 的推理链与 LLM 日志。`}
        </p>
        <SheetTrigger asChild>
          <Button variant="outline" size="sm" disabled={selectedMember === null} className="w-full">
            <ScrollText />
            打开流水线
          </Button>
        </SheetTrigger>
      </div>

      <SheetContent side="right" className="flex w-full flex-col gap-0 sm:max-w-2xl">
        <SheetHeader className="border-b border-border">
          <SheetTitle className="flex items-center gap-2">
            决策流水线
            <span className="num text-[12px] font-normal text-fg-muted">{selectedMember ?? "—"}</span>
          </SheetTitle>
          <SheetDescription>
            该成员这一天的完整决策链：宏观计划 → 成员协调 → 描述丰富 → 电器决策，附各阶段 LLM 原始日志。
          </SheetDescription>
        </SheetHeader>

        <Tabs defaultValue="s1" className="flex min-h-0 flex-1 flex-col">
          <TabsList className="mx-5 mt-4 shrink-0 justify-start">
            {STAGES.map((stage) => (
              <TabsTrigger key={stage.key} value={stage.key} className="num text-[11px]">
                {stage.key}
                {available(stage.key) ? "" : " ·"}
              </TabsTrigger>
            ))}
            <TabsTrigger value="logs" className="text-[11px]">
              日志
            </TabsTrigger>
            <TabsTrigger value="report" className="text-[11px]">
              校验
            </TabsTrigger>
          </TabsList>

          <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
            {STAGES.map((stage) => {
              const payload = stages === undefined ? undefined : (stages as unknown as Record<string, unknown>)[stage.key]
              const segments = readList(payload, stage.listKey)
              return (
                <TabsContent key={stage.key} value={stage.key} className="mt-0">
                  <div className="mb-3 flex items-baseline gap-2">
                    <span className="text-[12px] font-semibold text-fg">{stage.title}</span>
                    <span className="label-micro">{stage.hint}</span>
                    <span className="num ml-auto text-[10px] text-fg-subtle">
                      {segments.length} 段
                    </span>
                  </div>

                  {segments.length === 0 ? (
                    <p className="text-[11px] text-fg-subtle">
                      {stagesQuery.isPending ? "载入中…" : "该阶段没有数据。"}
                    </p>
                  ) : (
                    <ul className="flex flex-col gap-1.5">
                      {segments.map((segment, index) => (
                        <li
                          key={`${stage.key}-${index}`}
                          className="rounded-md border border-border bg-surface-2 px-3 py-2"
                        >
                          <div className="flex items-baseline gap-2">
                            <span className="num shrink-0 text-[11px] text-brand">{segment.time ?? "—"}</span>
                            <span className="min-w-0 flex-1 truncate text-[11px] text-fg-muted">
                              {segment.location ?? "—"}
                            </span>
                          </div>
                          <div className="mt-0.5 text-[11px] text-fg">{segment.activity ?? "—"}</div>
                          {segment.desc !== undefined && segment.desc.length > 0 ? (
                            <div className="mt-0.5 text-[10px] leading-relaxed text-fg-subtle">
                              {segment.desc}
                            </div>
                          ) : null}
                          {segment.operations !== undefined && segment.operations.length > 0 ? (
                            <div className="mt-1.5 flex flex-wrap gap-1">
                              {segment.operations.map((operation, opIndex) => (
                                <span
                                  key={`${operation.unique_id}-${opIndex}`}
                                  className="num rounded-sm border border-border-strong bg-surface px-1.5 py-px text-[9px] text-fg-muted"
                                >
                                  {operation.unique_id}
                                  <span className="text-energy">
                                    {operation.action !== undefined ? ` ${operation.action}` : ""}
                                  </span>
                                </span>
                              ))}
                            </div>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                  )}
                </TabsContent>
              )
            })}

            <TabsContent value="logs" className="mt-0">
              <div className="flex flex-col gap-4">
                {STAGES.map((stage) => {
                  const text = readLog(stages?.logs, stage.key)
                  return (
                    <section key={`log-${stage.key}`}>
                      <div className="mb-1.5 flex items-baseline gap-2">
                        <span className="text-[12px] font-semibold text-fg">{stage.title}</span>
                        <span className="label-latin">raw llm log</span>
                      </div>
                      <pre className="num max-h-72 overflow-auto rounded-md border border-border bg-surface-2 px-3 py-2 text-[10px] leading-relaxed whitespace-pre-wrap text-fg-muted">
                        {text.length > 0 ? text : "该阶段没有日志文件。"}
                      </pre>
                    </section>
                  )
                })}
              </div>
            </TabsContent>

            <TabsContent value="report" className="mt-0">
              <div className="mb-3 flex items-baseline gap-2">
                <span className="text-[12px] font-semibold text-fg">s4 校验报告</span>
                <span className="label-micro">清理 / 修复 / 丢弃统计</span>
              </div>
              <pre className="num max-h-[28rem] overflow-auto rounded-md border border-border bg-surface-2 px-3 py-2 text-[10px] leading-relaxed whitespace-pre-wrap text-fg-muted">
                {stages?.report === null || stages?.report === undefined
                  ? "没有校验报告。"
                  : JSON.stringify(stages.report, null, 2)}
              </pre>
            </TabsContent>
          </div>
        </Tabs>
      </SheetContent>
    </Sheet>
  )
}
