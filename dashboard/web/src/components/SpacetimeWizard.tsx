import { cloneElement, useState } from "react"

import { Loader2, Plus } from "lucide-react"

import type { Spacetime, SpacetimeCreate } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useCreateSpacetime } from "@/hooks/useSpacetimes"
import { errorMessage } from "@/lib/errors"
import { cn } from "@/lib/utils"

const FIELD_CLASS = "h-8 px-2.5 text-[14px]"

const NAME_RE = /^[A-Za-z0-9][A-Za-z0-9._-]*$/
const DATE_RE = /^\d{4}-\d{2}-\d{2}$/
const EVENT_LINE_RE = /^\d{4}-\d{2}-\d{2}\|.+$/

const today = (): string => new Date().toISOString().slice(0, 10)

const parseLines = (raw: string): string[] =>
  raw
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

interface WizardDraft {
  name: string
  start_date: string
  days: string
  policy: string
  seed: string
  events: string
  notices: string
}

type WizardKey = keyof WizardDraft

type WizardErrors = Partial<Record<WizardKey, string>>

const emptyDraft = (): WizardDraft => ({
  name: "",
  start_date: today(),
  days: "1",
  policy: "",
  seed: "",
  events: "",
  notices: "",
})

const validate = (
  draft: WizardDraft,
): { errors: WizardErrors; payload: SpacetimeCreate | null } => {
  const errors: WizardErrors = {}

  const name = draft.name.trim()
  if (name.length === 0) errors.name = "Required"
  else if (!NAME_RE.test(name)) errors.name = "Use letters, digits, '.', '_' or '-'"

  const startDate = draft.start_date.trim()
  if (!DATE_RE.test(startDate)) errors.start_date = "Use YYYY-MM-DD"

  const days = Number(draft.days)
  if (!Number.isInteger(days) || days < 1) errors.days = "Whole number ≥ 1"

  const seedText = draft.seed.trim()
  const seed = seedText.length === 0 ? null : Number(seedText)
  if (seed !== null && (!Number.isInteger(seed) || seed < 0)) errors.seed = "Whole number ≥ 0"

  const events = parseLines(draft.events)
  for (const line of events) {
    if (!EVENT_LINE_RE.test(line)) {
      errors.events = `Each line must be YYYY-MM-DD|template — got "${line}"`
      break
    }
  }

  const notices = parseLines(draft.notices)
  for (const line of notices) {
    const parts = line.split("|")
    const date = (parts[0] ?? "").trim()
    const title = (parts[1] ?? "").trim()
    const content = parts.length > 2 ? parts.slice(2).join("|").trim() : ""
    if (!DATE_RE.test(date) || title.length === 0 || content.length === 0) {
      errors.notices = `Each line must be YYYY-MM-DD|title|content — got "${line}"`
      break
    }
  }

  if (Object.keys(errors).length > 0) return { errors, payload: null }

  const policy = draft.policy.trim()
  return {
    errors,
    payload: {
      name,
      start_date: startDate,
      days,
      policy: policy.length > 0 ? policy : null,
      events,
      notices,
      seed,
    },
  }
}

function Field({
  id,
  label,
  hint,
  error,
  children,
}: {
  id: string
  label: string
  hint: string
  error: string | undefined
  children: React.ReactElement<{ "aria-invalid"?: boolean }>
}) {
  return (
    <div className="flex min-w-0 flex-col gap-1">
      <Label htmlFor={id} className="label-micro text-fg-muted">
        {label}
      </Label>
      {cloneElement(children, { "aria-invalid": error !== undefined })}
      <span className={cn("text-[12px]", error !== undefined ? "text-danger" : "label-latin text-fg-muted")}>
        {error ?? hint}
      </span>
    </div>
  )
}

export function SpacetimeWizard({
  world,
  onCreated,
  onCancel,
}: {
  world: string
  onCreated: (item: Spacetime) => void
  onCancel: () => void
}) {
  const create = useCreateSpacetime(world)
  const [draft, setDraft] = useState<WizardDraft>(emptyDraft)
  const [errors, setErrors] = useState<WizardErrors>({})

  const patch = (key: WizardKey, value: string) => {
    setDraft((previous) => ({ ...previous, [key]: value }))
  }

  const onSubmit = () => {
    const result = validate(draft)
    setErrors(result.errors)
    if (result.payload === null) return
    create.mutate(result.payload, {
      onSuccess: (item) => {
        setDraft(emptyDraft())
        onCreated(item)
      },
    })
  }

  return (
    <div className="chrome flex flex-col gap-3.5 p-4">
      <span className="label-micro text-fg-muted">
        A spacetime fixes a policy, news and a start date for this world&apos;s households. Creating
        one queues a simulation job.
      </span>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Field id="spacetime-name" label="Name" hint="run name — letters, digits, '.', '_' or '-'" error={errors.name}>
          <Input
            id="spacetime-name"
            value={draft.name}
            onChange={(event) => patch("name", event.target.value)}
            placeholder="run_2026_09"
            className={cn(FIELD_CLASS, "num")}
          />
        </Field>

        <Field id="spacetime-start" label="Start date" hint="YYYY-MM-DD" error={errors.start_date}>
          <Input
            id="spacetime-start"
            type="date"
            value={draft.start_date}
            onChange={(event) => patch("start_date", event.target.value)}
            className={cn(FIELD_CLASS, "num")}
          />
        </Field>

        <Field id="spacetime-days" label="Days" hint="how many days to simulate" error={errors.days}>
          <Input
            id="spacetime-days"
            type="number"
            min={1}
            value={draft.days}
            onChange={(event) => patch("days", event.target.value)}
            className={cn(FIELD_CLASS, "num")}
          />
        </Field>

        <Field id="spacetime-policy" label="Policy" hint="free text, optional" error={errors.policy}>
          <Input
            id="spacetime-policy"
            value={draft.policy}
            onChange={(event) => patch("policy", event.target.value)}
            placeholder="baseline"
            className={cn(FIELD_CLASS, "num")}
          />
        </Field>

        <Field id="spacetime-seed" label="Seed" hint="optional whole number" error={errors.seed}>
          <Input
            id="spacetime-seed"
            type="number"
            min={0}
            value={draft.seed}
            onChange={(event) => patch("seed", event.target.value)}
            placeholder="42"
            className={cn(FIELD_CLASS, "num")}
          />
        </Field>
      </div>

      <Field
        id="spacetime-events"
        label="Events"
        hint="one YYYY-MM-DD|template per line (optional)"
        error={errors.events}
      >
        <Textarea
          id="spacetime-events"
          value={draft.events}
          onChange={(event) => patch("events", event.target.value)}
          rows={3}
          placeholder="2026-09-11|heatwave"
          className={cn("num min-h-16 px-2.5 py-2 text-[13px]")}
        />
      </Field>

      <Field
        id="spacetime-notices"
        label="Notices"
        hint="one YYYY-MM-DD|title|content per line (optional)"
        error={errors.notices}
      >
        <Textarea
          id="spacetime-notices"
          value={draft.notices}
          onChange={(event) => patch("notices", event.target.value)}
          rows={3}
          placeholder="2026-09-11|Grid maintenance|Planned outage 09:00–11:00"
          className={cn("num min-h-16 px-2.5 py-2 text-[13px]")}
        />
      </Field>

      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" onClick={onSubmit} disabled={create.isPending}>
          {create.isPending ? <Loader2 className="animate-spin" /> : <Plus />}
          Create spacetime
        </Button>
        <Button variant="ghost" size="sm" onClick={onCancel} disabled={create.isPending}>
          Cancel
        </Button>
        {create.isError ? (
          <span className="text-[12px] text-danger">{errorMessage(create.error)}</span>
        ) : null}
      </div>
    </div>
  )
}
