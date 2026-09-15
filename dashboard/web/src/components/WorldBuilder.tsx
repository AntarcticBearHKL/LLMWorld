import { useEffect, useRef, useState } from "react"

import { useQueryClient } from "@tanstack/react-query"
import { Hammer, Loader2, Plus, RefreshCw, Trash2 } from "lucide-react"

import { ApiError } from "@/api/client"
import { BuildStepCard } from "@/components/BuildStepCard"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useJobs } from "@/hooks/useJobs"
import {
  BUILD_STEP_ORDER,
  findStepStatus,
  isActiveJob,
  isBuildStep,
  latestJobFor,
  useBuildState,
  useCreateWorld,
  useDeleteWorld,
  useWorlds,
  worldKeys,
} from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { cn } from "@/lib/utils"
import { useTimeStore } from "@/store/time"

const FIELD_CLASS =
  "h-8 rounded-md border-border-strong bg-surface-2 px-2.5 text-[12px] text-fg focus-visible:border-brand"

const randomWorldId = (): string => {
  const bytes = crypto.getRandomValues(new Uint8Array(3))
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("")
  return `world_${hex}`
}

function WorldList({ selected, onSelect }: { selected: string; onSelect: (world: string) => void }) {
  const worldsQuery = useWorlds()
  const create = useCreateWorld()
  const remove = useDeleteWorld()
  const [draft, setDraft] = useState("")
  const [pendingDelete, setPendingDelete] = useState<string | null>(null)

  const worlds = worldsQuery.data ?? []

  const onCreate = () => {
    const worldId = draft.trim().length > 0 ? draft.trim() : randomWorldId()
    create.mutate(
      { world_id: worldId },
      {
        onSuccess: (result) => {
          setDraft("")
          onSelect(result.world_id)
        },
      },
    )
  }

  const onDelete = (world: string) => {
    remove.mutate(world, {
      onSuccess: () => {
        setPendingDelete(null)
        if (world === selected) onSelect("")
      },
    })
  }

  return (
    <>
      <header className="flex shrink-0 items-center justify-between gap-2 border-b border-border px-4 py-2.5">
        <span className="text-[13px] font-semibold text-fg">
          世界列表 <span className="num text-[11px] text-fg-subtle">{worlds.length}</span>
        </span>
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label="刷新世界列表"
          onClick={() => void worldsQuery.refetch()}
        >
          <RefreshCw />
        </Button>
      </header>

      <div className="flex shrink-0 items-end gap-2 border-b border-border px-3 py-2.5">
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <Label htmlFor="build-world-id" className="label-micro">
            世界 ID（留空自动生成）
          </Label>
          <Input
            id="build-world-id"
            value={draft}
            placeholder="world_9f3a1c"
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !create.isPending) onCreate()
            }}
            className={cn(FIELD_CLASS, "num")}
          />
        </div>
        <Button size="sm" onClick={onCreate} disabled={create.isPending}>
          {create.isPending ? <Loader2 className="animate-spin" /> : <Plus />}
          新建空世界
        </Button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {worldsQuery.isPending ? (
          <p className="px-4 py-6 text-[11px] text-fg-subtle">载入中…</p>
        ) : worldsQuery.isError ? (
          <div className="flex flex-col items-start gap-2 px-4 py-6">
            <p className="text-[11px] text-danger">
              世界列表读取失败：{errorMessage(worldsQuery.error)}
            </p>
            <Button variant="outline" size="xs" onClick={() => void worldsQuery.refetch()}>
              重试
            </Button>
          </div>
        ) : worlds.length === 0 ? (
          <p className="px-4 py-6 text-[11px] text-fg-subtle">
            还没有世界。填写或留空世界 ID，点「新建空世界」创建一个空壳（不调用 LLM）。
          </p>
        ) : (
          <ul className="flex flex-col">
            {worlds.map((world) => {
              const active = world.world_id === selected
              return (
                <li key={world.world_id} className="flex items-center gap-1 border-b border-border pr-1">
                  <button
                    type="button"
                    onClick={() => onSelect(world.world_id)}
                    aria-current={active ? "true" : undefined}
                    className={cn(
                      "flex min-w-0 flex-1 flex-col gap-0.5 rounded-sm px-3 py-2 text-left transition-colors",
                      active ? "bg-brand-soft" : "hover:bg-surface-2",
                    )}
                  >
                    <span className={cn("num truncate text-[12px]", active ? "text-brand" : "text-fg")}>
                      {world.world_id}
                    </span>
                    <span className="label-micro">
                      {world.houses.length} 户
                      {world.postcode !== null ? ` · ${world.postcode}` : ""}
                      {world.has_events ? " · 有事件" : ""}
                    </span>
                  </button>

                  {pendingDelete === world.world_id ? (
                    <span className="flex shrink-0 items-center gap-1">
                      <button
                        type="button"
                        onClick={() => onDelete(world.world_id)}
                        disabled={remove.isPending}
                        title="移到 output/_trash/（可恢复）"
                        className="label-micro rounded-sm border border-danger/50 px-1.5 py-0.5 text-danger disabled:opacity-50"
                      >
                        确认删除
                      </button>
                      <button
                        type="button"
                        onClick={() => setPendingDelete(null)}
                        className="label-micro rounded-sm border border-border-strong px-1.5 py-0.5 text-fg-muted"
                      >
                        取消
                      </button>
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setPendingDelete(world.world_id)}
                      title="移到 output/_trash/（可恢复）"
                      className="label-micro mx-1 inline-flex shrink-0 items-center gap-1 rounded-sm border border-border-strong px-1.5 py-0.5 transition-colors hover:border-danger/60 hover:text-danger"
                    >
                      <Trash2 className="size-2.5" aria-hidden />
                      删除
                    </button>
                  )}
                </li>
              )
            })}
          </ul>
        )}
      </div>

      {create.isError || remove.isError || pendingDelete !== null ? (
        <div className="flex shrink-0 flex-col gap-1 border-t border-border px-4 py-2">
          {pendingDelete !== null ? (
            <p className="text-[10px] text-energy">
              删除会把 <span className="num">{pendingDelete}</span> 移到 output/_trash/（可恢复）。
            </p>
          ) : null}
          {create.isError ? (
            <p className="text-[10px] text-danger">创建失败：{errorMessage(create.error)}</p>
          ) : null}
          {remove.isError ? (
            <p className="text-[10px] text-danger">删除失败：{errorMessage(remove.error)}</p>
          ) : null}
        </div>
      ) : null}
    </>
  )
}

export function WorldBuilder() {
  const world = useTimeStore((state) => state.world)
  const step = useTimeStore((state) => state.step)
  const house = useTimeStore((state) => state.house)
  const setWorld = useTimeStore((state) => state.setWorld)
  const setStep = useTimeStore((state) => state.setStep)
  const setHouse = useTimeStore((state) => state.setHouse)
  const queryClient = useQueryClient()

  const worldsQuery = useWorlds()
  const jobsQuery = useJobs()
  const jobs = jobsQuery.data ?? []

  const worldJobs = jobs.filter((job) => job.kind === "build" && job.world === world)
  const activeJob = worldJobs.some(isActiveJob)
  const buildQuery = useBuildState(world, activeJob)
  const buildState = buildQuery.data

  const jobSignature = worldJobs.map((job) => `${job.id}:${job.status}`).join("|")
  const previousSignature = useRef(jobSignature)
  useEffect(() => {
    if (previousSignature.current === jobSignature) return
    previousSignature.current = jobSignature
    void queryClient.invalidateQueries({ queryKey: worldKeys.build(world) })
  }, [jobSignature, world, queryClient])

  useEffect(() => {
    if (world.length > 0) return
    const first = worldsQuery.data?.[0]
    if (first === undefined) return
    setWorld(first.world_id)
  }, [world, worldsQuery.data, setWorld])

  useEffect(() => {
    if (isBuildStep(step)) return
    if (buildState === undefined) return
    const pending = BUILD_STEP_ORDER.find(
      (item) => findStepStatus(buildState.steps, item)?.done === false,
    )
    setStep(pending ?? "assemble")
  }, [step, buildState, setStep])

  useEffect(() => {
    if (buildState === undefined) return
    if (buildState.houses.includes(house)) return
    const first = buildState.houses[0]
    if (first === undefined) return
    setHouse(first)
  }, [buildState, house, setHouse])

  return (
    <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 p-3 lg:grid-cols-[minmax(0,340px)_minmax(0,1fr)]">
      <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface">
        <WorldList selected={world} onSelect={setWorld} />
      </section>

      <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface">
        <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-4 py-2.5">
          <Hammer className="size-4 shrink-0 text-brand" aria-hidden />
          <span className="text-[13px] font-semibold text-fg">构建</span>
          {world.length > 0 ? <span className="num text-[11px] text-fg-muted">{world}</span> : null}
          {buildState !== undefined ? (
            <span className="label-micro">
              {buildState.houses.length} 户 ·{" "}
              {buildState.exists ? "world 目录已就绪" : "world 目录缺失"}
            </span>
          ) : null}
          <Button
            variant="ghost"
            size="icon-sm"
            className="ml-auto"
            aria-label="刷新构建状态"
            disabled={world.length === 0}
            onClick={() => void buildQuery.refetch()}
          >
            <RefreshCw />
          </Button>
        </header>

        {world.length === 0 ? (
          <p className="px-4 py-6 text-[11px] text-fg-subtle">
            先在左侧选择一个世界，或新建一个空世界。
          </p>
        ) : buildQuery.isPending ? (
          <p className="px-4 py-6 text-[11px] text-fg-subtle">构建状态载入中…</p>
        ) : buildQuery.isError ? (
          <div className="flex flex-col items-start gap-2 px-4 py-6">
            <p className="text-[11px] text-danger">
              {buildQuery.error instanceof ApiError && buildQuery.error.status === 404
                ? "世界不存在或已被删除："
                : "构建状态读取失败："}
              {errorMessage(buildQuery.error)}
            </p>
            <Button variant="outline" size="xs" onClick={() => void buildQuery.refetch()}>
              重试
            </Button>
          </div>
        ) : buildState === undefined ? (
          <p className="px-4 py-6 text-[11px] text-fg-subtle">构建状态载入中…</p>
        ) : (
          <div className="min-h-0 flex-1 overflow-y-auto">
            <div className="flex flex-col gap-3 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="label-micro">目标住户</span>
                {buildState.houses.length === 0 ? (
                  <span className="text-[11px] text-fg-subtle">暂无住户：先运行「类型」。</span>
                ) : (
                  buildState.houses.map((item) => (
                    <button
                      key={item}
                      type="button"
                      aria-pressed={house === item}
                      onClick={() => setHouse(item)}
                      className={cn(
                        "num rounded-sm border px-2 py-0.5 text-[10px] transition-colors",
                        house === item
                          ? "border-brand/50 bg-brand-soft text-brand"
                          : "border-border-strong text-fg-muted hover:text-fg",
                      )}
                    >
                      {item}
                    </button>
                  ))
                )}
                {house.length > 0 && !buildState.houses.includes(house) ? (
                  <span className="num text-[10px] text-energy">{house} 不在该世界</span>
                ) : null}
              </div>

              {BUILD_STEP_ORDER.map((item, index) => (
                <BuildStepCard
                  key={item}
                  world={world}
                  house={house}
                  step={item}
                  index={index}
                  status={findStepStatus(buildState.steps, item)}
                  job={latestJobFor(jobs, world, item, house)}
                  focused={step === item}
                  onFocus={() => setStep(item)}
                />
              ))}

              {jobsQuery.isError ? (
                <p className="text-[10px] text-danger">
                  作业列表读取失败，最近运行状态可能不完整：{errorMessage(jobsQuery.error)}
                </p>
              ) : null}

              <p className="text-[10px] text-fg-subtle">
                类型为世界级（1 次 LLM 调用）；人格 / 家庭按住户调用 LLM；装配只合并已有产物（0 次调用）。
                构建作业真实消耗 API 额度。
              </p>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
