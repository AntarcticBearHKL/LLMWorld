import { useId, useState } from "react"
import { BookOpen } from "lucide-react"

import type { DistrictPreset } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

interface DistrictTemplate {
  id: string
  title: string
  description: string
  prompt: string
}

const DISTRICT_TEMPLATE_LIBRARY: DistrictTemplate[] = [
  {
    id: "clayton_3168",
    title: "Clayton 3168 (ABS census style)",
    description: "ABS-style district profile modelled on the Clayton 3168 census text.",
    prompt:
      "You are drafting a synthetic district profile for a residential energy-simulation world, written in the register of an Australian Bureau of Statistics (ABS) 2021 Census community report.\n\n## Reference profile (ABS-style census text)\n\nIn the southeastern part of the Melbourne metropolitan area, the Clayton 3168 postcode district presents a distinctive demographic profile. According to the 2021 census, the district has a usual resident population of 21,880 — 11,681 males and 10,201 females, a slight male skew. The most striking feature is its extremely young age structure: the district's median age is only 28, well below the Australian national average. The 20-24 age group alone has 4,638 residents and the 25-34 group 6,640 — together more than half of the total population — making this an area dominated by young students and early-career professionals. By contrast, there are only 1,934 children aged 0-14 and about 1,486 residents aged 65 and over, a classic \"large middle, small ends\" structure.\n\nThis age structure deeply shapes the local household landscape. The district has 4,009 households with an average size of 2.5 people. Couple-only households are the largest group at 1,768, alongside 1,891 couples with children and 434 single-parent families. Because the population is young and student-heavy, living alone or sharing is very common: 1,893 households are one-person non-family dwellings and another 3,263 are non-family households, meaning many people do not live in traditional family units. Marital status reflects this too: among 25-34 year-olds, 2,838 men have never married and 1,183 women are unmarried.\n\nEconomically, Clayton shows a typical \"student economy\". The median personal weekly income is AUD 606 — below the Greater Melbourne level — reflecting the large number of full-time students and part-time workers. The median household weekly income is AUD 1,778 and the median family weekly income AUD 1,508. The unemployment rate is 9.3% and the labour force participation rate 60.7% (63.5% for men, 57.4% for women). Among employed residents, 5,386 work full-time and 4,761 part-time — a notably high part-time share. Education is one of the largest employers, with 1,216 people working in education and training, followed by health care and social assistance, and professional, scientific and technical services.\n\nHousing in Clayton is diverse. Of the 8,606 private dwellings, 2,640 are separate houses, 2,703 are semi-detached, row or terrace houses, and 1,794 are flats or units. Home ownership rates are relatively low: only 1,358 households fully own their home, while 3,305 rent through a real estate agent and 618 rent from a private landlord. The median weekly rent is AUD 396 and the median monthly mortgage repayment AUD 2,000. On average 0.9 people live per bedroom — not especially crowded. Notably, 1,452 dwellings are unoccupied, likely including investor properties and short-term student rentals.\n\nEducation is the district's most defining feature. 4,797 residents hold a bachelor's degree, 3,485 a postgraduate qualification, and 1,577 an advanced diploma or diploma — an exceptionally dense concentration of highly educated people. Student numbers are striking: 3,337 residents aged 15-24 are enrolled in education and 2,517 aged 25 and over are still studying, confirming Clayton's identity as a university town adjacent to Monash University. The cultural diversity is equally marked: only 6,488 residents speak only English at home, while 13,724 speak a language other than English — including 5,406 of Chinese ancestry and about 2,800 of Indian ancestry, plus large numbers of migrants from Sri Lanka, Malaysia, Vietnam and elsewhere. 7,541 residents have no religious affiliation, 1,617 are Buddhists, 1,145 Orthodox Christians, and there is a substantial Hindu community. For commuting, driving dominates: 4,631 people drive to work alone, while close to 670 rely on trains and buses, with a notable number walking or cycling.\n\nIn summary, Clayton 3168 is a dynamic, multicultural community formed by international students, young professionals and newly arrived migrant families. It lacks the quiet ageing typical of traditional Australian suburbs; instead it is full of the bustle of study, work and mobility. High education levels, multilingualism, a high rental share and young residents clustering together are its defining traits — and its vitality. As a residential area it functions more like a \"talent incubator\" for the future: large numbers of young people receive higher education and start their careers here, continuously supplying fresh energy to Melbourne.\n\n## Task\n\nWrite a NEW district description in the same register, structure and level of detail as the reference above, but for a DIFFERENT district with a DIFFERENT name. Keep the same thematic spine:\n\n- a young population dominated by university students and early-career professionals, with a middle-heavy age structure and a small share of children and older residents;\n- a high share of renters and of non-family / shared households;\n- strong cultural and linguistic diversity, with a large overseas-born and multilingual population.\n\nInvent plausible, internally consistent census-style figures and a specific district name. Do not reuse the reference's name and do not copy its numbers verbatim. Return only the description prose, following the house rules below.",
  },
  {
    id: "inner_city_highrise",
    title: "Inner-city high-rise",
    description:
      "Dense apartment district: high rental share, transient young professionals, night-time economy.",
    prompt:
      "Write a district description for a dense INNER-CITY HIGH-RISE district of an Australian capital city, and invent a plausible district name for it. The district is dominated by apartment towers, has an exceptionally high rental share, a young and highly transient professional population, a strong night-time economy, excellent public transport, and a cosmopolitan, multilingual resident mix. Cover population and age structure, household composition, income and employment, dwelling type and tenure, education, ancestry and language, and commuting, in a consistent census-report voice. Follow the house rules below and return only the description prose.",
  },
  {
    id: "outer_suburban_family",
    title: "Outer-suburban family",
    description:
      "Mortgage-belt district of detached family homes, two-car households and long commutes.",
    prompt:
      "Write a district description for an OUTER-SUBURBAN FAMILY district of an Australian capital city, and invent a plausible district name for it. The district is a mortgage belt of detached houses on generous blocks, with many families with children, two-car households, high car dependence and long commutes, a mix of owner-occupiers and younger families, some ageing-in-place older residents, and a comparatively settled but still multicultural population. Cover population and age structure, household composition, income and employment, dwelling type and tenure, education, ancestry and language, and commuting, in a consistent census-report voice. Follow the house rules below and return only the description prose.",
  },
]

interface DistrictPromptFieldsProps {
  prompt: string
  disabled: boolean
  onPromptChange: (prompt: string) => void
  presets?: DistrictPreset[]
  presetsPending?: boolean
  preset?: string
  onPresetChange?: (preset: string) => void
}

export function DistrictPromptFields({
  prompt,
  disabled,
  onPromptChange,
  presets,
  presetsPending = false,
  preset = "",
  onPresetChange,
}: DistrictPromptFieldsProps) {
  const promptId = useId()
  const [libraryOpen, setLibraryOpen] = useState(false)

  if (presets !== undefined) {
    const custom = prompt.trim().length > 0
    const selected = presets.find((item) => item.id === preset) ?? null

    return (
      <div className="flex flex-col gap-3">
        <div className="flex flex-col gap-1.5">
          <span className="label-micro">Preset</span>
          {presetsPending ? (
            <span className="t-caption text-fg-subtle">Loading presets…</span>
          ) : presets.length === 0 ? (
            <span className="t-caption text-fg-subtle">
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
                    onClick={() => onPresetChange?.(active ? "" : item.id)}
                    className={cn(
                      "t-body transition-colors disabled:opacity-50",
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
            <p className="t-caption text-fg-subtle">{selected.description}</p>
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
            className="min-h-24 t-body"
          />
          <span className="t-caption text-fg-subtle">
            {custom
              ? "Custom prompt takes precedence over the preset."
              : selected === null
                ? "Pick a preset or write a prompt: the district step refuses to run with neither."
                : "Clear the prompt to fall back to the selected preset."}
          </span>
        </div>
      </div>
    )
  }

  const applied = DISTRICT_TEMPLATE_LIBRARY.find((item) => item.prompt === prompt) ?? null

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between gap-2">
        <Label htmlFor={promptId} className="t-micro">
          Optimization prompt
        </Label>
        <Button
          variant="ghost"
          size="sm"
          type="button"
          disabled={disabled}
          onClick={() => setLibraryOpen(true)}
        >
          <BookOpen />
          Library
        </Button>
      </div>

      <Textarea
        id={promptId}
        value={prompt}
        disabled={disabled}
        placeholder="Write the district-description prompt, or load one from the library."
        onChange={(event) => onPromptChange(event.target.value)}
        className="min-h-32 t-body"
      />
      <span className="t-caption text-fg-subtle">
        {applied === null
          ? "The LLM rewrites this prompt into the district description and saves it — it does not invent the district from nothing."
          : `Library: ${applied.title}. Edit it freely — the field is what gets sent.`}
      </span>

      <Sheet open={libraryOpen} onOpenChange={setLibraryOpen}>
        <SheetContent side="center" className="flex flex-col gap-0 sm:max-w-lg">
          <SheetHeader className="border-b border-border">
            <SheetTitle>Prompt library</SheetTitle>
            <SheetDescription>
              Read-only templates for the optimization prompt. Applying one fills the field behind
              this dialog.
            </SheetDescription>
          </SheetHeader>

          <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-4">
            {DISTRICT_TEMPLATE_LIBRARY.map((item) => (
              <div
                key={item.id}
                className="flex flex-col gap-1.5 rounded-xl border border-border bg-surface-2 px-3 py-2.5"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="t-title">{item.title}</span>
                  <Button
                    variant="outline"
                    size="sm"
                    type="button"
                    disabled={disabled}
                    onClick={() => {
                      onPromptChange(item.prompt)
                      setLibraryOpen(false)
                    }}
                  >
                    {item.prompt === prompt ? "Applied" : "Apply"}
                  </Button>
                </div>
                <span className="t-caption text-fg-subtle">{item.description}</span>
                <span className="num t-caption text-fg-muted">
                  {item.prompt.slice(0, 160)}…
                </span>
              </div>
            ))}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  )
}
