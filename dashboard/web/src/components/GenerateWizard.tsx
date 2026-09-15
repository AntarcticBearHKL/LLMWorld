import { useState } from "react"

import { Globe2 } from "lucide-react"

import type { JobRequest } from "@/api/types"
import { JobSubmitBar } from "@/components/JobSubmitBar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { USE_MOCK } from "@/api/client"

const FIELD_CLASS =
  "h-8 rounded-md border-border-strong bg-surface-2 px-2.5 text-[12px] text-fg focus-visible:border-brand"

export function GenerateWizard() {
  const [world, setWorld] = useState("")
  const [count, setCount] = useState(1)
  const [seed, setSeed] = useState(42)
  const [worldConfig, setWorldConfig] = useState("")
  const [workers, setWorkers] = useState(4)

  const payload: JobRequest = {
    kind: "world",
    world: world.trim().length > 0 ? world.trim() : null,
    count,
    seed,
    world_config: worldConfig.trim().length > 0 ? worldConfig.trim() : null,
    workers,
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <header className="flex items-start gap-2">
        <Globe2 className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden />
        <div className="flex flex-col gap-1">
          <h2 className="text-[13px] font-semibold text-fg">生成世界</h2>
          <p className="text-[11px] text-fg-muted">
            对应 <span className="num">run.py --mode world</span>：先产出住户类型，再逐个住户构建
            家庭结构与成员画像。研究规则限制世界最多 5 户。
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="world-id" className="label-micro">
            世界 ID（留空自动生成）
          </Label>
          <Input
            id="world-id"
            value={world}
            placeholder="world_838587"
            onChange={(event) => setWorld(event.target.value)}
            className={FIELD_CLASS}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="world-count" className="label-micro">
            住户类型数量（1–5）
          </Label>
          <Input
            id="world-count"
            type="number"
            min={1}
            max={5}
            value={count}
            onChange={(event) => {
              const next = Number(event.target.value)
              setCount(Number.isFinite(next) ? Math.min(5, Math.max(1, Math.trunc(next))) : 1)
            }}
            className={FIELD_CLASS}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="world-seed" className="label-micro">
            随机种子
          </Label>
          <Input
            id="world-seed"
            type="number"
            value={seed}
            onChange={(event) => {
              const next = Number(event.target.value)
              setSeed(Number.isFinite(next) ? Math.trunc(next) : 42)
            }}
            className={FIELD_CLASS}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="world-config" className="label-micro">
            世界配置（import/world/ 下的名称，留空用默认）
          </Label>
          <Input
            id="world-config"
            value={worldConfig}
            placeholder="Melbourne"
            onChange={(event) => setWorldConfig(event.target.value)}
            className={FIELD_CLASS}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="world-workers" className="label-micro">
            并发线程
          </Label>
          <Input
            id="world-workers"
            type="number"
            min={1}
            max={8}
            value={workers}
            onChange={(event) => {
              const next = Number(event.target.value)
              setWorkers(Number.isFinite(next) ? Math.min(8, Math.max(1, Math.trunc(next))) : 4)
            }}
            className={FIELD_CLASS}
          />
        </div>
      </div>

      <JobSubmitBar
        payload={payload}
        disabled={USE_MOCK}
        disabledReason="当前是 mock 模式（VITE_USE_MOCK=1），不会真正提交。请用 VITE_USE_MOCK=0 启动前端以连接后端。"
      />
    </div>
  )
}
