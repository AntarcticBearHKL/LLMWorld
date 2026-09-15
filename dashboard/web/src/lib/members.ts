/** Member colours and initials, shared by the timeline / floor plan / snapshot so one person keeps one colour. */

const MEMBER_VARS = [
  "var(--member-1)",
  "var(--member-2)",
  "var(--member-3)",
  "var(--member-4)",
] as const

export function memberColorVar(memberId: string, allMembers: readonly string[]): string {
  const index = allMembers.indexOf(memberId)
  if (index < 0) return "var(--fg-subtle)"
  return MEMBER_VARS[index % MEMBER_VARS.length] ?? "var(--fg-subtle)"
}

/** "Member 3" -> "3"; without digits, the first two characters. */
export function memberInitial(memberId: string): string {
  const digits = memberId.match(/\d+/)
  if (digits !== null) return digits[0]
  return memberId.slice(0, 2)
}
