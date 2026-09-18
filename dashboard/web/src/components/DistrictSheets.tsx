import * as React from "react"

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus, Save } from "lucide-react"

import { USE_MOCK, updateDistrict } from "@/api/client"
import type { DistrictInfo, DistrictUpdateRequest, JobRequest } from "@/api/types"
import { MOCK_REASON } from "@/components/BuildStepCard"
import { DistrictPromptFields } from "@/components/DistrictPromptFields"
import { HouseholdPreview } from "@/components/HouseholdPreview"
import { JobSubmitBar } from "@/components/JobSubmitBar"
import { WorldBuilder } from "@/components/WorldBuilder"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Textarea } from "@/components/ui/textarea"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { useJobs } from "@/hooks/useJobs"
import { isActiveJob, useCreateDistrict, worldKeys } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { randomDistrictId } from "@/lib/world"

const PANEL = "min-h-0 flex-1 overflow-y-auto p-4"
const NOT_RUNNABLE = "This district is not runnable right now."
const NOTHING_CHOSEN = "Write a prompt or pick a preset — nothing is chosen for you."

export function NewDistrictSheet(props: {
  world: string
  districtNames: string[]
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreated: (name: string) => void
}): React.JSX.Element {
  const { world, districtNames, open, onOpenChange, onCreated } = props
  const create = useCreateDistrict(world)
  const [draft, setDraft] = React.useState("")
  const [createdHere, setCreatedHere] = React.useState<string[]>([])
  const takenKey = React.useMemo(
    () => Array.from(new Set([...districtNames, ...createdHere])).sort().join("|"),
    [districtNames, createdHere],
  )
  const takenNames = React.useMemo(
    () => (takenKey === "" ? [] : takenKey.split("|")),
    [takenKey],
  )
  const suggested = React.useMemo(
    () => randomDistrictId(takenNames),
    [takenNames],
  )

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const typed = draft.trim()
    const proposed = typed.length > 0 ? typed : suggested
    const name =
      typed.length === 0 && takenNames.includes(proposed)
        ? randomDistrictId(takenNames)
        : proposed
    create.mutate(
      { name },
      {
        onSuccess: (data) => {
          setDraft("")
          setCreatedHere((prev) => (prev.includes(data.name) ? prev : [...prev, data.name]))
          onCreated(data.name)
        },
      },
    )
  }

  return (
    <Sheet
      open={open}
      onOpenChange={(next) => {
        if (next) setCreatedHere([])
        onOpenChange(next)
      }}
    >
        <SheetContent side="center" className="flex flex-col gap-0 sm:max-w-lg">
        <SheetHeader className="border-b border-border">
          <SheetTitle>New district</SheetTitle>
          <SheetDescription>
            Add a district to <span className="num">{world}</span>. A blank name uses the suggested
            id.
          </SheetDescription>
        </SheetHeader>

        <div className={PANEL}>
          <form onSubmit={onSubmit} className="flex flex-col gap-1.5">
            <Label htmlFor="new-district-name" className="label-micro text-fg-muted">
              New district (blank = use the suggested id)
            </Label>
            <div className="flex flex-wrap items-center gap-2">
              <Input
                id="new-district-name"
                value={draft}
                placeholder={suggested}
                onChange={(event) => setDraft(event.target.value)}
                className="num h-8 w-full px-2.5 t-title"
              />
              <Button size="sm" type="submit" disabled={create.isPending}>
                <Plus />
                Create district
              </Button>
            </div>
            <p className="t-caption text-fg-subtle">
              A blank name uses the suggested <span className="num">district_&lt;word&gt;</span> id
              shown above. Creating a district is local — no LLM calls.
            </p>
            {create.isError ? (
              <p className="t-caption text-danger">Create failed: {errorMessage(create.error)}</p>
            ) : null}
            {create.isSuccess ? (
              <p className="num t-caption text-success">
                District {create.data.name}{" "}
                {create.data.created ? "created" : "already existed — nothing changed"}.
              </p>
            ) : null}
          </form>
        </div>
      </SheetContent>
    </Sheet>
  )
}

function useSaveDistrict(world: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (vars: { name: string; payload: DistrictUpdateRequest }) =>
      updateDistrict(world, vars.name, vars.payload),
    onSuccess: (_district, vars) => {
      void queryClient.invalidateQueries({ queryKey: worldKeys.districts(world) })
      void queryClient.invalidateQueries({ queryKey: worldKeys.build(world, vars.name) })
    },
  })
}

function DescriptionBody({
  world,
  district,
  target,
  onTargetChange,
  onRenamed,
  districtRunnable,
  districtBlockedReason,
}: {
  world: string
  district: DistrictInfo
  target: string
  onTargetChange: (name: string) => void
  onRenamed?: (oldName: string, newName: string) => void
  districtRunnable: boolean
  districtBlockedReason: string | null
}): React.JSX.Element {
  const save = useSaveDistrict(world)
  const [prompt, setPrompt] = React.useState("")
  const [name, setName] = React.useState(district.name)
  const [description, setDescription] = React.useState(district.description)
  const [saved, setSaved] = React.useState({
    name: district.name,
    description: district.description,
  })
  const [nameError, setNameError] = React.useState<string | null>(null)
  const trimmedPrompt = prompt.trim()
  const trimmedName = name.trim()
  const trimmedDescription = description.trim()
  const nameChanged = trimmedName !== saved.name
  const descriptionChanged = trimmedDescription !== saved.description
  const dirty = nameChanged || descriptionChanged
  const nothingChosen = trimmedPrompt.length === 0
  const jobs = useJobs().data ?? []
  const districtJobInFlight = jobs.some(
    (job) =>
      job.kind === "build" &&
      job.world === world &&
      job.step === "district" &&
      (job.district ?? "") === target &&
      isActiveJob(job),
  )

  const payload: JobRequest = {
    kind: "build",
    world,
    district: target,
    step: "district",
  }
  if (trimmedPrompt.length > 0) payload.prompt = trimmedPrompt

  const onSave = () => {
    if (trimmedName.length === 0) {
      setNameError("A district needs a name — a blank rename is refused, not skipped.")
      return
    }
    setNameError(null)
    if (!dirty) return
    const patch: DistrictUpdateRequest = {}
    if (nameChanged) patch.name = trimmedName
    if (descriptionChanged) patch.description = trimmedDescription
    save.mutate(
      { name: target, payload: patch },
      {
        onSuccess: (updated) => {
          const oldName = target
          setSaved({ name: updated.name, description: updated.description })
          setName(updated.name)
          setDescription(updated.description)
          onTargetChange(updated.name)
          if (updated.name !== oldName) onRenamed?.(oldName, updated.name)
        },
      },
    )
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="district-description-name" className="label-micro text-fg-muted">
            Name
          </Label>
          <Input
            id="district-description-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="num h-8 w-full px-2.5 t-title"
          />
          {nameError !== null ? <p className="t-caption text-danger">{nameError}</p> : null}
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="district-description-text" className="label-micro text-fg-muted">
            Description
          </Label>
          <Textarea
            id="district-description-text"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            className="min-h-32 t-body whitespace-pre-wrap"
          />
          {!district.has_description ? (
            <p className="t-caption text-fg-subtle">
              {target} has no description yet — write a prompt below and the LLM rewrites it into
              one, then saves it.
            </p>
          ) : district.description.length === 0 ? (
            <p className="t-caption text-fg-subtle">
              The description file for {target} exists, but its text is not inlined here.
            </p>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm" type="button" onClick={onSave} disabled={save.isPending || !dirty}>
            <Save />
            {save.isPending ? "Saving…" : nameChanged ? "Save changes & rename" : "Save description"}
          </Button>
          <span className="t-caption text-fg-subtle">
            {dirty ? "Only the fields you changed are sent." : "Everything matches what is saved."}
          </span>
        </div>
        {save.isError ? (
          <p className="t-caption text-danger">Save failed: {errorMessage(save.error)}</p>
        ) : null}
        {save.isSuccess && !dirty ? (
          <p className="num t-caption text-success">Saved {saved.name}.</p>
        ) : null}
      </div>

      <DistrictPromptFields
        prompt={prompt}
        disabled={!districtRunnable}
        onPromptChange={setPrompt}
      />

      <div className="lg:col-span-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="inline-flex w-full [&>div]:w-full">
              <JobSubmitBar
                key={`${district.name}-${trimmedPrompt.length > 0 ? "custom" : "none"}`}
                label="Optimize"
                payload={payload}
                disabled={USE_MOCK || !districtRunnable || nothingChosen || districtJobInFlight}
                disabledReason={
                  USE_MOCK
                    ? MOCK_REASON
                    : !districtRunnable
                      ? (districtBlockedReason ?? NOT_RUNNABLE)
                      : nothingChosen
                        ? NOTHING_CHOSEN
                        : undefined
                }
                showEstimate={false}
              />
            </span>
          </TooltipTrigger>
          {districtJobInFlight ? (
            <TooltipContent>Waiting for the running job to finish</TooltipContent>
          ) : null}
        </Tooltip>
      </div>
    </div>
  )
}

export function DistrictDescriptionSheet(props: {
  world: string
  district: DistrictInfo | null
  districtRunnable: boolean
  districtBlockedReason: string | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onRenamed?: (oldName: string, newName: string) => void
}): React.JSX.Element {
  const { world, district, districtRunnable, districtBlockedReason, open, onOpenChange, onRenamed } =
    props
  const selectedName = district?.name ?? ""
  const [target, setTarget] = React.useState(selectedName)
  const [syncedName, setSyncedName] = React.useState(selectedName)
  if (syncedName !== selectedName) {
    setSyncedName(selectedName)
    setTarget(selectedName)
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="center" className="flex flex-col gap-0 sm:max-w-2xl">
        <SheetHeader className="border-b border-border">
          <SheetTitle>District description</SheetTitle>
          <SheetDescription>
            {district === null ? "No district selected." : target}
          </SheetDescription>
        </SheetHeader>

        <div className={PANEL}>
          {district === null ? null : (
            <DescriptionBody
              key={district.name}
              world={world}
              district={district}
              target={target}
              onTargetChange={setTarget}
              onRenamed={onRenamed}
              districtRunnable={districtRunnable}
              districtBlockedReason={districtBlockedReason}
            />
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}

export function HouseholdSheet(props: {
  world: string
  district: string
  house: string
  homeDone: boolean
  homeRunnable: boolean
  homeBlockedReason: string | null
  open: boolean
  onOpenChange: (open: boolean) => void
}): React.JSX.Element {
  const { world, district, house, homeDone, homeRunnable, homeBlockedReason, open, onOpenChange } =
    props
  const homePayload: JobRequest = { kind: "build", world, district, step: "home", house }
  const jobs = useJobs().data ?? []
  const homeJobInFlight = jobs.some(
    (job) =>
      job.kind === "build" &&
      job.world === world &&
      job.step === "home" &&
      (job.district ?? "") === district &&
      job.house === house &&
      isActiveJob(job),
  )

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="center" className="flex flex-col gap-0 sm:max-w-lg">
        <SheetHeader className="border-b border-border">
          <SheetTitle>Household</SheetTitle>
          <SheetDescription>{house === "" ? "No household selected." : house}</SheetDescription>
        </SheetHeader>

        <div className={PANEL}>
          {house === "" ? null : homeDone ? (
            <HouseholdPreview world={world} district={district} house={house} />
          ) : (
            <div className="flex flex-col gap-3">
              <p className="t-caption text-fg-subtle">
                No home for {house} yet — generate its rooms and appliances to preview them here.
              </p>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="inline-flex w-full [&>div]:w-full">
                    <JobSubmitBar
                      key={`${house}-home`}
                      payload={homePayload}
                      disabled={USE_MOCK || !homeRunnable || homeJobInFlight}
                      disabledReason={
                        USE_MOCK
                          ? MOCK_REASON
                          : !homeRunnable
                            ? (homeBlockedReason ?? "This household is not runnable right now.")
                            : undefined
                      }
                    />
                  </span>
                </TooltipTrigger>
                {homeJobInFlight ? (
                  <TooltipContent>Waiting for the running job to finish</TooltipContent>
                ) : null}
              </Tooltip>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}

export function DistrictStepsSheet(props: {
  world: string
  district: string
  open: boolean
  onOpenChange: (open: boolean) => void
}): React.JSX.Element {
  const { world, district, open, onOpenChange } = props

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="center" className="flex flex-col gap-0 sm:max-w-lg">
        <SheetHeader className="border-b border-border">
          <SheetTitle>Steps</SheetTitle>
          <SheetDescription>
            Run the pipeline steps for this district: district → household → home.
          </SheetDescription>
        </SheetHeader>

        <div className={PANEL}>
          {district === "" ? null : <WorldBuilder world={world} district={district} />}
        </div>
      </SheetContent>
    </Sheet>
  )
}
