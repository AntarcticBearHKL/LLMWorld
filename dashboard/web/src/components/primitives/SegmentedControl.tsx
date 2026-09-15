import { cn } from "@/lib/utils"

export interface SegmentedOption<T extends string> {
  value: T
  label: string
  hint?: string
}

interface SegmentedControlProps<T extends string> {
  options: ReadonlyArray<SegmentedOption<T>>
  value: T
  onChange: (value: T) => void
  label: string
  className?: string
}

export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
  label,
  className,
}: SegmentedControlProps<T>) {
  return (
    <div
      role="group"
      aria-label={label}
      className={cn(
        "flex items-center gap-0.5 rounded-md border border-border bg-surface-2 p-0.5",
        className,
      )}
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          aria-pressed={value === option.value}
          title={option.hint}
          className={cn(
            "rounded-sm px-2.5 py-1 text-[12px] font-medium transition-colors",
            value === option.value
              ? "bg-brand-soft text-brand"
              : "text-fg-muted hover:bg-surface-3 hover:text-fg",
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
