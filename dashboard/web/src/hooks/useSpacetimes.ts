import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { createSpacetime, deleteSpacetime, getSpacetimes, getWorldDayBlocks } from "@/api/client"
import type { SpacetimeCreate } from "@/api/types"
import { worldKeys } from "@/hooks/useWorldBuild"

export const spacetimeKeys = {
  list: (world: string) => ["spacetimes", world] as const,
  dayBlocks: (world: string, run: string, date: string, policy: string) =>
    ["worlds", world, "runs", run, "days", date, "blocks", policy] as const,
}

export function useSpacetimes(world: string) {
  return useQuery({
    queryKey: spacetimeKeys.list(world),
    queryFn: () => getSpacetimes(world),
    enabled: world.length > 0,
    staleTime: 15_000,
  })
}

export function useCreateSpacetime(world: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: SpacetimeCreate) => createSpacetime(world, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: spacetimeKeys.list(world) })
      void queryClient.invalidateQueries({ queryKey: worldKeys.list })
    },
  })
}

export function useDeleteSpacetime(world: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (name: string) => deleteSpacetime(name),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: spacetimeKeys.list(world) })
      void queryClient.invalidateQueries({ queryKey: worldKeys.list })
    },
  })
}

export function useWorldDayBlocks(
  world: string,
  run: string,
  date: string,
  policy: string,
  enabled: boolean,
) {
  return useQuery({
    queryKey: spacetimeKeys.dayBlocks(world, run, date, policy),
    queryFn: () => getWorldDayBlocks(world, run, date, policy),
    enabled: enabled && world.length > 0 && run.length > 0 && date.length > 0,
    staleTime: 60_000,
  })
}
