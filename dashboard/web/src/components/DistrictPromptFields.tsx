import { useId } from "react"

import type { DistrictPreset } from "@/api/types"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

interface DistrictPromptFieldsProps {
  presets: DistrictPreset[]
  presetsPending: boolean
  preset: string
  prompt: string
  disabled: boolean
  onPresetChange: (preset: string) => void
  onPromptChange: (prompt: string) => void
}

export function DistrictPromptFields({
  presets,
  presetsPending,
  preset,
  prompt,
  disabled,
  onPresetChange,
  onPromptChange,
}: DistrictPromptFieldsProps) {
  const promptId = useId()
  const custom = prompt.trim().length > 0
  const selected = presets.find((item) => item.id === preset) ?? null

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-1.5">
        <span className="label-micro">Preset</span>
        {presetsPending ? (
          <span className="text-[12px] text-fg-subtle">Loading presets…</span>
        ) : presets.length === 0 ? (
          <span className="text-[12px] text-fg-subtle">
            No presets available — write a custom prompt instead.
          </span>
        ) : (
          <div className="flex flex-wrap gap-1.5">
            {presets.map((item) => {
              const active = item.id === preset && !custom
              return (
                <button
                  key={item.id}
                  type="button"
                  aria-pressed={active}
                  disabled={disabled}
                  title={item.description}
                  onClick={() => onPresetChange(active ? "" : item.id)}
                  className={cn(
                    "text-[12px] transition-colors disabled:opacity-50",
                    active
                      ? "chip chip-active"
                      : "chip hover:border-border-strong hover:bg-item-hover hover:text-fg",
                  )}
                >
                  {item.title.length > 0 ? item.title : item.id}
                </button>
              )
            })}
          </div>
        )}
        {selected !== null && !custom ? (
          <p className="text-[12px] text-fg-subtle">{selected.description}</p>
        ) : null}
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor={promptId} className="label-micro">
          Custom prompt
        </Label>
        <Textarea
          id={promptId}
          value={prompt}
          disabled={disabled}
          placeholder="Write the district-description prompt yourself — it overrides the preset."
          onChange={(event) => onPromptChange(event.target.value)}
          className="min-h-24 text-[13px]"
        />
        <span className="text-[12px] text-fg-subtle">
          {custom
            ? "Custom prompt takes precedence over the preset."
            : selected === null
              ? "Pick a preset, or write a prompt: with neither, the backend falls back to the first preset."
              : "Clear the prompt to fall back to the selected preset."}
        </span>
      </div>
    </div>
  )
}
