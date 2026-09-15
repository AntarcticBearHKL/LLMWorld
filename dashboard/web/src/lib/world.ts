export const randomWorldId = (): string => {
  const bytes = crypto.getRandomValues(new Uint8Array(3))
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("")
  return `world_${hex}`
}
