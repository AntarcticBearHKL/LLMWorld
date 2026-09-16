import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

interface MetricCellProps {
  label: string
  value: ReactNode
  unit?: string
  detail?: ReactNode
  tone?: "default" | "energy" | "brand"
  className?: string
}

const TONE_CLASS: Record<NonNullable<MetricCellProps["tone"]>, string> = {
  default: "text-fg",
  energy: "text-energy",
  brand: "text-brand",
}

export function MetricCell({ label, value, unit, detail, tone = "default", className }: MetricCellProps) {
  return (
    <div className={cn("flex min-w-[104px] flex-col gap-0.5", className)}>
      <span className="label-micro whitespace-nowrap">{label}</span>
      <span className="flex items-baseline gap-1">
        <span className={cn("num text-[22px] leading-[1.15] font-medium tracking-[-0.01em]", TONE_CLASS[tone])}>
          {value}
        </span>
        {unit !== undefined ? <span className="label-latin">{unit}</span> : null}
      </span>
      {detail !== undefined ? (
        <span className="num text-[12px] leading-none text-fg-subtle">{detail}</span>
      ) : null}
    </div>
  )
}
