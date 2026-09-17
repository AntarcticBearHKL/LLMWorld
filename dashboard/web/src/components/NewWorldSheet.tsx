import * as React from "react"

import { Plus } from "lucide-react"

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
import { useCreateWorld } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { randomWorldId } from "@/lib/world"

const PANEL = "min-h-0 flex-1 overflow-y-auto p-4"

export function NewWorldSheet(props: {
  worldIds: string[]
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreated: (worldId: string) => void
}): React.JSX.Element {
  const { worldIds, open, onOpenChange, onCreated } = props
  const create = useCreateWorld()
  const [draft, setDraft] = React.useState("")
  const takenKey = worldIds.join("|")
  const suggested = React.useMemo(
    () => randomWorldId(takenKey === "" ? [] : takenKey.split("|")),
    [takenKey],
  )

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const worldId = draft.trim().length > 0 ? draft.trim() : suggested
    create.mutate(
      { world_id: worldId },
      {
        onSuccess: (result) => {
          setDraft("")
          onCreated(result.world_id)
        },
      },
    )
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="center" className="flex flex-col gap-0 sm:max-w-lg">
        <SheetHeader className="border-b border-border">
          <SheetTitle>New world</SheetTitle>
          <SheetDescription>
            A world is a fixed set of blocks and households. Creating one is local — no LLM calls.
          </SheetDescription>
        </SheetHeader>

        <div className={PANEL}>
          <form onSubmit={onSubmit} className="flex flex-col gap-1.5">
            <Label htmlFor="new-world-id" className="label-micro text-fg-muted">
              World ID (blank = use the suggested id)
            </Label>
            <Input
              id="new-world-id"
              value={draft}
              placeholder={suggested}
              onChange={(event) => setDraft(event.target.value)}
              className="num h-8 w-full px-2.5 text-[14px]"
            />
            <div className="flex flex-wrap items-center gap-2">
              <Button size="sm" type="submit" disabled={create.isPending}>
                <Plus />
                New blank world
              </Button>
            </div>
            <p className="text-[12px] text-fg-subtle">
              Households are a world&apos;s fixed physics — scenarios replay them under their own
              policy and dates.
            </p>
            {create.isError ? (
              <p className="text-[12px] text-danger">Create failed: {errorMessage(create.error)}</p>
            ) : null}
          </form>
        </div>
      </SheetContent>
    </Sheet>
  )
}
