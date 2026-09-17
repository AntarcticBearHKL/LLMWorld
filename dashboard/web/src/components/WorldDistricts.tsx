import { useEffect, useState } from "react"

import { useMutation, useQueryClient } from "@tanstack/react-query"

import { Copy, ListChecks, Loader2, Lock, Plus, RefreshCw, Sparkles, Trash2 } from "lucide-react"

import { copyDistrict, lockDistrict } from "@/api/client"
import type { DistrictInfo, DistrictStatus, JobInfo, WorldInfo } from "@/api/types"
import { AddHouseholdsSheet } from "@/components/AddHouseholdsSheet"
import {
  DistrictDescriptionSheet,
  DistrictStepsSheet,
  HouseholdSheet,
  NewDistrictSheet,
} from "@/components/DistrictSheets"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useJobs } from "@/hooks/useJobs"
import {
  findStepStatus,
  isActiveJob,
  useBuildState,
  useDeleteDistrict,
  useDistricts,
  worldKeys,
} from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { cn } from "@/lib/utils"

const HEAD_CLASS = "h-8 px-2.5 text-[11px] font-semibold uppercase tracking-[0.04em] text-fg-muted"

const HEAD_CENTER_CLASS = cn(HEAD_CLASS, "text-center")
const CELL_CENTER_CLASS = "num text-center tabular-nums text-fg-muted"
const CHIP_CLASS = "num rounded-full border px-2 py-px text-[12px]"
const CHIP_ON_CLASS = "border-success/40 bg-success/10 text-success"
const CHIP_OFF_CLASS = "border-border-strong bg-surface-2 text-fg-subtle"
const STATUS_CHIP_CLASS: Record<DistrictStatus, string> = {
  uninitialized: CHIP_OFF_CLASS,
  initialized: "border-energy/40 bg-energy-soft text-energy",
  locked: CHIP_ON_CLASS,
}

type DeleteNotice =
  | { kind: "error"; message: string }
  | { kind: "success"; name: string; deleted: boolean; movedTo: string | null }

function StatusChip({ status }: { status: DistrictStatus }) {
  return (
    <span
      className={cn(
        CHIP_CLASS,
        "inline-block max-w-full truncate align-middle",
        STATUS_CHIP_CLASS[status],
      )}
      title={status}
    >
      {status}
    </span>
  )
}

function HomeChip({ done }: { done: boolean }) {
  return (
    <span className={cn(CHIP_CLASS, done ? CHIP_ON_CLASS : CHIP_OFF_CLASS)}>
      {done ? "home ready" : "no home yet"}
    </span>
  )
}

function DistrictRow({
  world,
  district,
  selected,
  onSelect,
  onCopied,
  onActionError,
  onDeleteNotice,
}: {
  world: string
  district: DistrictInfo
  selected: boolean
  onSelect: () => void
  onCopied: (name: string) => void
  onActionError: (message: string | null) => void
  onDeleteNotice: (notice: DeleteNotice) => void
}) {
  const remove = useDeleteDistrict(world)
  const queryClient = useQueryClient()
  const [armed, setArmed] = useState(false)

  useEffect(() => {
    if (!armed) return
    const timer = window.setTimeout(() => setArmed(false), 6000)
    return () => window.clearTimeout(timer)
  }, [armed])

  const invalidate = (name: string) => {
    void queryClient.invalidateQueries({ queryKey: worldKeys.districts(world) })
    void queryClient.invalidateQueries({ queryKey: worldKeys.build(world, name) })
  }

  const lockMutation = useMutation({
    mutationFn: () => lockDistrict(world, district.name),
    onSuccess: () => {
      onActionError(null)
      invalidate(district.name)
    },
    onError: (error) => onActionError(errorMessage(error)),
  })

  const copyMutation = useMutation({
    mutationFn: () => copyDistrict(world, district.name, {}),
    onSuccess: (created) => {
      onActionError(null)
      invalidate(district.name)
      invalidate(created.name)
      onCopied(created.name)
    },
    onError: (error) => onActionError(errorMessage(error)),
  })

  return (
    <TableRow
      aria-selected={selected}
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(event) => {
        if (event.target !== event.currentTarget) return
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault()
          onSelect()
        }
      }}
      className={cn(
        "h-10 cursor-pointer border-b border-border/60 hover:bg-item-hover",
        selected && "bg-item-selected",
      )}
    >
      <TableCell className="text-center align-middle">
        <span
          className="num block truncate text-[13px] font-semibold tracking-[-0.01em] text-fg"
          title={district.name}
        >
          {district.name}
        </span>
      </TableCell>

      <TableCell className="text-center align-middle">
        <StatusChip status={district.status} />
      </TableCell>

      <TableCell className={CELL_CENTER_CLASS}>
        <span className="block truncate" title={String(district.house_count)}>
          {district.house_count}
        </span>
      </TableCell>

      <TableCell
        className="text-center whitespace-nowrap"
        onClick={(event) => event.stopPropagation()}
      >
        <span className="inline-flex items-center gap-1">
          {district.status === "initialized" ? (
            <Button
              variant="ghost"
              size="icon-xs"
              className="text-brand"
              title="Lock this district (one-way)"
              aria-label="Lock this district (one-way)"
              disabled={lockMutation.isPending}
              onClick={() => lockMutation.mutate()}
            >
              {lockMutation.isPending ? <Loader2 className="animate-spin" /> : <Lock />}
            </Button>
          ) : null}
          {district.status === "locked" ? (
            <Button
              variant="ghost"
              size="icon-xs"
              className="text-fg-subtle"
              title="Copy this district (new initialized district, no households)"
              aria-label="Copy this district"
              disabled={copyMutation.isPending}
              onClick={() => copyMutation.mutate()}
            >
              {copyMutation.isPending ? <Loader2 className="animate-spin" /> : <Copy />}
            </Button>
          ) : null}
          <Button
            variant="ghost"
            size={armed ? "xs" : "icon-xs"}
            disabled={remove.isPending}
            aria-label="Delete district"
            title={
              armed
                ? "Click again to delete"
                : "Delete this district (moves to output/_trash/, recoverable)"
            }
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => {
              if (!armed) {
                setArmed(true)
                return
              }
              remove.mutate(district.name, {
                onSuccess: (data) => {
                  onDeleteNotice({
                    kind: "success",
                    name: data.name,
                    deleted: data.deleted,
                    movedTo: data.moved_to,
                  })
                },
                onError: (error) => {
                  onDeleteNotice({ kind: "error", message: errorMessage(error) })
                },
              })
            }}
            className={cn(
              "text-danger",
              armed && "bg-danger/10 hover:bg-danger/15 hover:text-danger",
            )}
          >
            {remove.isPending ? <Loader2 className="animate-spin" /> : <Trash2 />}
            {armed ? "Confirm delete" : null}
          </Button>
        </span>
      </TableCell>
    </TableRow>
  )
}

function DistrictHouseholdsPanel({
  world,
  district,
  jobs,
  descriptionOpen,
  onDescriptionOpenChange,
  stepsOpen,
  onStepsOpenChange,
  addHouseholdsOpen,
  onAddHouseholdsOpenChange,
  houseOpen,
  onHouseOpenChange,
}: {
  world: string
  district: DistrictInfo
  jobs: JobInfo[]
  descriptionOpen: boolean
  onDescriptionOpenChange: (open: boolean) => void
  stepsOpen: boolean
  onStepsOpenChange: (open: boolean) => void
  addHouseholdsOpen: boolean
  onAddHouseholdsOpenChange: (open: boolean) => void
  houseOpen: string | null
  onHouseOpenChange: (house: string | null) => void
}) {
  const activeJob = jobs.filter((job) => (job.district ?? "") === district.name).some(isActiveJob)
  const buildQuery = useBuildState(world, district.name, activeJob)
  const buildState = buildQuery.data
  const districtStep = buildState === undefined ? null : findStepStatus(buildState.steps, "district")
  const homeStep = buildState === undefined ? null : findStepStatus(buildState.steps, "home")
  const houses = buildState?.houses ?? []
  const homeStatusFor = (house: string) =>
    homeStep?.houses.find((item) => item.house === house) ?? null
  const openHomeStatus = houseOpen === null ? null : homeStatusFor(houseOpen)
  const isLocked = district.status === "locked"
  const householdGate =
    district.status === "locked"
      ? null
      : district.status === "uninitialized"
        ? "Write the district description first."
        : "Lock this district first."

  return (
    <section className="card flex min-h-0 flex-col overflow-hidden">
      <header className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-3.5 py-2.5">
        <span
          className="num min-w-0 truncate text-[15px] font-semibold tracking-[-0.01em] text-fg"
          title={district.name}
        >
          {district.name}
        </span>
        <span className="ml-auto flex items-center gap-1">
          <Button variant="outline" size="sm" onClick={() => onDescriptionOpenChange(true)}>
            <Sparkles aria-hidden />
            Description
          </Button>
          <Button
            size="sm"
            disabled={householdGate !== null}
            title={householdGate ?? undefined}
            onClick={() => onAddHouseholdsOpenChange(true)}
          >
            {householdGate === null ? <Plus aria-hidden /> : <Lock aria-hidden />}
            Add household
          </Button>
          <Button
            variant="ghost"
            size="icon-xs"
            title="Steps"
            aria-label="Steps"
            onClick={() => onStepsOpenChange(true)}
          >
            <ListChecks aria-hidden />
          </Button>
        </span>
      </header>

      <div className="relative min-h-0 flex-1">
        <div
          className={cn("h-full overflow-auto", !isLocked && "pointer-events-none")}
          aria-hidden={!isLocked}
        >
        <Table className="w-full text-[13px]">
          <TableHeader>
            <TableRow className="border-b border-border hover:bg-transparent">
              <TableHead className={HEAD_CLASS}>Household</TableHead>
              <TableHead className={HEAD_CLASS}>Home</TableHead>
              <TableHead className={HEAD_CLASS}>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {buildQuery.isPending ? (
              <TableRow className="hover:bg-transparent">
                <TableCell colSpan={3} className="p-6 text-center text-[13px] text-fg-subtle">
                  Loading households…
                </TableCell>
              </TableRow>
            ) : buildQuery.isError ? (
              <TableRow className="hover:bg-transparent">
                <TableCell colSpan={3} className="p-6 text-center text-[13px] text-fg-subtle">
                  Households unavailable: {errorMessage(buildQuery.error)}
                </TableCell>
              </TableRow>
            ) : houses.length === 0 ? (
              <TableRow className="hover:bg-transparent">
                <TableCell colSpan={3} className="p-6 text-center text-[13px] text-fg-subtle">
                  No households in this district yet.
                </TableCell>
              </TableRow>
            ) : (
              houses.map((house) => {
                const status = homeStatusFor(house)
                const done = status?.done ?? false
                return (
                  <TableRow key={house} className="h-10 border-b border-border/60 hover:bg-item-hover">
                    <TableCell className="align-middle">
                      <span className="num text-[13px] font-semibold tracking-[-0.01em] text-fg">
                        {house}
                      </span>
                    </TableCell>
                    <TableCell className="align-middle">
                      <HomeChip done={done} />
                    </TableCell>
                    <TableCell className="text-right whitespace-nowrap">
                      <Button variant="outline" size="xs" onClick={() => onHouseOpenChange(house)}>
                        Open
                      </Button>
                    </TableCell>
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
        </div>
        {isLocked ? null : (
          <div className="glass-lg absolute inset-0 flex flex-col items-center justify-center gap-2.5 px-6">
            <span className="flex size-9 items-center justify-center rounded-full border border-border-strong bg-surface-2 text-fg-subtle">
              <Lock className="size-4" aria-hidden />
            </span>
            <p className="max-w-[260px] text-center text-[13px] leading-relaxed text-fg-muted">
              Lock this district to start generating households.
            </p>
          </div>
        )}
      </div>

      <DistrictDescriptionSheet
        world={world}
        district={district}
        districtRunnable={districtStep?.runnable ?? false}
        districtBlockedReason={districtStep?.blocked_reason ?? null}
        open={descriptionOpen}
        onOpenChange={onDescriptionOpenChange}
      />
      <DistrictStepsSheet
        world={world}
        district={district.name}
        open={stepsOpen}
        onOpenChange={onStepsOpenChange}
      />
      <AddHouseholdsSheet
        world={world}
        district={district.name}
        districtStatus={district.status}
        open={addHouseholdsOpen}
        onOpenChange={onAddHouseholdsOpenChange}
      />
      <HouseholdSheet
        world={world}
        district={district.name}
        house={houseOpen ?? ""}
        homeDone={openHomeStatus?.done ?? false}
        homeRunnable={openHomeStatus?.runnable ?? false}
        homeBlockedReason={openHomeStatus?.blocked_reason ?? homeStep?.blocked_reason ?? null}
        open={houseOpen !== null}
        onOpenChange={(open) => {
          if (!open) onHouseOpenChange(null)
        }}
      />
    </section>
  )
}

export function WorldDistricts({ info }: { info: WorldInfo }) {
  const world = info.world_id
  const districtsQuery = useDistricts(world)
  const jobsQuery = useJobs()
  const jobs = jobsQuery.data ?? []
  const worldJobs = jobs.filter((job) => job.kind === "build" && job.world === world)
  const districts = districtsQuery.data ?? []

  const [selected, setSelected] = useState("")
  const [newOpen, setNewOpen] = useState(false)
  const [descriptionOpen, setDescriptionOpen] = useState(false)
  const [stepsOpen, setStepsOpen] = useState(false)
  const [addHouseholdsOpen, setAddHouseholdsOpen] = useState(false)
  const [houseOpen, setHouseOpen] = useState<string | null>(null)
  const [deleteNotice, setDeleteNotice] = useState<DeleteNotice | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  useEffect(() => {
    if (districtsQuery.isPending) return
    const list = districtsQuery.data ?? []
    if (list.length === 0) {
      if (selected !== "") queueMicrotask(() => setSelected(""))
      return
    }
    if (!list.some((d) => d.name === selected)) {
      queueMicrotask(() => setSelected(list[0]?.name ?? ""))
    }
  }, [districtsQuery.isPending, districtsQuery.data, selected])

  const selectedDistrict = districts.find((district) => district.name === selected) ?? null
  const isEmpty = !districtsQuery.isPending && !districtsQuery.isError && districts.length === 0

  if (isEmpty) {
    return (
      <section className="card flex min-h-0 flex-1 flex-col overflow-hidden">
        <div className="grid min-h-full flex-1 grid-rows-[auto_1fr_auto]">
          <div className="row-start-2 flex items-center justify-center px-6 py-8">
            <div className="flex w-full max-w-[440px] flex-col items-center text-center">
              <p className="text-[15px] font-semibold text-fg">No districts yet</p>
              <p className="mt-1.5 text-[13px] leading-relaxed text-fg-muted">
                A district is this world's first layer. Name it, write its description, and lock it —
                only then can you generate households.
              </p>
              <Button size="sm" className="mt-4" onClick={() => setNewOpen(true)}>
                <Plus />
                New district
              </Button>
            </div>
          </div>
        </div>

        <NewDistrictSheet
          world={world}
          districtNames={districts.map((district) => district.name)}
          open={newOpen}
          onOpenChange={setNewOpen}
          onCreated={(name) => setSelected(name)}
        />
      </section>
    )
  }

  return (
    <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[minmax(320px,38%)_minmax(0,1fr)]">
      <section className="card flex min-h-0 flex-col overflow-hidden">
        <header className="flex shrink-0 items-center gap-2 border-b border-border px-3.5 py-2.5">
          <Button
            variant="ghost"
            size="icon-sm"
            className="ml-auto"
            aria-label="Refresh districts"
            onClick={() => void districtsQuery.refetch()}
          >
            <RefreshCw />
          </Button>
          <Button variant="outline" size="sm" onClick={() => setNewOpen(true)}>
            <Plus />
            New district
          </Button>
        </header>

        <div className="min-h-0 flex-1 overflow-auto">
          <Table className="w-full table-fixed text-[13px]">
            <colgroup>
              <col className="w-1/4" />
              <col className="w-1/4" />
              <col className="w-1/4" />
              <col className="w-1/4" />
            </colgroup>
            <TableHeader>
              <TableRow className="border-b border-border hover:bg-transparent">
                <TableHead className={HEAD_CENTER_CLASS}>
                  <span className="block truncate" title="District">
                    District
                  </span>
                </TableHead>
                <TableHead className={HEAD_CENTER_CLASS}>
                  <span className="block truncate" title="Status">
                    Status
                  </span>
                </TableHead>
                <TableHead className={HEAD_CENTER_CLASS}>
                  <span className="block truncate" title="Households">
                    Households
                  </span>
                </TableHead>
                <TableHead className={HEAD_CENTER_CLASS}>
                  <span className="block truncate" title="Actions">
                    Actions
                  </span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {districtsQuery.isPending ? (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={4} className="p-6 text-center text-[13px] text-fg-subtle">
                    Loading districts…
                  </TableCell>
                </TableRow>
              ) : districtsQuery.isError ? (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={4} className="p-6 text-center text-[13px] text-fg-subtle">
                    <span className="flex flex-col items-center gap-2">
                      <span className="text-[13px] text-danger">
                        Failed to load districts: {errorMessage(districtsQuery.error)}
                      </span>
                      <Button variant="outline" size="xs" onClick={() => void districtsQuery.refetch()}>
                        Retry
                      </Button>
                    </span>
                  </TableCell>
                </TableRow>
              ) : (
                districts.map((district) => (
                  <DistrictRow
                    key={district.name}
                    world={world}
                    district={district}
                    selected={district.name === selected}
                    onSelect={() => setSelected(district.name)}
                    onCopied={setSelected}
                    onActionError={setActionError}
                    onDeleteNotice={setDeleteNotice}
                  />
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {deleteNotice === null && actionError === null && !jobsQuery.isError ? null : (
          <div className="shrink-0 border-t border-border px-3.5 py-2">
            {actionError !== null ? (
              <p className="text-[12px] text-danger">District action failed: {actionError}</p>
            ) : null}
            {deleteNotice?.kind === "error" ? (
              <p className="text-[12px] text-danger">Delete failed: {deleteNotice.message}</p>
            ) : null}
            {deleteNotice?.kind === "success" ? (
              <p className="min-w-0 text-[12px] text-fg-subtle">
                {deleteNotice.deleted
                  ? `Deleted ${deleteNotice.name} — recoverable from output/_trash/`
                  : `Nothing deleted for ${deleteNotice.name}`}
                {deleteNotice.movedTo !== null ? (
                  <span
                    className="num ml-1 inline-block max-w-full truncate align-bottom"
                    title={deleteNotice.movedTo}
                  >
                    {deleteNotice.movedTo}
                  </span>
                ) : null}
              </p>
            ) : null}
            {jobsQuery.isError ? (
              <p className="text-[12px] text-danger">
                Failed to load jobs; recent run status may be incomplete:{" "}
                {errorMessage(jobsQuery.error)}
              </p>
            ) : null}
          </div>
        )}

        <NewDistrictSheet
          world={world}
          districtNames={districts.map((district) => district.name)}
          open={newOpen}
          onOpenChange={setNewOpen}
          onCreated={(name) => setSelected(name)}
        />
      </section>

      {selectedDistrict === null ? null : (
        <DistrictHouseholdsPanel
          key={selectedDistrict.name}
          world={world}
          district={selectedDistrict}
          jobs={worldJobs}
          descriptionOpen={descriptionOpen}
          onDescriptionOpenChange={setDescriptionOpen}
          stepsOpen={stepsOpen}
          onStepsOpenChange={setStepsOpen}
          addHouseholdsOpen={addHouseholdsOpen}
          onAddHouseholdsOpenChange={setAddHouseholdsOpen}
          houseOpen={houseOpen}
          onHouseOpenChange={setHouseOpen}
        />
      )}
    </div>
  )
}
