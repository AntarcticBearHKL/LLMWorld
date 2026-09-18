import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react"

export type ScreenChrome = {
  title?: ReactNode
  actions?: ReactNode
}

type ScreenChromeValue = {
  chrome: ScreenChrome
  setChrome: (chrome: ScreenChrome) => () => void
}

const EMPTY: ScreenChrome = {}

const ScreenChromeContext = createContext<ScreenChromeValue | null>(null)

export function ScreenChromeProvider({ children }: { children: ReactNode }) {
  const [chrome, setChromeState] = useState<ScreenChrome>(EMPTY)

  const setChrome = useCallback((next: ScreenChrome) => {
    setChromeState(next)
    return () => {
      setChromeState((current) => (current === next ? EMPTY : current))
    }
  }, [])

  const value = useMemo(() => ({ chrome, setChrome }), [chrome, setChrome])

  return <ScreenChromeContext value={value}>{children}</ScreenChromeContext>
}

function useScreenChromeContext(): ScreenChromeValue {
  const value = useContext(ScreenChromeContext)
  if (value === null) {
    throw new Error("useScreenChrome must be used within a ScreenChromeProvider")
  }
  return value
}

export function useScreenChrome(): (chrome: ScreenChrome) => () => void {
  return useScreenChromeContext().setChrome
}

export function useScreenChromeValue(): ScreenChrome {
  return useScreenChromeContext().chrome
}
