import { useEffect, useRef, useState } from "react"

import { Building2, House, LayoutGrid, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useDayReplay } from "@/hooks/useDayData"
import { memberInitial } from "@/lib/members"
import { useTimeStore } from "@/store/time"
import { AgentHud } from "./AgentHud"
import { ApplianceLayer } from "../layers/ApplianceLayer"
import { CharacterLayer } from "../layers/CharacterLayer"
import { EFFECTS_DEFAULT_ENABLED } from "../core/effects"
import { EffectLayer } from "../layers/EffectLayer"
import { PerfHud } from "./PerfHud"
import { SceneOutline } from "./SceneOutline"
import { SceneStage } from "./SceneStage"
import { Town } from "./Town"
import { useSceneState } from "../core/useSceneState"

interface SceneViewProps {
  onOpenPipeline?: (memberId: string) => void
  onEnterHouse?: (house: string) => void
}

type SceneMode = "town" | "interior"

export function SceneView({ onOpenPipeline, onEnterHouse }: SceneViewProps) {
  const wrapRef = useRef<HTMLDivElement>(null)
  const [size, setSize] = useState({ width: 0, height: 0 })
  const [mode, setMode] = useState<SceneMode>("town")
  const [effectsEnabled, setEffectsEnabled] = useState(EFFECTS_DEFAULT_ENABLED)
  const [trailEnabled, setTrailEnabled] = useState(false)
  const [outlineOpen, setOutlineOpen] = useState(false)
  const [diagnosticsOpen, setDiagnosticsOpen] = useState(false)
  const [highlighted, setHighlighted] = useState<string | null>(null)
  const [degraded, setDegraded] = useState(false)
  const replayQuery = useDayReplay()
  const replay = replayQuery.data
  const house = useTimeStore((store) => store.house)
  const setHouse = useTimeStore((store) => store.setHouse)
  const selectedMember = useTimeStore((store) => store.selectedMember)
  const setSelectedMember = useTimeStore((store) => store.setSelectedMember)
  const state = useSceneState(replay, size)
  const mapOnly = onEnterHouse !== undefined

  useEffect(() => {
    const wrap = wrapRef.current
    if (wrap === null) return
    const measure = () => setSize({ width: wrap.clientWidth, height: wrap.clientHeight })
    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(wrap)
    return () => observer.disconnect()
  }, [])

  const effectsOn = effectsEnabled && !degraded

  const enter = (next: string) => {
    if (onEnterHouse !== undefined) {
      onEnterHouse(next)
      return
    }
    setHouse(next)
    setMode("interior")
  }

  return (
    <div className="card flex h-full min-h-0 flex-col overflow-hidden">
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-3.5 py-2.5">
        <span className="t-micro flex items-center gap-1.5">
          {mapOnly || mode === "town" ? (
            <LayoutGrid className="size-3" />
          ) : (
            <Building2 className="size-3" />
          )}
          {mapOnly ? "Town map" : mode === "town" ? "Town" : `Indoor · ${house}`}
        </span>

        {mapOnly ? null : (
          <>
            <div className="ml-2 flex items-center gap-0.5 rounded-full border border-border bg-surface-2 p-0.5">
              <Button
                variant={mode === "town" ? "default" : "ghost"}
                size="sm"
                className="h-6 rounded-full px-2.5 t-caption"
                onClick={() => setMode("town")}
              >
                Town
              </Button>
              <Button
                variant={mode === "interior" ? "default" : "ghost"}
                size="sm"
                className="h-6 rounded-full px-2.5 t-caption"
                onClick={() => setMode("interior")}
                disabled={state === null}
              >
                <House className="mr-1 size-3" />
                Indoor
              </Button>
            </div>

            {replay !== undefined && mode === "interior" ? (
              <nav className="ml-2 flex flex-wrap items-center gap-1" aria-label="Select member">
                {replay.members.map((member) => {
                  const active = member.id === selectedMember
                  return (
                    <Button
                      key={member.id}
                      variant={active ? "default" : "outline"}
                      size="sm"
                      className="h-6 rounded-full px-2.5 t-caption"
                      aria-pressed={active}
                      onClick={() => setSelectedMember(active ? null : member.id)}
                    >
                      <span className="num">{memberInitial(member.id)}</span>
                      <span className="ml-1 hidden sm:inline">{member.id}</span>
                    </Button>
                  )
                })}
              </nav>
            ) : null}

            <div className="ml-auto flex flex-wrap items-center gap-1.5">
              <Button
                variant={diagnosticsOpen ? "default" : "outline"}
                size="sm"
                className="h-6 rounded-full px-2.5 t-caption"
                onClick={() => setDiagnosticsOpen((value) => !value)}
                disabled={mode !== "interior" || state === null}
                title="Frame rate and memory diagnostics (keep the page in the foreground)"
              >
                Diagnostics
              </Button>
              <Button
                variant={outlineOpen ? "default" : "outline"}
                size="sm"
                className="h-6 rounded-full px-2.5 t-caption"
                onClick={() => setOutlineOpen((value) => !value)}
                disabled={mode !== "interior" || state === null}
              >
                Outline
              </Button>
              <Button
                variant={effectsOn ? "default" : "outline"}
                size="sm"
                className="h-6 rounded-full px-2.5 t-caption"
                onClick={() => {
                  if (degraded) {
                    setDegraded(false)
                    setEffectsEnabled(true)
                    return
                  }
                  setEffectsEnabled((value) => !value)
                }}
                title={
                  degraded
                    ? "Performance is below the threshold, so effects were disabled; click to force them on and lift the degradation"
                    : undefined
                }
              >
                Effects {effectsOn ? "on" : "off"}
                {degraded ? " (degraded)" : ""}
              </Button>
              <Button
                variant={trailEnabled ? "default" : "outline"}
                size="sm"
                className="h-6 rounded-full px-2.5 t-caption"
                onClick={() => setTrailEnabled((value) => !value)}
              >
                Trails {trailEnabled ? "on" : "off"}
              </Button>
            </div>
          </>
        )}
      </header>

      <div ref={wrapRef} className="relative min-h-0 flex-1">
        {mode === "town" ? <Town onEnter={enter} /> : null}

        {mode === "interior" && state !== null ? (
          <SceneStage state={state}>
            <ApplianceLayer state={state} highlighted={highlighted} />
            <CharacterLayer state={state} showTrail={trailEnabled} />
            <EffectLayer state={state} enabled={effectsOn} />
          </SceneStage>
        ) : null}

        {mode === "interior" && state === null ? (
          <div className="flex h-full items-center justify-center p-6 text-center">
            <p className="t-caption text-fg-muted">
              {replayQuery.isPending ? "Loading…" : "No replay data for this household and date."}
            </p>
          </div>
        ) : null}

        <AgentHud replay={replay} onOpenPipeline={onOpenPipeline} />

        {mode === "interior" && state !== null && diagnosticsOpen ? (
          <div className="flex shrink-0 justify-end border-b border-border px-3 py-1.5">
            <PerfHud onDegradeChange={setDegraded} />
          </div>
        ) : null}

        {mode === "interior" && state !== null && outlineOpen ? (
          <aside className="chrome-lg absolute right-3 top-3 z-20 flex max-h-[min(560px,calc(100%-24px))] w-[250px] flex-col overflow-hidden shadow-3">
            <header className="flex shrink-0 items-center justify-between gap-2 border-b border-border px-3 py-1.5">
              <span className="t-micro">Rooms and appliances</span>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label="Close outline"
                onClick={() => setOutlineOpen(false)}
              >
                <X />
              </Button>
            </header>
            <div className="min-h-0 flex-1 overflow-y-auto">
              <SceneOutline state={state} highlighted={highlighted} onHighlight={setHighlighted} />
            </div>
          </aside>
        ) : null}

        <p className="sr-only" aria-live="polite">
          {mode === "town"
            ? "Town view: every square is one household; select a house to enter it."
            : state === null
              ? "No indoor scene data to replay at this moment."
              : `Indoor scene: ${state.rooms.length} rooms, ${state.appliances.length} appliances, ${
                  state.appliances.filter(
                    (pose) => pose.state === "active" || pose.state === "baseload",
                  ).length
                } drawing power, ${state.outMembers.length} members away, ${Math.round(state.totalWatts)} W total.`}
        </p>
      </div>
    </div>
  )
}
