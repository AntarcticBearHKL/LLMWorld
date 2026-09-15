import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export function WorldBadge({ frozen, className }: { frozen: boolean; className?: string }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "label-latin",
        frozen ? "border-info/50 text-info" : "border-border-strong text-fg-muted",
        className,
      )}
    >
      {frozen ? "Frozen" : "Draft"}
    </Badge>
  )
}
