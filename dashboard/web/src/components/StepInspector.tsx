import { useState, type ReactNode } from "react"

import { RefreshCw } from "lucide-react"

import { ApiError } from "@/api/client"
import type { LLMCallSummary } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useJobLlmCall, useJobLlmCalls } from "@/hooks/useJobs"
import { cn } from "@/lib/utils"

interface StepInspectorProps {
  jobId: string | null
  step?: string | null
  live?: boolean
}

const asRecord = (value: unknown): Record<string, unknown> | null =>
  typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null

const readText = (record: Record<string, unknown> | null, key: string): string | null => {
  if (record === null) return null
  const value = record[key]
  return typeof value === "string" ? value : null
}

const asJson = (value: unknown): string => {
  const text = JSON.stringify(value, null, 2)
  return text === undefined ? String(value) : text
}

type ResponseView =
  | { kind: "success"; content: string; reasoning: string | null; usage: unknown }
  | { kind: "failure"; rawText: string }
  | { kind: "raw"; json: string }
  | { kind: "none" }

const describeResponse = (response: unknown): ResponseView => {
  if (response === null || response === undefined) return { kind: "none" }
  const record = asRecord(response)
  if (record === null) return { kind: "raw", json: asJson(response) }
  const content = readText(record, "content")
  const reasoning = readText(record, "reasoning_content")
  if (content === null && reasoning === null) {
    const rawText = readText(record, "raw_text")
    return rawText === null ? { kind: "raw", json: asJson(record) } : { kind: "failure", rawText }
  }
  return { kind: "success", content: content ?? "", reasoning, usage: record["usage"] }
}

const formatDuration = (seconds: number | null): string => {
  if (seconds === null) return "—"
  return seconds < 1 ? `${Math.round(seconds * 1000)} ms` : `${seconds.toFixed(2)} s`
}

const formatChars = (chars: number | null): string => {
  if (chars === null) return "—"
  return chars >= 1000 ? `${(chars / 1000).toFixed(1)}k chars` : `${chars} chars`
}

const formatStartedAt = (iso: string | null): string => {
  if (iso === null) return "—"
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  const pad = (value: number): string => String(value).padStart(2, "0")
  return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

const statusText = (httpStatus: number | null): string =>
  httpStatus === null ? "no status" : `HTTP ${httpStatus}`

const PRE_CLASS =
  "num max-h-80 overflow-auto rounded-lg border border-border bg-surface-2 px-3 py-2 text-[12px] leading-relaxed whitespace-pre-wrap break-words text-fg-muted"

function StatusChip({ ok, httpStatus }: { ok: boolean; httpStatus: number | null }) {
  return (
    <span
      className={cn(
        "num rounded-full border px-2 py-px text-[12px] whitespace-nowrap",
        ok
          ? "border-success/40 bg-success/10 text-success"
          : "border-danger/40 bg-danger/10 text-danger",
      )}
    >
      {statusText(httpStatus)}
    </span>
  )
}

function CallRow({
  call,
  active,
  onSelect,
}: {
  call: LLMCallSummary
  active: boolean
  onSelect: () => void
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={active}
      className={cn(
        "flex w-full flex-col gap-1 border-b border-border px-3 py-2 text-left transition-colors",
        active ? "bg-item-selected" : "hover:bg-item-hover",
      )}
    >
      <div className="flex items-center gap-2">
        <span className="num text-[13px] text-fg">#{call.request_index}</span>
        <StatusChip ok={call.ok} httpStatus={call.http_status} />
        <span
          className={cn("ml-auto text-[12px] whitespace-nowrap", call.ok ? "text-success" : "text-danger")}
        >
          {call.ok ? "OK" : "Failed"}
        </span>
      </div>
      <div className="num flex items-center gap-1.5 text-[12px] text-fg-subtle">
        <span>{formatDuration(call.duration_seconds)}</span>
        <span aria-hidden>·</span>
        <span>{formatChars(call.prompt_chars)}</span>
        {call.request_count > 1 ? (
          <span className="ml-auto">
            {call.request_index}/{call.request_count}
          </span>
        ) : null}
      </div>
    </button>
  )
}

function Section({ title, hint, children }: { title: string; hint?: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-1.5">
      <div className="flex items-baseline gap-2">
        <span className="text-[15px] font-semibold text-fg">{title}</span>
        {hint !== undefined ? <span className="label-latin">{hint}</span> : null}
      </div>
      {children}
    </section>
  )
}

function ResponseBody({ view }: { view: ResponseView }) {
  if (view.kind === "none") return <p className="text-[13px] text-fg-subtle">(no response body)</p>
  if (view.kind === "failure") {
    return (
      <div className="flex flex-col gap-1.5">
        <span className="text-[12px] text-danger">HTTP error response body (provider raw_text)</span>
        <pre className={cn(PRE_CLASS, "border-danger/40 text-fg")}>{view.rawText}</pre>
      </div>
    )
  }
  if (view.kind === "raw") return <pre className={PRE_CLASS}>{view.json}</pre>
  return (
    <div className="flex flex-col gap-3">
      {view.content.length > 0 ? (
        <pre className={cn(PRE_CLASS, "text-fg")}>{view.content}</pre>
      ) : (
        <p className="text-[13px] text-fg-subtle">(empty response content)</p>
      )}
      {view.reasoning !== null && view.reasoning.length > 0 ? (
        <div className="flex flex-col gap-1.5">
          <span className="label-micro">Reasoning</span>
          <pre className={PRE_CLASS}>{view.reasoning}</pre>
        </div>
      ) : null}
      {view.usage !== null && view.usage !== undefined ? (
        <div className="flex flex-col gap-1.5">
          <span className="label-micro">Usage</span>
          <pre className={PRE_CLASS}>{asJson(view.usage)}</pre>
        </div>
      ) : null}
    </div>
  )
}

function CallDetail({ jobId, callId }: { jobId: string; callId: string }) {
  const detailQuery = useJobLlmCall(jobId, callId)

  if (detailQuery.isPending) {
    return <p className="px-4 py-3 text-[13px] text-fg-subtle">Loading…</p>
  }

  if (detailQuery.isError) {
    const message =
      detailQuery.error instanceof ApiError ? detailQuery.error.message : "Could not load this call's details"
    return <p className="px-4 py-3 text-[13px] text-danger">{message}</p>
  }

  const detail = detailQuery.data
  const request = asRecord(detail.request)
  const model = readText(request, "model")
  const prompt = readText(request, "input")
  const ok = detail.http_status === 200 && detail.error === null

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-4 py-2">
        <span className="num text-[13px] text-fg">
          #{detail.request_index}
          {detail.request_count > 1 ? (
            <span className="text-fg-subtle">/{detail.request_count}</span>
          ) : null}
        </span>
        <StatusChip ok={ok} httpStatus={detail.http_status} />
        <Badge variant="outline" className={cn("label-latin", ok ? "text-success" : "text-danger")}>
          {ok ? "OK" : "Failed"}
        </Badge>
        <span className="num text-[12px] text-fg-subtle">{formatDuration(detail.duration_seconds)}</span>
        <span className="num text-[12px] text-fg-subtle">{formatChars(detail.prompt_chars)}</span>
        <span className="num ml-auto text-[12px] text-fg-subtle">{formatStartedAt(detail.started_at)}</span>
      </div>

      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col gap-4 px-4 py-3">
          <div className="flex flex-wrap items-baseline gap-2">
            <span className="label-micro">Model</span>
            <span className="num text-[13px] text-fg">{model ?? "—"}</span>
            <span className="num ml-auto text-[12px] text-fg-subtle">{detail.logical_call_id}</span>
          </div>

          <Section title="Prompt" hint="request.input">
            {prompt === null || prompt.length === 0 ? (
              <p className="text-[13px] text-fg-subtle">(no prompt recorded)</p>
            ) : (
              <pre className={PRE_CLASS}>{prompt}</pre>
            )}
          </Section>

          <Section title="Raw response">
            <ResponseBody view={describeResponse(detail.response)} />
          </Section>

          {detail.error !== null ? (
            <Section title="Error">
              <p className="rounded-xl border border-danger/40 bg-danger/10 px-3 py-2 text-[13px] text-danger">
                {detail.error}
              </p>
            </Section>
          ) : null}
        </div>
      </ScrollArea>
    </div>
  )
}

export function StepInspector({ jobId, step = null, live = false }: StepInspectorProps) {
  const listQuery = useJobLlmCalls(jobId, live)
  const [pickedId, setPickedId] = useState<string | null>(null)

  if (jobId === null) {
    return (
      <div className="flex flex-1 items-center justify-center p-6">
        <span className="text-[13px] text-fg-subtle">Select a build job to inspect its LLM calls.</span>
      </div>
    )
  }

  const calls = listQuery.data?.calls ?? []
  const activeId =
    pickedId !== null && calls.some((call) => call.logical_call_id === pickedId)
      ? pickedId
      : (calls[0]?.logical_call_id ?? null)
  const list = listQuery.data

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-center gap-2 border-b border-border px-4 py-2">
        <span className="label-micro">LLM calls</span>
        <span className="num text-[12px] text-fg-subtle">
          {list === undefined ? "—" : `${list.total} calls`}
        </span>
        {step !== null ? <span className="num text-[12px] text-fg-subtle">· step {step}</span> : null}
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label="Refresh LLM calls"
          className="ml-auto"
          onClick={() => void listQuery.refetch()}
        >
          <RefreshCw />
        </Button>
      </div>

      {listQuery.isPending ? (
        <p className="px-4 py-3 text-[13px] text-fg-subtle">Loading…</p>
      ) : listQuery.isError ? (
        <p className="px-4 py-3 text-[13px] text-danger">
          {listQuery.error instanceof ApiError ? listQuery.error.message : "Could not load LLM calls"}
        </p>
      ) : list === undefined ? (
        <p className="px-4 py-3 text-[13px] text-fg-subtle">Loading…</p>
      ) : list.total === 0 ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-1.5 p-6 text-center">
          <span className="text-[14px] text-fg-muted">
            {list.exists ? "The trace file is empty." : "This job has no LLM calls."}
          </span>
          <span className="text-[12px] text-fg-subtle">
            The step may not have reached its LLM phase yet, or the job is still queued.
          </span>
        </div>
      ) : (
        <div className="flex min-h-0 flex-1 flex-col md:flex-row">
          <ul className="max-h-40 min-h-0 shrink-0 overflow-y-auto border-b border-border md:max-h-none md:w-60 md:border-r md:border-b-0">
            {calls.map((call) => (
              <li key={call.logical_call_id}>
                <CallRow
                  call={call}
                  active={call.logical_call_id === activeId}
                  onSelect={() => setPickedId(call.logical_call_id)}
                />
              </li>
            ))}
          </ul>
          <div className="flex min-h-0 flex-1 flex-col">
            {activeId === null ? (
              <p className="px-4 py-3 text-[13px] text-fg-subtle">Select a call to view details.</p>
            ) : (
              <CallDetail jobId={jobId} callId={activeId} />
            )}
          </div>
        </div>
      )}
    </div>
  )
}
