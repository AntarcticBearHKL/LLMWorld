import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export function WorldBadge({ frozen, className }: { frozen: boolean; className?: string }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "label-latin",
        frozen
          ? "border-info/40 bg-info/10 text-info"
          : "border-border-strong bg-surface-2 text-fg-muted",
        className,
      )}
    >
      {frozen ? "Frozen" : "Draft"}
    </Badge>
  )
}
