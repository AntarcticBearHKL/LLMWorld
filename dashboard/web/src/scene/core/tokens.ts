import { useEffect, useState } from "react"

export interface SceneTokens {
  bg: string
  surface: string
  surface2: string
  surface3: string
  border: string
  borderStrong: string
  fg: string
  fgMuted: string
  fgSubtle: string
  brand: string
  energy: string
  danger: string
  success: string
  member: string[]
}

const FALLBACK: SceneTokens = {
  bg: "#0a0f12",
  surface: "#0f161a",
  surface2: "#141d22",
  surface3: "#1a252b",
  border: "#1e2a30",
  borderStrong: "#2a3840",
  fg: "#e7edf0",
  fgMuted: "#93a4ac",
  fgSubtle: "#64757e",
  brand: "#2fc4b2",
  energy: "#f5a524",
  danger: "#f2555a",
  success: "#3dd68c",
  member: ["#2fc4b2", "#7c9cff", "#c084fc", "#fb923c"],
}

const MEMBER_VARS = ["--member-1", "--member-2", "--member-3", "--member-4"] as const

const read = (style: CSSStyleDeclaration, name: string, fallback: string): string => {
  const value = style.getPropertyValue(name).trim()
  return value.length > 0 ? value : fallback
}

export const resolveSceneTokens = (): SceneTokens => {
  if (typeof document === "undefined") return FALLBACK
  const style = getComputedStyle(document.documentElement)
  return {
    bg: read(style, "--bg", FALLBACK.bg),
    surface: read(style, "--surface", FALLBACK.surface),
    surface2: read(style, "--surface-2", FALLBACK.surface2),
    surface3: read(style, "--surface-3", FALLBACK.surface3),
    border: read(style, "--border", FALLBACK.border),
    borderStrong: read(style, "--border-strong", FALLBACK.borderStrong),
    fg: read(style, "--fg", FALLBACK.fg),
    fgMuted: read(style, "--fg-muted", FALLBACK.fgMuted),
    fgSubtle: read(style, "--fg-subtle", FALLBACK.fgSubtle),
    brand: read(style, "--brand", FALLBACK.brand),
    energy: read(style, "--energy", FALLBACK.energy),
    danger: read(style, "--danger", FALLBACK.danger),
    success: read(style, "--success", FALLBACK.success),
    member: MEMBER_VARS.map((name, index) => read(style, name, FALLBACK.member[index] ?? FALLBACK.brand)),
  }
}

export function useSceneTokens(): SceneTokens {
  const [tokens, setTokens] = useState<SceneTokens>(resolveSceneTokens)
  useEffect(() => {
    const observer = new MutationObserver(() => setTokens(resolveSceneTokens()))
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] })
    return () => observer.disconnect()
  }, [])
  return tokens
}

export const prefersReducedMotion = (): boolean =>
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches
