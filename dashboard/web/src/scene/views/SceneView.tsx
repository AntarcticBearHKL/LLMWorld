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
}

type SceneMode = "town" | "interior"

export function SceneView({ onOpenPipeline }: SceneViewProps) {
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
    setHouse(next)
    setMode("interior")
  }

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface">
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-3 py-2">
        <span className="label-micro flex items-center gap-1.5">
          {mode === "town" ? <LayoutGrid className="size-3" /> : <Building2 className="size-3" />}
          {mode === "town" ? "住户小镇" : `室内 · ${house}`}
        </span>

        <div className="ml-2 flex items-center gap-0.5 rounded-md border border-border bg-surface-2 p-0.5">
          <Button
            variant={mode === "town" ? "secondary" : "ghost"}
            size="sm"
            className="h-6 px-2 text-[11px]"
            onClick={() => setMode("town")}
          >
            小镇
          </Button>
          <Button
            variant={mode === "interior" ? "secondary" : "ghost"}
            size="sm"
            className="h-6 px-2 text-[11px]"
            onClick={() => setMode("interior")}
            disabled={state === null}
          >
            <House className="mr-1 size-3" />
            室内
          </Button>
        </div>

        {replay !== undefined && mode === "interior" ? (
          <nav className="ml-2 flex flex-wrap items-center gap-1" aria-label="选择成员">
            {replay.members.map((member) => {
              const active = member.id === selectedMember
              return (
                <Button
                  key={member.id}
                  variant={active ? "secondary" : "outline"}
                  size="sm"
                  className="h-6 px-2 text-[11px]"
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
            variant={diagnosticsOpen ? "secondary" : "outline"}
            size="sm"
            className="h-6 px-2 text-[11px]"
            onClick={() => setDiagnosticsOpen((value) => !value)}
            disabled={mode !== "interior" || state === null}
            title="帧率与内存诊断（需保持页面在前台才有效）"
          >
            诊断
          </Button>
          <Button
            variant={outlineOpen ? "secondary" : "outline"}
            size="sm"
            className="h-6 px-2 text-[11px]"
            onClick={() => setOutlineOpen((value) => !value)}
            disabled={mode !== "interior" || state === null}
          >
            清单
          </Button>
          <Button
            variant={effectsOn ? "secondary" : "outline"}
            size="sm"
            className="h-6 px-2 text-[11px]"
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
                ? "性能低于阈值，特效已被自动关闭；点击可强制开启并解除降级"
                : undefined
            }
          >
            特效{effectsOn ? "开" : "关"}
            {degraded ? "（已降级）" : ""}
          </Button>
          <Button
            variant={trailEnabled ? "secondary" : "outline"}
            size="sm"
            className="h-6 px-2 text-[11px]"
            onClick={() => setTrailEnabled((value) => !value)}
          >
            轨迹{trailEnabled ? "开" : "关"}
          </Button>
        </div>
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
            <p className="text-[12px] text-fg-muted">
              {replayQuery.isPending ? "载入中…" : "该住户/日期没有可回放的数据。"}
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
          <aside className="absolute right-3 top-3 z-20 flex max-h-[min(560px,calc(100%-24px))] w-[250px] flex-col overflow-hidden rounded-lg border border-border bg-surface/95 shadow-[var(--shadow-2)] backdrop-blur">
            <header className="flex shrink-0 items-center justify-between gap-2 border-b border-border px-3 py-1.5">
              <span className="label-micro">房间与电器清单</span>
              <Button variant="ghost" size="icon-sm" aria-label="关闭清单" onClick={() => setOutlineOpen(false)}>
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
            ? "住户小镇视图：每个方块是一户，点击进入室内。"
            : state === null
              ? "当前没有可回放的室内场景数据。"
              : `室内场景：${state.rooms.length} 个房间，${state.appliances.length} 台电器，其中 ${
                  state.appliances.filter(
                    (pose) => pose.state === "active" || pose.state === "baseload",
                  ).length
                } 台在用电，${state.outMembers.length} 人外出，当前总功率 ${
                  state.totalWatts >= 1000
                    ? `${(state.totalWatts / 1000).toFixed(2)} 千瓦`
                    : `${Math.round(state.totalWatts)} 瓦`
                }。`}
        </p>
      </div>
    </div>
  )
}
