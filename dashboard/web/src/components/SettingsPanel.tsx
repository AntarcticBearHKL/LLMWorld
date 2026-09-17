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
  description: string
  kind: "text" | "number"
  min?: number
  max?: number
  step?: number
  placeholder?: string
}

const FIELDS: readonly FieldSpec[] = [
  {
    key: "model",
    label: "Model",
    env: "LLMWORLD_MODEL",
    description: "The model every pipeline stage calls.",
    kind: "text",
    placeholder: "deepseek-v4-flash",
  },
  {
    key: "temperature",
    label: "Temperature",
    env: "LLMWORLD_TEMPERATURE",
    description: "Sampling randomness — 0 is the most deterministic.",
    kind: "number",
    min: 0,
    max: 2,
    step: 0.1,
  },
  {
    key: "max_tokens",
    label: "Max tokens",
    env: "LLMWORLD_MAX_TOKENS",
    description: "Upper bound on tokens per LLM response.",
    kind: "number",
    min: 1,
    step: 1,
  },
  {
    key: "request_timeout_seconds",
    label: "Request timeout (s)",
    env: "LLMWORLD_REQUEST_TIMEOUT",
    description: "Abort a single LLM call after this long.",
    kind: "number",
    min: 1,
    step: 1,
  },
  {
    key: "max_retries",
    label: "Max retries",
    env: "LLMWORLD_MAX_RETRIES",
    description: "Retry attempts before a step is marked failed.",
    kind: "number",
    min: 1,
    step: 1,
  },
  {
    key: "retry_backoff_seconds",
    label: "Retry backoff (s)",
    env: "LLMWORLD_RETRY_BACKOFF",
    description: "Pause between retry attempts.",
    kind: "number",
    min: 0,
    step: 0.5,
  },
]

const FIELD_CLASS = "h-8 px-2.5 t-body"

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
    return text.length > 0 ? { ok: true, value: text } : { ok: false, message: "Required" }
  }
  const value = Number(text)
  if (text.length === 0 || !Number.isFinite(value)) return { ok: false, message: "Enter a number" }
  if (spec.key === "temperature" && (value < 0 || value > 2)) {
    return { ok: false, message: "Must be between 0 and 2" }
  }
  if (spec.key === "retry_backoff_seconds" && value < 0) {
    return { ok: false, message: "Must be ≥ 0" }
  }
  if (spec.key === "max_tokens" || spec.key === "request_timeout_seconds") {
    if (!Number.isInteger(value) || value <= 0) return { ok: false, message: "Must be an integer > 0" }
  }
  if (spec.key === "max_retries" && (!Number.isInteger(value) || value < 1)) {
    return { ok: false, message: "Must be an integer ≥ 1" }
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
    return <p className="px-4 py-6 t-caption">Loading settings…</p>
  }

  if (settingsQuery.isError) {
    return (
      <div className="flex flex-col items-start gap-2 px-4 py-6">
        <p className="t-caption text-danger">Failed to load settings: {errorMessage(settingsQuery.error)}</p>
        <Button variant="outline" size="xs" onClick={() => void settingsQuery.refetch()}>
          Retry
        </Button>
      </div>
    )
  }

  if (draft === null) {
    return <p className="px-4 py-6 t-caption">Loading settings…</p>
  }

  const canSave = draft.changed > 0 && draft.invalid === 0 && !update.isPending

  return (
    <div className="flex flex-col gap-6 p-5 lg:p-6">
      <header className="flex items-start gap-2.5">
        <Settings2 className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden />
        <div className="flex flex-col gap-1">
          <h2 className="t-body">LLM runtime settings</h2>
          <p className="max-w-[720px] t-caption">
            Saving writes the backend settings file and injects the values into the next job as{" "}
            <span className="num">LLMWORLD_*</span> environment variables, so it only affects jobs
            started after saving; running jobs are untouched.
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-x-6 gap-y-4 md:grid-cols-2 xl:grid-cols-3">
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
              <span
                className={cn(
                  "t-caption leading-snug",
                  error === undefined ? "text-fg-subtle" : "text-danger",
                )}
              >
                {error ?? spec.description}
              </span>
              <span className="label-latin">{spec.env}</span>
            </div>
          )
        })}
      </div>

      <div className="flex flex-wrap items-center gap-x-3 gap-y-2 border-t border-border pt-4">
        <Button size="sm" onClick={onSave} disabled={!canSave}>
          {update.isPending ? <Loader2 className="animate-spin" /> : <Save />}
          Save
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onRestoreDefaults}
          disabled={update.isPending}
          title="Fill in the defaults; click Save to apply"
        >
          <RotateCcw />
          Restore defaults
        </Button>

        {draft.invalid > 0 ? (
          <span className="t-caption text-danger">{draft.invalid} invalid input(s)</span>
        ) : draft.changed > 0 ? (
          <span className="label-micro">{draft.changed} pending change(s)</span>
        ) : (
          <span className="label-micro">No changes</span>
        )}

        {justSaved ? (
          <span className="flex items-center gap-1 t-caption text-success">
            <CheckCircle2 className="size-3" aria-hidden />
            Saved — applies to the next job
          </span>
        ) : null}

        {update.isError ? (
          <span className="t-caption text-danger">Save failed: {errorMessage(update.error)}</span>
        ) : null}
      </div>
    </div>
  )
}
