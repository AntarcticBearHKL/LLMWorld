import { useState } from "react"

import { Copy, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useCloneWorld } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { cn } from "@/lib/utils"
import { randomWorldId } from "@/lib/world"

const FIELD_CLASS =
  "h-7 w-36 rounded-md border-border-strong bg-surface-2 px-2 text-[11px] text-fg focus-visible:border-brand"

interface CloneWorldButtonProps {
  world: string
  size?: "xs" | "sm"
  label?: string
  className?: string
  onCloned?: (worldId: string) => void
}

export function CloneWorldButton({
  world,
  size = "xs",
  label = "Clone",
  className,
  onCloned,
}: CloneWorldButtonProps) {
  const clone = useCloneWorld()
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState("")

  const start = () => {
    setDraft(randomWorldId())
    setOpen(true)
  }

  const cancel = () => {
    setOpen(false)
    clone.reset()
  }

  const submit = () => {
    const newId = draft.trim()
    if (newId.length === 0 || clone.isPending) return
    clone.mutate(
      { world, newId },
      {
        onSuccess: (result) => {
          setOpen(false)
          onCloned?.(result.world_id)
        },
      },
    )
  }

  if (!open) {
    return (
      <Button
        variant="outline"
        size={size}
        className={className}
        onClick={start}
        title="Copy this world (households included) into a new draft"
      >
        <Copy />
        {label}
      </Button>
    )
  }

  return (
    <span className={cn("flex flex-wrap items-center gap-1.5", className)}>
      <Input
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") submit()
          if (event.key === "Escape") cancel()
        }}
        aria-label="New world id"
        placeholder="world_9f3a1c"
        autoFocus
        className={cn(FIELD_CLASS, "num")}
      />
      <Button size={size} onClick={submit} disabled={clone.isPending || draft.trim().length === 0}>
        {clone.isPending ? <Loader2 className="animate-spin" /> : <Copy />}
        {label}
      </Button>
      <Button variant="ghost" size={size} onClick={cancel} disabled={clone.isPending}>
        Cancel
      </Button>
      {clone.isError ? (
        <span className="w-full text-[10px] text-danger">{errorMessage(clone.error)}</span>
      ) : null}
    </span>
  )
}
