import { cn } from "@/lib/utils"

interface PlaceholderBadgeProps {
  milestone: string
  className?: string
}

export function PlaceholderBadge({ milestone, className }: PlaceholderBadgeProps) {
  return (
    <span
      className={cn(
        "rounded-sm border border-border-strong bg-surface-2 px-1.5 py-0.5 text-[10px] font-semibold tracking-[0.1em] text-fg-subtle",
        className,
      )}
    >
      待实现 · {milestone}
    </span>
  )
}

interface PlaceholderNoteProps {
  children: React.ReactNode
  className?: string
}

export function PlaceholderNote({ children, className }: PlaceholderNoteProps) {
  return (
    <p className={cn("text-[11px] leading-relaxed text-fg-subtle", className)}>{children}</p>
  )
}
