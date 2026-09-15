/** 成员配色与首字母，供时间轴 / 平面图 / 快照共用，保证同一人处处同色。 */

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

/** "Member 3" -> "3"；无数字则取前两个字符。 */
export function memberInitial(memberId: string): string {
  const digits = memberId.match(/\d+/)
  if (digits !== null) return digits[0]
  return memberId.slice(0, 2)
}
