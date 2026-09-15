import { APPLIANCE_STATE_LABELS } from "@/lib/appliance"
import { formatWatts } from "@/lib/time"
import { cn } from "@/lib/utils"
import type { SceneState } from "../core/types"

interface SceneOutlineProps {
  state: SceneState
  highlighted: string | null
  onHighlight: (uniqueId: string | null) => void
}

export function SceneOutline({ state, highlighted, onHighlight }: SceneOutlineProps) {
  return (
    <ul className="flex flex-col" aria-label="房间与电器清单">
      {state.rooms.map((room) => {
        const appliances = state.appliances.filter((pose) => pose.room === room.room)
        return (
          <li key={room.room} className="border-b border-border last:border-b-0">
            <div className="flex items-baseline gap-2 px-3 py-1.5">
              <span className="min-w-0 flex-1 truncate text-[11px] font-medium text-fg">
                {room.room}
              </span>
              <span className="label-latin shrink-0">
                {room.occupants.length > 0 ? room.occupants.join(" · ") : ""}
              </span>
              <span className="num shrink-0 text-[10px] text-energy">
                {room.watts > 0 ? formatWatts(room.watts) : "—"}
              </span>
            </div>
            {appliances.length > 0 ? (
              <ul className="flex flex-col pb-1">
                {appliances.map((pose) => {
                  const live = pose.state === "active" || pose.state === "baseload"
                  const selected = highlighted === pose.uniqueId
                  return (
                    <li key={pose.uniqueId}>
                      <button
                        type="button"
                        aria-pressed={selected}
                        onClick={() => onHighlight(selected ? null : pose.uniqueId)}
                        className={cn(
                          "flex w-full items-baseline gap-2 px-5 py-0.5 text-left transition-colors",
                          selected ? "bg-brand-soft" : "hover:bg-surface-2",
                        )}
                      >
                        <span
                          className={cn(
                            "min-w-0 flex-1 truncate text-[10px]",
                            live ? "text-fg" : "text-fg-subtle",
                          )}
                        >
                          {pose.label}
                        </span>
                        <span className="num shrink-0 text-[9px] text-fg-subtle">
                          {pose.watts > 0 ? formatWatts(pose.watts) : APPLIANCE_STATE_LABELS[pose.state]}
                        </span>
                      </button>
                    </li>
                  )
                })}
              </ul>
            ) : null}
          </li>
        )
      })}
    </ul>
  )
}
