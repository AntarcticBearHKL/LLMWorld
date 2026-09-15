import { cn } from "@/lib/utils"

interface MemberTagProps {
  member: string
  bedroom?: string | null
  lane: number
  selected?: boolean
  onClick?: () => void
  className?: string
}

export function MemberTag({ member, bedroom, lane, selected = false, onClick, className }: MemberTagProps) {
  const Wrapper = onClick === undefined ? "div" : "button"
  return (
    <Wrapper
      type={onClick === undefined ? undefined : "button"}
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-2 px-3 text-left",
        onClick !== undefined && "cursor-pointer",
        className,
      )}
    >
      <span
        aria-hidden
        className="h-4 w-[3px] shrink-0 rounded-full"
        style={{ backgroundColor: `var(--member-${lane})` }}
      />
      <span className="flex min-w-0 flex-col leading-tight">
        <span
          className={cn(
            "truncate text-[12px] font-semibold transition-colors",
            selected ? "text-brand" : "text-fg",
          )}
        >
          {member}
        </span>
        {bedroom !== null && bedroom !== undefined ? (
          <span className="truncate text-[10px] text-fg-subtle">{bedroom}</span>
        ) : null}
      </span>
    </Wrapper>
  )
}
