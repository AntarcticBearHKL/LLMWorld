import { cn } from "@/lib/utils"

export function WorldBadge({ frozen, className }: { frozen: boolean; className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-1.5", className)}>
      <span
        aria-hidden
        className={cn(
          "size-1.5 shrink-0 rounded-full border",
          frozen ? "border-info bg-info" : "border-border-strong bg-transparent",
        )}
      />
      <span className={cn("label-latin whitespace-nowrap", frozen ? "text-info" : "text-fg-muted")}>
        {frozen ? "Frozen" : "Draft"}
      </span>
    </span>
  )
}
