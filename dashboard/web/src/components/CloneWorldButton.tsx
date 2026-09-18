import { useState } from "react"

import { Copy, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useCloneWorld } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { cn } from "@/lib/utils"
import { randomWorldId } from "@/lib/world"

const FIELD_CLASS = "h-7 w-36 px-2 t-body"

interface CloneWorldButtonProps {
  world: string
  size?: "xs" | "sm"
  variant?: "outline" | "ghost"
  label?: string
  "aria-label"?: string
  className?: string
  onCloned?: (worldId: string) => void
}

export function CloneWorldButton({
  world,
  size = "xs",
  variant = "outline",
  label = "Clone",
  "aria-label": ariaLabel,
  className,
  onCloned,
}: CloneWorldButtonProps) {
  const clone = useCloneWorld()
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState("")

  const start = () => {
      setDraft(randomWorldId([world]))
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
        variant={variant}
        size={size}
        className={className}
        onClick={start}
        title="Copy this world (households included) into a new draft"
        aria-label={ariaLabel}
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
          placeholder="world_fish"
        autoFocus
        className={cn(FIELD_CLASS, "num")}
      />
      <Button size={size} onClick={submit} disabled={clone.isPending || draft.trim().length === 0}>
        {clone.isPending ? <Loader2 className="animate-spin" /> : <Copy />}
        {label || "Clone"}
      </Button>
      <Button variant="ghost" size={size} onClick={cancel} disabled={clone.isPending}>
        Cancel
      </Button>
      {clone.isError ? (
        <span className="w-full t-caption text-danger">{errorMessage(clone.error)}</span>
      ) : null}
    </span>
  )
}
