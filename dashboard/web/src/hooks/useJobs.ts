import { useEffect, useRef, useState } from "react"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { USE_MOCK, createJob, estimateJob, getJobLlmCall, jobStreamUrl, listJobLlmCalls, listJobs } from "@/api/client"
import type { JobInfo, JobRequest } from "@/api/types"

const MAX_LOG_LINES = 4000

export const jobKeys = {
  list: ["jobs"] as const,
  llmCalls: (jobId: string) => ["jobs", jobId, "llm-calls"] as const,
  llmCall: (jobId: string, callId: string) => ["jobs", jobId, "llm-calls", callId] as const,
}

const isActive = (job: JobInfo): boolean => job.status === "running" || job.status === "queued"

/** 有作业在跑就快轮询，否则慢轮询。 */
export function useJobs() {
  const [interval, setInterval] = useState(15000)
  const query = useQuery({
    queryKey: jobKeys.list,
    queryFn: listJobs,
    refetchInterval: interval,
    refetchIntervalInBackground: false,
  })
  useEffect(() => {
    const jobs = query.data ?? []
    setInterval(jobs.some(isActive) ? 2500 : 15000)
  }, [query.data])
  return query
}

export function useEstimateJob() {
  return useMutation({ mutationFn: (payload: JobRequest) => estimateJob(payload) })
}

export function useCreateJob() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: JobRequest) => createJob(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: jobKeys.list })
      void queryClient.invalidateQueries({ queryKey: ["worlds"] })
    },
  })
}

/** SSE 实时日志。mock 模式下不连接（后端不存在）。 */
export function useJobLog(jobId: string | null) {
  const [lines, setLines] = useState<string[]>([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    setLines([])
    setConnected(false)
    if (jobId === null || USE_MOCK) return

    const source = new EventSource(jobStreamUrl(jobId))
    const onOpen = () => setConnected(true)
    const onLog = (event: Event) => {
      const data = (event as MessageEvent<string>).data
      let text = data
      try {
        const parsed: unknown = JSON.parse(data)
        if (typeof parsed === "string") text = parsed
      } catch {
        // 后端也可能直接发纯文本行
      }
      setLines((previous) =>
        previous.length >= MAX_LOG_LINES ? [...previous.slice(-MAX_LOG_LINES + 1), text] : [...previous, text],
      )
    }
    const onDone = () => {
      setConnected(false)
      source.close()
    }

    source.addEventListener("open", onOpen)
    source.addEventListener("log", onLog)
    source.addEventListener("done", onDone)
    source.addEventListener("error", onDone)
    return () => {
      source.removeEventListener("open", onOpen)
      source.removeEventListener("log", onLog)
      source.removeEventListener("done", onDone)
      source.removeEventListener("error", onDone)
      source.close()
    }
  }, [jobId])

  return { lines, connected }
}

/** 一个作业的 LLM 调用清单；live=true 时快轮询（构建作业运行中，trace 持续增长）。 */
export function useJobLlmCalls(jobId: string | null, live = false) {
  const queryClient = useQueryClient()
  const wasLive = useRef(live)
  const query = useQuery({
    queryKey: jobKeys.llmCalls(jobId ?? ""),
    queryFn: () => listJobLlmCalls(jobId ?? ""),
    enabled: jobId !== null,
    refetchInterval: live ? 3000 : false,
  })
  useEffect(() => {
    // 作业刚结束：轮询已停，但 trace 通常在最后才落盘 —— 补拉一次，避免停在空结果。
    if (wasLive.current && !live && jobId !== null) {
      void queryClient.invalidateQueries({ queryKey: jobKeys.llmCalls(jobId) })
    }
    wasLive.current = live
  }, [live, jobId, queryClient])
  return query
}

export function useJobLlmCall(jobId: string | null, callId: string | null) {
  return useQuery({
    queryKey: jobKeys.llmCall(jobId ?? "", callId ?? ""),
    queryFn: () => getJobLlmCall(jobId ?? "", callId ?? ""),
    enabled: jobId !== null && callId !== null,
  })
}
