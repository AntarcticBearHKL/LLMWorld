import { useCallback, useEffect, useState } from "react"

export type ThemeMode = "dark" | "light"

const STORAGE_KEY = "llmworld.theme"

const readTheme = (): ThemeMode => {
  if (typeof window === "undefined") return "dark"
  const stored = window.localStorage.getItem(STORAGE_KEY)
  return stored === "light" ? "light" : "dark"
}

export function useTheme(): { theme: ThemeMode; toggleTheme: () => void } {
  const [theme, setTheme] = useState<ThemeMode>(readTheme)

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle("light", theme === "light")
    root.classList.toggle("dark", theme === "dark")
    window.localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  const toggleTheme = useCallback(() => {
    setTheme((current) => (current === "dark" ? "light" : "dark"))
  }, [])

  return { theme, toggleTheme }
}
