import * as React from "react"

import type { JobRequest } from "@/api/types"
import { JobSubmitBar } from "@/components/JobSubmitBar"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"

export function ComposeHouseholdSheet(props: {
  world: string
  district: string
  house: string
  open: boolean
  onOpenChange: (open: boolean) => void
}): React.JSX.Element {
  const { world, district, house, open, onOpenChange } = props
  const payload: JobRequest = { kind: "build", world, district, step: "household", house }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="center" className="flex flex-col gap-0 sm:max-w-lg">
        <SheetHeader className="border-b border-border">
          <SheetTitle>Compose members</SheetTitle>
          <SheetDescription>
            Compose the members of <span className="num">{house}</span> in{" "}
            <span className="num">{district}</span>, <span className="num">{world}</span>.
          </SheetDescription>
        </SheetHeader>

        <div className="min-h-0 flex-1 overflow-y-auto p-4">
          <div className="flex flex-col gap-3">
            <p className="t-caption text-fg-subtle">
              This household already has its description. Composing turns that brief into its
              members — one LLM call — so the residents match the description you reviewed.
            </p>

            <JobSubmitBar payload={payload} label="Compose members" />
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
