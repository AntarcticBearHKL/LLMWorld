import type { ReactNode } from "react"

import type { BuildPreview } from "@/api/types"
import { cn } from "@/lib/utils"

interface BuildPreviewListProps {
  preview: BuildPreview | undefined
  isPending: boolean
  error: string | null
  needsHouse: boolean
  house: string
}

function PathRow({ path, exists }: { path: string; exists: boolean }) {
  return (
    <li className="flex min-w-0 items-center gap-2">
      <span
        className={cn("size-1.5 shrink-0 rounded-full", exists ? "bg-success" : "bg-border-strong")}
        aria-hidden
      />
      <span className="num min-w-0 flex-1 truncate text-[10px] text-fg-muted" title={path}>
        {path}
      </span>
      <span className={cn("label-latin shrink-0", exists ? "text-success" : "text-fg-subtle")}>
        {exists ? "exists" : "missing"}
      </span>
    </li>
  )
}

function Group({
  title,
  hint,
  tone,
  children,
}: {
  title: string
  hint?: string
  tone?: "energy"
  children: ReactNode
}) {
  return (
    <div className="flex flex-col gap-1">
      <span className={cn("label-latin", tone === "energy" ? "text-energy" : undefined)}>
        {title}
        {hint !== undefined ? ` · ${hint}` : ""}
      </span>
      {children}
    </div>
  )
}

export function BuildPreviewList({ preview, isPending, error, needsHouse, house }: BuildPreviewListProps) {
  if (needsHouse && house.length === 0) {
    return <p className="text-[10px] text-fg-subtle">先选择目标住户以查看读写路径。</p>
  }

  if (isPending) {
    return <p className="text-[10px] text-fg-subtle">读写预览载入中…</p>
  }

  if (error !== null) {
    return <p className="text-[10px] text-danger">读写预览读取失败：{error}</p>
  }

  if (preview === undefined) {
    return <p className="text-[10px] text-fg-subtle">暂无预览。</p>
  }

  const empty =
    preview.reads.length === 0 && preview.writes.length === 0 && preview.overwrites.length === 0

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-baseline gap-2">
        <span className="label-micro">读写预览</span>
        <span className="num text-[10px] text-fg-subtle">
          读 <span className="text-fg-muted">{preview.reads.length}</span> · 写{" "}
          <span className="text-fg-muted">{preview.writes.length}</span> · 覆盖{" "}
          <span className="text-energy">{preview.overwrites.length}</span>
        </span>
        {preview.house !== null ? (
          <span className="num ml-auto text-[10px] text-fg-subtle" title="后端解析出的目标住户">
            {preview.house}
          </span>
        ) : null}
      </div>

      {empty ? (
        <p className="text-[10px] text-fg-subtle">（后端未返回读写路径）</p>
      ) : (
        <>
          {preview.reads.length > 0 ? (
            <Group title="read">
              <ul className="flex flex-col gap-1">
                {preview.reads.map((item) => (
                  <PathRow key={item.path} path={item.path} exists={item.exists} />
                ))}
              </ul>
            </Group>
          ) : null}

          {preview.writes.length > 0 ? (
            <Group title="write">
              <ul className="flex flex-col gap-1">
                {preview.writes.map((item) => (
                  <PathRow key={item.path} path={item.path} exists={item.exists} />
                ))}
              </ul>
            </Group>
          ) : null}

          {preview.overwrites.length > 0 ? (
            <Group title="overwrite" hint="先备份" tone="energy">
              <ul className="flex flex-col gap-1">
                {preview.overwrites.map((path) => (
                  <li key={path} className="num min-w-0 truncate text-[10px] text-energy" title={path}>
                    {path}
                  </li>
                ))}
              </ul>
            </Group>
          ) : null}
        </>
      )}
    </div>
  )
}
