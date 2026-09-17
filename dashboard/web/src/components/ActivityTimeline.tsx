import { useEffect, useRef } from "react"
import { Maximize2, Minus, Plus } from "lucide-react"
import { DataSet } from "vis-data"
import { Timeline, type DataGroup, type DataItem, type IdType } from "vis-timeline/esnext"

import type { DayReplay } from "@/api/types"
import { CategoryLegend } from "@/components/primitives/CategoryLegend"
import { Panel } from "@/components/primitives/Panel"
import { Button } from "@/components/ui/button"
import { categorizeActivity, type ActivityCategory } from "@/lib/activity"
import { DAY_MINUTES, dateToMinute, formatHHMM, formatMinutesAsDuration, minuteToDate } from "@/lib/time"
import { useTimeStore } from "@/store/time"

interface TimelineActivityItem extends DataItem {
  id: string
  memberId: string
  lane: number
  category: ActivityCategory
}

const LANE_HEIGHT_PX = 54
const AXIS_HEIGHT_PX = 52

const escapeHtml = (value: string): string =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")

const buildTooltip = (
  start: number,
  end: number,
  activity: string,
  location: string,
  desc: string | null,
): string => {
  const parts = [
    `<span class="tip-time">${formatHHMM(start)}–${formatHHMM(end)}</span>`,
    `<b>${escapeHtml(activity)}</b>`,
    `<br><span class="tip-loc">${escapeHtml(location)} · ${formatMinutesAsDuration(end - start)}</span>`,
  ]
  if (desc !== null && desc.length > 0) {
    parts.push(`<span class="tip-desc">${escapeHtml(desc)}</span>`)
  }
  return parts.join(" ")
}

const buildGroupLabel = (member: string, bedroom: string | null, lane: number): HTMLElement => {
  const wrapper = document.createElement("div")
  wrapper.className = "lane-label"
  wrapper.style.setProperty("--lane", `var(--member-${lane})`)

  const bar = document.createElement("span")
  bar.className = "lane-label-bar"
  wrapper.appendChild(bar)

  const text = document.createElement("span")
  text.className = "lane-label-text"

  const name = document.createElement("span")
  name.className = "lane-label-name"
  name.textContent = member
  text.appendChild(name)

  if (bedroom !== null && bedroom.length > 0) {
    const room = document.createElement("span")
    room.className = "lane-label-room"
    room.textContent = bedroom
    text.appendChild(room)
  }

  wrapper.appendChild(text)
  return wrapper
}

interface ActivityTimelineProps {
  replay: DayReplay | undefined
  isPending: boolean
  error: Error | null
}

export function ActivityTimeline({ replay, isPending, error }: ActivityTimelineProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const timelineRef = useRef<Timeline | null>(null)
  const customTimeIdRef = useRef<IdType | null>(null)

  const minute = useTimeStore((state) => state.minute)
  const selectedMember = useTimeStore((state) => state.selectedMember)
  const setSelectedMember = useTimeStore((state) => state.setSelectedMember)

  const replayKey =
    replay === undefined ? "" : `${replay.run}|${replay.date}|${replay.house}|${replay.policy}`

  useEffect(() => {
    const container = containerRef.current
    if (container === null || replay === undefined) return

    const items = new DataSet<TimelineActivityItem>()
    const groups = new DataSet<DataGroup>()

    replay.members.forEach((member, index) => {
      const lane = index + 1
      groups.add({
        id: member.id,
        content: buildGroupLabel(member.id, member.info.bedroom, lane),
        className: `m${lane}`,
      })
      member.activities.forEach((segment, activityIndex) => {
        const category = categorizeActivity(segment.activity, segment.location)
        items.add({
          id: `${member.id}#${activityIndex}`,
          group: member.id,
          start: minuteToDate(segment.start),
          end: minuteToDate(segment.end),
          content: segment.activity,
          title: buildTooltip(segment.start, segment.end, segment.activity, segment.location, segment.desc),
          className: `cat-${category} lane-${lane}`,
          memberId: member.id,
          lane,
          category,
        })
      })
    })

    const timeline = new Timeline(container, items, groups, {
      autoResize: true,
      height: "100%",
      width: "100%",
      stack: true,
      stackSubgroups: false,
      orientation: "top",
      showCurrentTime: false,
      showMajorLabels: false,
      showMinorLabels: true,
      showTooltips: true,
      selectable: true,
      multiselect: false,
      moveable: true,
      zoomable: true,
      zoomMin: 1000 * 60 * 30,
      zoomMax: 1000 * 60 * DAY_MINUTES,
      verticalScroll: false,
      horizontalScroll: false,
      align: "left",
      margin: { item: { horizontal: 1, vertical: 2 }, axis: 4 },
      min: minuteToDate(0),
      max: minuteToDate(DAY_MINUTES),
      start: minuteToDate(0),
      end: minuteToDate(DAY_MINUTES),
      timeAxis: { scale: "hour", step: 2 },
      tooltip: { followMouse: true, overflowMethod: "flip" },
      format: {
        minorLabels: {
          millisecond: "SSS",
          second: "HH:mm:ss",
          minute: "HH:mm",
          hour: "HH:mm",
          day: "D MMM",
        },
      },
    })

    timelineRef.current = timeline

    const cursorId = timeline.addCustomTime(minuteToDate(useTimeStore.getState().minute), "replay-cursor")
    customTimeIdRef.current = cursorId
    timeline.setCustomTimeTitle(formatHHMM(useTimeStore.getState().minute), cursorId)

    const handleClick = (properties?: { item: IdType | null }) => {
      const rawId = properties?.item
      if (typeof rawId !== "string") return
      const item = items.get(rawId)
      if (item === null) return
      setSelectedMember(item.memberId)
      timeline.setSelection([item.id])
    }

    const handleDoubleClick = (properties?: { time: Date | null }) => {
      const time = properties?.time
      if (time === null || time === undefined) return
      useTimeStore.getState().setMinute(dateToMinute(time))
    }

    timeline.on("click", handleClick)
    timeline.on("doubleClick", handleDoubleClick)

    return () => {
      timeline.off("click", handleClick)
      timeline.off("doubleClick", handleDoubleClick)
      timeline.destroy()
      timelineRef.current = null
      customTimeIdRef.current = null
      container.replaceChildren()
    }
  }, [replayKey, replay, setSelectedMember])

  useEffect(() => {
    const timeline = timelineRef.current
    const cursorId = customTimeIdRef.current
    if (timeline === null || cursorId === null) return
    const cursor = minuteToDate(minute)
    timeline.setCustomTime(cursor, cursorId)
    timeline.setCustomTimeTitle(formatHHMM(minute), cursorId)

    const visible = timeline.getWindow()
    const span = visible.end.getTime() - visible.start.getTime()
    if (span <= 0) return
    const relative = (cursor.getTime() - visible.start.getTime()) / span
    if (relative < 0 || relative > 0.97) {
      timeline.moveTo(new Date(cursor.getTime() + span * 0.25), { animation: false })
    }
  }, [minute, replayKey])

  const zoomBy = (factor: number) => {
    const timeline = timelineRef.current
    if (timeline === null) return
    const visible = timeline.getWindow()
    const center = (visible.start.getTime() + visible.end.getTime()) / 2
    const half = Math.max(
      ((visible.end.getTime() - visible.start.getTime()) / 2) * factor,
      1000 * 60 * 15,
    )
    timeline.setWindow(new Date(center - half), new Date(center + half), { animation: false })
  }

  const fitDay = () => {
    timelineRef.current?.setWindow(minuteToDate(0), minuteToDate(DAY_MINUTES), { animation: false })
  }

  const selectedLane =
    selectedMember === null || replay === undefined
      ? null
      : replay.members.findIndex((member) => member.id === selectedMember) + 1

  const status = error !== null ? "Load failed" : isPending ? "Loading" : `${replay?.members.length ?? 0} lanes`

  return (
    <Panel
      title="Activity timeline"
      hint={status}
      index={1}
      className="min-h-[280px]"
      bodyClassName="flex min-h-0 flex-col"
      actions={
        <>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={fitDay}
            aria-label="Show full day"
            title="Show full day"
          >
            <Maximize2 />
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => zoomBy(0.6)}
            aria-label="Zoom in"
            title="Zoom in"
          >
            <Plus />
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => zoomBy(1.7)}
            aria-label="Zoom out"
            title="Zoom out"
          >
            <Minus />
          </Button>
        </>
      }
    >
      <div className="flex shrink-0 items-center justify-between gap-4 border-b border-border px-4 py-2">
        <CategoryLegend />
        <span className="label-latin hidden shrink-0 xl:inline">
          {selectedMember === null ? "Select a block to locate its member" : `Selected ${selectedMember}`}
        </span>
      </div>

      {error !== null ? (
        <div className="flex flex-1 items-center justify-center px-4 py-10 text-center">
          <p className="max-w-md text-[14px] leading-relaxed text-fg-muted">
            Could not load replay data for this selection.
            <br />
            <span className="num text-fg-subtle">{error.message}</span>
          </p>
        </div>
      ) : (
        <div
          ref={containerRef}
          role="region"
          aria-label="Full-day activity timeline for every member; the axis runs from 00:00 to 24:00"
          data-selected={selectedLane === null || selectedLane <= 0 ? "" : String(selectedLane)}
          className="vis-host min-h-0 flex-1"
          style={{ minHeight: AXIS_HEIGHT_PX + Math.max(replay?.members.length ?? 0, 1) * LANE_HEIGHT_PX }}
        />
      )}

      <p className="sr-only">
        {replay === undefined
          ? "Replay data is not loaded yet."
          : replay.members
              .map(
                (member) =>
                  `${member.id} (${member.info.bedroom ?? "no room noted"}): ${member.activities.length} activity segments.`,
              )
              .join(" ")}
      </p>
    </Panel>
  )
}
