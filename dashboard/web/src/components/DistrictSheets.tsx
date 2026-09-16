import * as React from "react"

import { Plus } from "lucide-react"

import { USE_MOCK } from "@/api/client"
import type { DistrictInfo, JobRequest } from "@/api/types"
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
import { useCreateDistrict, useDistrictPresets } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { randomDistrictId } from "@/lib/world"

const PANEL = "min-h-0 flex-1 overflow-y-auto p-4"
const NOT_RUNNABLE = "This district is not runnable right now."

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
  const takenKey = districtNames.join("|")
  const suggested = React.useMemo(
    () => randomDistrictId(takenKey === "" ? [] : takenKey.split("|")),
    [takenKey],
  )

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const typed = draft.trim()
    const name = typed.length > 0 ? typed : suggested
    create.mutate(
      { name },
      {
        onSuccess: (data) => {
          setDraft("")
          onCreated(data.name)
        },
      },
    )
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex w-full flex-col gap-0 sm:max-w-lg">
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
                className="num h-8 w-full px-2.5 text-[14px]"
              />
              <Button size="sm" type="submit" disabled={create.isPending}>
                <Plus />
                Create district
              </Button>
            </div>
            <p className="text-[12px] text-fg-subtle">
              A blank name uses the suggested <span className="num">district_&lt;word&gt;</span> id
              shown above. Creating a district is local — no LLM calls.
            </p>
            {create.isError ? (
              <p className="text-[12px] text-danger">Create failed: {errorMessage(create.error)}</p>
            ) : null}
            {create.isSuccess ? (
              <p className="num text-[12px] text-success">
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

function DescriptionBody({
  world,
  district,
  districtRunnable,
  districtBlockedReason,
}: {
  world: string
  district: DistrictInfo
  districtRunnable: boolean
  districtBlockedReason: string | null
}): React.JSX.Element {
  const presetsQuery = useDistrictPresets()
  const [preset, setPreset] = React.useState("")
  const [prompt, setPrompt] = React.useState("")
  const trimmedPrompt = prompt.trim()

  const payload: JobRequest = {
    kind: "build",
    world,
    district: district.name,
    step: "district",
  }
  if (trimmedPrompt.length > 0) payload.prompt = trimmedPrompt
  else if (preset.length > 0) payload.preset = preset

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <span className="label-micro">Description</span>
        {!district.has_description ? (
          <p className="text-[13px] text-fg-subtle">
            No description yet — generate one from a preset or write a custom prompt.
          </p>
        ) : district.description.length === 0 ? (
          <p className="text-[13px] text-fg-subtle">
            The description file for {district.name} exists, but its text is not inlined here.
          </p>
        ) : (
          <p className="text-[13px] leading-relaxed whitespace-pre-wrap text-fg-muted">
            {district.description}
          </p>
        )}
      </div>

      <div className="border-t border-border" />

      <div className="flex flex-col gap-3">
        <DistrictPromptFields
          presets={presetsQuery.data ?? []}
          presetsPending={presetsQuery.isPending}
          preset={preset}
          prompt={prompt}
          disabled={!districtRunnable}
          onPresetChange={setPreset}
          onPromptChange={setPrompt}
        />
        <JobSubmitBar
          key={`${district.name}-${preset}-${trimmedPrompt.length > 0 ? "custom" : "none"}`}
          payload={payload}
          disabled={USE_MOCK || !districtRunnable}
          disabledReason={
            USE_MOCK ? MOCK_REASON : (districtBlockedReason ?? NOT_RUNNABLE)
          }
        />
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
}): React.JSX.Element {
  const { world, district, districtRunnable, districtBlockedReason, open, onOpenChange } = props

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex w-full flex-col gap-0 sm:max-w-lg">
        <SheetHeader className="border-b border-border">
          <SheetTitle>District description</SheetTitle>
          <SheetDescription>
            {district === null ? "No district selected." : district.name}
          </SheetDescription>
        </SheetHeader>

        <div className={PANEL}>
          {district === null ? null : (
            <DescriptionBody
              world={world}
              district={district}
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

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex w-full flex-col gap-0 sm:max-w-lg">
        <SheetHeader className="border-b border-border">
          <SheetTitle>Household</SheetTitle>
          <SheetDescription>{house === "" ? "No household selected." : house}</SheetDescription>
        </SheetHeader>

        <div className={PANEL}>
          {house === "" ? null : homeDone ? (
            <HouseholdPreview world={world} district={district} house={house} />
          ) : (
            <div className="flex flex-col gap-3">
              <p className="text-[12px] text-fg-subtle">
                No home for {house} yet — generate its rooms and appliances to preview them here.
              </p>
              <JobSubmitBar
                key={`${house}-home`}
                payload={homePayload}
                disabled={USE_MOCK || !homeRunnable}
                disabledReason={
                  USE_MOCK
                    ? MOCK_REASON
                    : (homeBlockedReason ?? "This household is not runnable right now.")
                }
              />
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
      <SheetContent side="right" className="flex w-full flex-col gap-0 sm:max-w-lg">
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
