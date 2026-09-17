import * as React from "react"

import { USE_MOCK } from "@/api/client"
import type { DistrictStatus, JobRequest } from "@/api/types"
import { MOCK_REASON } from "@/components/BuildStepCard"
import { JobSubmitBar } from "@/components/JobSubmitBar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"

const MIN_COUNT = 1
const MAX_COUNT = 50
const COUNT_INVALID = `Enter a whole number from ${MIN_COUNT} to ${MAX_COUNT}.`

export function AddHouseholdsSheet(props: {
  world: string
  district: string
  districtStatus: DistrictStatus
  open: boolean
  onOpenChange: (open: boolean) => void
}): React.JSX.Element {
  const { world, district, districtStatus, open, onOpenChange } = props
  const [count, setCount] = React.useState(1)

  const gate =
    districtStatus === "locked"
      ? null
      : districtStatus === "uninitialized"
        ? "Write the district description first."
        : "Lock this district first."

  const countValid = Number.isInteger(count) && count >= MIN_COUNT && count <= MAX_COUNT
  const payload: JobRequest = { kind: "build", world, district, step: "household", count }
  const disabledReason = USE_MOCK
    ? MOCK_REASON
    : gate !== null
      ? gate
      : countValid
        ? undefined
        : COUNT_INVALID

  return (
    <Sheet
      open={open}
      onOpenChange={(next) => {
        if (next) setCount(1)
        onOpenChange(next)
      }}
    >
      <SheetContent side="center" className="flex flex-col gap-0 sm:max-w-lg">
        <SheetHeader className="border-b border-border">
          <SheetTitle>Add households</SheetTitle>
          <SheetDescription>
            Add households to <span className="num">{district}</span> in{" "}
            <span className="num">{world}</span>.
          </SheetDescription>
        </SheetHeader>

        <div className="min-h-0 flex-1 overflow-y-auto p-4">
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="add-households-count" className="label-micro text-fg-muted">
                How many households to add?
              </Label>
              <Input
                id="add-households-count"
                type="number"
                min={MIN_COUNT}
                max={MAX_COUNT}
                step={1}
                value={Number.isFinite(count) ? count : ""}
                onChange={(event) => setCount(event.target.valueAsNumber)}
                className="num h-8 w-full px-2.5 t-body"
              />
            </div>

            <p className="t-caption text-fg-subtle">
              One LLM call writes this many household descriptions from the district description.
              They start as described households — members come next.
            </p>

            <JobSubmitBar
              payload={payload}
              label="Add households"
              disabled={disabledReason !== undefined}
              disabledReason={disabledReason}
            />
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
