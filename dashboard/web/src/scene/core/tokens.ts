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
  bg: "#181715",
  surface: "#1f1d1a",
  surface2: "#292524",
  surface3: "#33302b",
  border: "#44403c",
  borderStrong: "#57534e",
  fg: "#f5f5f4",
  fgMuted: "#d6d3d1",
  fgSubtle: "#a8a29e",
  brand: "#fafafa",
  energy: "#e9a94a",
  danger: "#ef6f6b",
  success: "#57c98e",
  member: ["#8a9bb5", "#a3b393", "#c2a882", "#b39ab3"],
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
