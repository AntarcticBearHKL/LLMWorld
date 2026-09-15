import { useState } from "react"

import { CheckCircle2, Loader2, RotateCcw, Save, Settings2 } from "lucide-react"

import { DEFAULT_SETTINGS } from "@/api/client"
import type { Settings, SettingsUpdate } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useSettings, useUpdateSettings } from "@/hooks/useSettings"
import { errorMessage } from "@/lib/errors"
import { cn } from "@/lib/utils"

type SettingsKey = keyof Settings

interface FieldSpec {
  key: SettingsKey
  label: string
  env: string
  kind: "text" | "number"
  min?: number
  max?: number
  step?: number
  placeholder?: string
}

const FIELDS: readonly FieldSpec[] = [
  {
    key: "model",
    label: "模型",
    env: "LLMWORLD_MODEL",
    kind: "text",
    placeholder: "deepseek-v4-flash",
  },
  {
    key: "temperature",
    label: "温度",
    env: "LLMWORLD_TEMPERATURE",
    kind: "number",
    min: 0,
    max: 2,
    step: 0.1,
  },
  {
    key: "max_tokens",
    label: "最大 token 数",
    env: "LLMWORLD_MAX_TOKENS",
    kind: "number",
    min: 1,
    step: 1,
  },
  {
    key: "request_timeout_seconds",
    label: "请求超时（秒）",
    env: "LLMWORLD_REQUEST_TIMEOUT",
    kind: "number",
    min: 1,
    step: 1,
  },
  {
    key: "max_retries",
    label: "最大重试次数",
    env: "LLMWORLD_MAX_RETRIES",
    kind: "number",
    min: 1,
    step: 1,
  },
  {
    key: "retry_backoff_seconds",
    label: "重试退避（秒）",
    env: "LLMWORLD_RETRY_BACKOFF",
    kind: "number",
    min: 0,
    step: 0.5,
  },
]

const FIELD_CLASS =
  "h-8 rounded-md border-border-strong bg-surface-2 px-2.5 text-[12px] text-fg focus-visible:border-brand"

type FormValues = Record<SettingsKey, string>

const toForm = (settings: Settings): FormValues => ({
  model: settings.model,
  temperature: String(settings.temperature),
  max_tokens: String(settings.max_tokens),
  request_timeout_seconds: String(settings.request_timeout_seconds),
  max_retries: String(settings.max_retries),
  retry_backoff_seconds: String(settings.retry_backoff_seconds),
})

type ParsedField = { ok: true; value: string | number } | { ok: false; message: string }

const parseField = (spec: FieldSpec, raw: string): ParsedField => {
  const text = raw.trim()
  if (spec.kind === "text") {
    return text.length > 0 ? { ok: true, value: text } : { ok: false, message: "不能为空" }
  }
  const value = Number(text)
  if (text.length === 0 || !Number.isFinite(value)) return { ok: false, message: "请输入数字" }
  if (spec.key === "temperature" && (value < 0 || value > 2)) {
    return { ok: false, message: "需在 0–2 之间" }
  }
  if (spec.key === "retry_backoff_seconds" && value < 0) {
    return { ok: false, message: "需 ≥ 0" }
  }
  if (spec.key === "max_tokens" || spec.key === "request_timeout_seconds") {
    if (!Number.isInteger(value) || value <= 0) return { ok: false, message: "需为大于 0 的整数" }
  }
  if (spec.key === "max_retries" && (!Number.isInteger(value) || value < 1)) {
    return { ok: false, message: "需为 ≥ 1 的整数" }
  }
  return { ok: true, value }
}

const assignField = <K extends SettingsKey>(
  patch: SettingsUpdate,
  key: K,
  value: Settings[K],
): void => {
  patch[key] = value
}

interface Draft {
  values: FormValues
  patch: SettingsUpdate
  errors: Partial<Record<SettingsKey, string>>
  changed: number
  invalid: number
}

const analyze = (values: FormValues, settings: Settings): Draft => {
  const errors: Partial<Record<SettingsKey, string>> = {}
  const patch: SettingsUpdate = {}
  let changed = 0
  let invalid = 0
  for (const spec of FIELDS) {
    const parsed = parseField(spec, values[spec.key])
    if (!parsed.ok) {
      errors[spec.key] = parsed.message
      invalid += 1
      continue
    }
    if (parsed.value !== settings[spec.key]) {
      assignField(patch, spec.key, parsed.value)
      changed += 1
    }
  }
  return { values, patch, errors, changed, invalid }
}

export function SettingsPanel() {
  const settingsQuery = useSettings()
  const update = useUpdateSettings()
  const [form, setForm] = useState<FormValues | null>(null)
  const [justSaved, setJustSaved] = useState(false)

  const settings = settingsQuery.data
  const values = form ?? (settings === undefined ? null : toForm(settings))
  const draft = values === null || settings === undefined ? null : analyze(values, settings)

  const onChange = (key: SettingsKey, next: string) => {
    const base = form ?? (settings === undefined ? null : toForm(settings))
    if (base === null) return
    setJustSaved(false)
    setForm({ ...base, [key]: next })
  }

  const onSave = () => {
    if (draft === null || draft.changed === 0 || draft.invalid > 0) return
    update.mutate(draft.patch, { onSuccess: () => setJustSaved(true) })
  }

  const onRestoreDefaults = () => {
    setJustSaved(false)
    setForm(toForm(DEFAULT_SETTINGS))
  }

  if (settingsQuery.isPending) {
    return <p className="px-4 py-6 text-[11px] text-fg-subtle">设置载入中…</p>
  }

  if (settingsQuery.isError) {
    return (
      <div className="flex flex-col items-start gap-2 px-4 py-6">
        <p className="text-[11px] text-danger">设置读取失败：{errorMessage(settingsQuery.error)}</p>
        <Button variant="outline" size="xs" onClick={() => void settingsQuery.refetch()}>
          重试
        </Button>
      </div>
    )
  }

  if (draft === null) {
    return <p className="px-4 py-6 text-[11px] text-fg-subtle">设置载入中…</p>
  }

  const canSave = draft.changed > 0 && draft.invalid === 0 && !update.isPending

  return (
    <div className="flex flex-col gap-4 p-4">
      <header className="flex items-start gap-2">
        <Settings2 className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden />
        <div className="flex flex-col gap-1">
          <h2 className="text-[13px] font-semibold text-fg">LLM 运行参数</h2>
          <p className="text-[11px] text-fg-muted">
            保存后写入后端设置文件，并在启动下一个作业时以{" "}
            <span className="num">LLMWORLD_*</span> 环境变量注入子进程，因此只影响保存之后启动的作业，正在运行的作业不受影响。
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {FIELDS.map((spec) => {
          const error = draft.errors[spec.key]
          return (
            <div key={spec.key} className="flex flex-col gap-1.5">
              <Label htmlFor={`settings-${spec.key}`} className="label-micro">
                {spec.label}
              </Label>
              <Input
                id={`settings-${spec.key}`}
                type={spec.kind === "number" ? "number" : "text"}
                value={draft.values[spec.key]}
                placeholder={spec.placeholder}
                min={spec.min}
                max={spec.max}
                step={spec.step}
                disabled={update.isPending}
                aria-invalid={error !== undefined}
                onChange={(event) => onChange(spec.key, event.target.value)}
                className={cn(FIELD_CLASS, spec.kind === "number" && "num")}
              />
              <span className={cn("text-[10px]", error === undefined ? "label-latin" : "text-danger")}>
                {error ?? spec.env}
              </span>
            </div>
          )
        })}
      </div>

      <div className="flex flex-wrap items-center gap-x-3 gap-y-2 border-t border-border pt-3">
        <Button size="sm" onClick={onSave} disabled={!canSave}>
          {update.isPending ? <Loader2 className="animate-spin" /> : <Save />}
          保存
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onRestoreDefaults}
          disabled={update.isPending}
          title="填回默认值，仍需点「保存」生效"
        >
          <RotateCcw />
          恢复默认
        </Button>

        {draft.invalid > 0 ? (
          <span className="text-[10px] text-danger">有 {draft.invalid} 项输入无效</span>
        ) : draft.changed > 0 ? (
          <span className="label-micro">待保存 {draft.changed} 项</span>
        ) : (
          <span className="label-micro">无改动</span>
        )}

        {justSaved ? (
          <span className="flex items-center gap-1 text-[10px] text-success">
            <CheckCircle2 className="size-3" aria-hidden />
            已保存，下一个作业生效
          </span>
        ) : null}

        {update.isError ? (
          <span className="text-[10px] text-danger">保存失败：{errorMessage(update.error)}</span>
        ) : null}
      </div>
    </div>
  )
}
