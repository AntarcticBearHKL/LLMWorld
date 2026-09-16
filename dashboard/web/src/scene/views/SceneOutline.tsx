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
    <ul className="flex flex-col" aria-label="Rooms and appliances outline">
      {state.rooms.map((room) => {
        const appliances = state.appliances.filter((pose) => pose.room === room.room)
        return (
          <li key={room.room} className="border-b border-border last:border-b-0">
            <div className="flex items-baseline gap-2 px-3 py-1.5">
              <span className="min-w-0 flex-1 truncate text-[13px] font-medium text-fg">
                {room.room}
              </span>
              <span className="label-latin shrink-0">
                {room.occupants.length > 0 ? room.occupants.join(" · ") : ""}
              </span>
              <span className="num shrink-0 text-[12px] text-energy">
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
                          "flex w-full items-baseline gap-2 px-5 py-1 text-left transition-colors",
                          selected ? "bg-item-selected" : "hover:bg-item-hover",
                        )}
                      >
                        <span
                          className={cn(
                            "min-w-0 flex-1 truncate text-[12px]",
                            live ? "text-fg" : "text-fg-subtle",
                          )}
                        >
                          {pose.label}
                        </span>
                        <span className="num shrink-0 text-[12px] text-fg-subtle">
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
