import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { getSettings, updateSettings } from "@/api/client"
import type { SettingsUpdate } from "@/api/types"

export const settingsKeys = {
  current: ["settings"] as const,
}

export function useSettings() {
  return useQuery({ queryKey: settingsKeys.current, queryFn: getSettings, staleTime: 300_000 })
}

export function useUpdateSettings() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (patch: SettingsUpdate) => updateSettings(patch),
    onSuccess: (updated) => {
      queryClient.setQueryData(settingsKeys.current, updated)
      void queryClient.invalidateQueries({ queryKey: settingsKeys.current })
    },
  })
}
