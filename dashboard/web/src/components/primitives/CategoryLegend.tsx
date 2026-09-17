import { ACTIVITY_CATEGORIES, CATEGORY_DESCRIPTIONS, CATEGORY_LABELS } from "@/lib/activity"
import { cn } from "@/lib/utils"

interface CategoryLegendProps {
  className?: string
  activeOnly?: boolean
}

export function CategoryLegend({ className, activeOnly = false }: CategoryLegendProps) {
  const items = activeOnly ? ACTIVITY_CATEGORIES.slice(1, 5) : ACTIVITY_CATEGORIES
  return (
    <ul className={cn("flex flex-wrap items-center gap-x-3 gap-y-1", className)}>
      {items.map((category) => (
        <li key={category} className="flex items-center gap-1.5">
          <span
            aria-hidden
            className={cn(
              "size-2.5 shrink-0 rounded-[3px] border",
              category === "away" && "border-dashed",
            )}
            style={{
              backgroundColor: `color-mix(in srgb, var(--cat-${category}) 30%, transparent)`,
              borderColor: `var(--cat-${category})`,
            }}
          />
          <span className="t-caption text-fg-muted" title={CATEGORY_DESCRIPTIONS[category]}>
            {CATEGORY_LABELS[category]}
          </span>
        </li>
      ))}
    </ul>
  )
}
