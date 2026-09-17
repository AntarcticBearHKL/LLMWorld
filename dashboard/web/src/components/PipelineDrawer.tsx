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
    title: "s1 · Macro plan",
    hint: "time / place / activity for the whole day",
    listKey: "activities",
  },
  {
    key: "s2",
    title: "s2 · Member coordination",
    hint: "avoid shared-resource conflicts",
    listKey: "coordinated_activities",
  },
  {
    key: "s3",
    title: "s3 · Rich description",
    hint: "add detail to each segment",
    listKey: "enriched_activities",
  },
  {
    key: "s4",
    title: "s4 · Appliance decisions",
    hint: "appliance operations per segment",
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
      <div className="card flex flex-col gap-3 px-4 py-3.5">
        <div className="flex items-center justify-between gap-2">
          <span className="label-micro flex items-center gap-1.5">
            <GitBranch className="size-3" aria-hidden />
            Decision pipeline
          </span>
          <Badge variant="outline" className="label-latin">
            s1–s4
          </Badge>
        </div>
        <p className="t-body">
          {selectedMember === null
            ? "Select a block on the timeline to pick a member."
            : `Selected ${selectedMember} — inspect the s1 → s4 reasoning chain and LLM logs.`}
        </p>
        <SheetTrigger asChild>
          <Button variant="outline" size="sm" disabled={selectedMember === null} className="w-full">
            <ScrollText />
            Open pipeline
          </Button>
        </SheetTrigger>
      </div>

      <SheetContent side="right" className="flex w-full flex-col gap-0 sm:max-w-2xl">
        <SheetHeader className="border-b border-border">
          <SheetTitle className="flex items-center gap-2">
            Decision pipeline
            <span className="num t-caption">{selectedMember ?? "—"}</span>
          </SheetTitle>
          <SheetDescription>
            The full decision chain for this member&apos;s day: macro plan → member coordination → rich
            description → appliance decisions, with the raw LLM log of every stage.
          </SheetDescription>
        </SheetHeader>

        <Tabs defaultValue="s1" className="flex min-h-0 flex-1 flex-col">
          <TabsList className="mx-5 mt-4 shrink-0 justify-start">
            {STAGES.map((stage) => (
              <TabsTrigger key={stage.key} value={stage.key} className="num t-micro">
                {stage.key}
                {available(stage.key) ? "" : " ·"}
              </TabsTrigger>
            ))}
            <TabsTrigger value="logs" className="t-micro">
              Logs
            </TabsTrigger>
            <TabsTrigger value="report" className="t-micro">
              Report
            </TabsTrigger>
          </TabsList>

          <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
            {STAGES.map((stage) => {
              const payload = stages === undefined ? undefined : (stages as unknown as Record<string, unknown>)[stage.key]
              const segments = readList(payload, stage.listKey)
              return (
                <TabsContent key={stage.key} value={stage.key} className="mt-0">
                  <div className="mb-3 flex items-baseline gap-2">
                    <span className="t-title">{stage.title}</span>
                    <span className="label-micro">{stage.hint}</span>
                    <span className="num ml-auto t-caption">
                      {segments.length} segments
                    </span>
                  </div>

                  {segments.length === 0 ? (
                    <p className="t-caption">
                      {stagesQuery.isPending ? "Loading…" : "No data for this stage."}
                    </p>
                  ) : (
                    <ul className="flex flex-col gap-0">
                      {segments.map((segment, index) => (
                        <li
                          key={`${stage.key}-${index}`}
                          className="border-b border-border bg-surface-2 px-3.5 py-2.5"
                        >
                          <div className="flex items-baseline gap-2">
                            <span className="num shrink-0 t-caption text-brand">{segment.time ?? "—"}</span>
                            <span className="min-w-0 flex-1 truncate t-body">
                              {segment.location ?? "—"}
                            </span>
                          </div>
                          <div className="mt-0.5 t-body">{segment.activity ?? "—"}</div>
                          {segment.desc !== undefined && segment.desc.length > 0 ? (
                            <div className="mt-0.5 t-body leading-relaxed">
                              {segment.desc}
                            </div>
                          ) : null}
                          {segment.operations !== undefined && segment.operations.length > 0 ? (
                            <div className="mt-1.5 flex flex-wrap gap-1">
                              {segment.operations.map((operation, opIndex) => (
                                <span
                                  key={`${operation.unique_id}-${opIndex}`}
                                  className="num rounded-full border border-border-strong bg-surface px-2 py-px t-micro"
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
                        <span className="t-title">{stage.title}</span>
                        <span className="label-latin">raw llm log</span>
                      </div>
                      <pre className="num max-h-72 overflow-auto rounded-xl border border-border bg-surface-2 px-3 py-2 t-caption leading-relaxed whitespace-pre-wrap">
                        {text.length > 0 ? text : "No log file for this stage."}
                      </pre>
                    </section>
                  )
                })}
              </div>
            </TabsContent>

            <TabsContent value="report" className="mt-0">
              <div className="mb-3 flex items-baseline gap-2">
                <span className="t-title">s4 validation report</span>
                <span className="label-micro">cleaned / repaired / dropped counts</span>
              </div>
              <pre className="num max-h-[28rem] overflow-auto rounded-xl border border-border bg-surface-2 px-3 py-2 t-caption leading-relaxed whitespace-pre-wrap">
                {stages?.report === null || stages?.report === undefined
                  ? "No validation report."
                  : JSON.stringify(stages.report, null, 2)}
              </pre>
            </TabsContent>
          </div>
        </Tabs>
      </SheetContent>
    </Sheet>
  )
}
