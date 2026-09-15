import * as React from "react"
import { cn } from "@/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "flex field-sizing-content min-h-16 w-full rounded-md border border-border-strong bg-surface px-3 py-2 text-base transition-[color,border-color,box-shadow] outline-none placeholder:text-fg-subtle selection:bg-brand selection:text-brand-fg focus-visible:border-brand-ring focus-visible:ring-[3px] focus-visible:ring-brand-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm dark:bg-surface-2",
        "aria-invalid:border-destructive aria-invalid:ring-destructive/20",
        className,
      )}
      {...props}
    />
  )
}

export { Textarea }
