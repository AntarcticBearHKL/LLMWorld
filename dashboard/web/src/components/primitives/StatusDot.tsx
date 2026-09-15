import { cn } from "@/lib/utils"

interface StatusDotProps {
  on: boolean
  className?: string
  title?: string
}

export function StatusDot({ on, className, title }: StatusDotProps) {
  return (
    <span
      title={title}
      aria-hidden={title === undefined ? true : undefined}
      className={cn(
        "inline-block size-2 shrink-0 rounded-full border transition-colors duration-150",
        on ? "border-energy bg-energy" : "border-border-strong bg-transparent",
        className,
      )}
    />
  )
}
