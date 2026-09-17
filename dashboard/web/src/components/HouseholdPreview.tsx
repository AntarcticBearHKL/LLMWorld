import type { ApplianceInfo, HouseholdInfo, MemberInfo, RoomInfo } from "@/api/types"
import { useDistrictHousehold } from "@/hooks/useWorldBuild"
import { errorMessage } from "@/lib/errors"
import { countLabel } from "@/lib/format"

interface HouseholdPreviewProps {
  world: string
  district: string
  house: string
}

const roomList = (info: HouseholdInfo): RoomInfo[] =>
  info.room_meta.length > 0 ? info.room_meta : info.rooms.map((name) => ({ name, size: null }))

const groupByRoom = (info: HouseholdInfo): Map<string, ApplianceInfo[]> => {
  const grouped = new Map<string, ApplianceInfo[]>()
  for (const appliance of info.appliances) {
    const room = appliance.room ?? ""
    const bucket = grouped.get(room)
    if (bucket === undefined) grouped.set(room, [appliance])
    else bucket.push(appliance)
  }
  return grouped
}

function ApplianceChip({ appliance }: { appliance: ApplianceInfo }) {
  return (
    <span
      className="chip t-body"
      title={appliance.owner === null ? appliance.type : `${appliance.type} · ${appliance.owner}`}
    >
      <span>{appliance.name}</span>
      <span className="num shrink-0 t-caption">{Math.round(appliance.power_watts)} W</span>
    </span>
  )
}

function RoomRow({
  name,
  size,
  appliances,
}: {
  name: string
  size: number | null
  appliances: ApplianceInfo[]
}) {
  const totalWatts = appliances.reduce((sum, item) => sum + item.power_watts, 0)

  return (
    <li className="flex flex-col gap-1 rounded-lg border border-border bg-surface px-2.5 py-1.5">
      <span className="flex flex-wrap items-baseline gap-x-2">
        <span className="t-body">{name}</span>
        {size !== null ? <span className="num t-caption">{size} m²</span> : null}
        {totalWatts > 0 ? (
          <span className="num ml-auto t-caption">{Math.round(totalWatts)} W</span>
        ) : null}
      </span>
      {appliances.length === 0 ? (
        <span className="t-caption">No appliances.</span>
      ) : (
        <span className="flex flex-wrap gap-1.5">
          {appliances.map((appliance) => (
            <ApplianceChip key={appliance.unique_id} appliance={appliance} />
          ))}
        </span>
      )}
    </li>
  )
}

function MemberRow({ member }: { member: MemberInfo }) {
  return (
    <li className="rounded-lg border border-border bg-surface px-2.5 py-1.5">
      <div className="flex flex-wrap items-baseline gap-x-2">
        <span className="num t-body">{member.id}</span>
        <span className="num t-caption">
          {member.age !== null ? `${member.age} y` : "age unknown"}
        </span>
        <span className="t-caption">{member.gender ?? "gender unknown"}</span>
      </div>
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 t-caption">
        <span>{member.occupation ?? "occupation unknown"}</span>
        {member.bedroom !== null ? <span className="chip t-body">{member.bedroom}</span> : null}
      </div>
    </li>
  )
}

export function HouseholdPreview({ world, district, house }: HouseholdPreviewProps) {
  const query = useDistrictHousehold(world, district, house, true)

  if (query.isPending) {
    return <p className="t-caption">Loading rooms, members and appliances…</p>
  }

  if (query.isError) {
    return (
      <p className="t-caption text-danger">
        Failed to load this household: {errorMessage(query.error)}
      </p>
    )
  }

  const info = query.data
  if (info === undefined) {
    return <p className="t-caption">No household data for {house}.</p>
  }

  const rooms = roomList(info)
  const grouped = groupByRoom(info)
  const unassigned = grouped.get("") ?? []
  const knownRooms = new Set(rooms.map((room) => room.name))
  const extraRooms = [...grouped.keys()].filter((name) => name.length > 0 && !knownRooms.has(name))
  const emptyRooms = rooms.length === 0 && extraRooms.length === 0 && unassigned.length === 0

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
        <span className="t-title">{info.household_type}</span>
        {info.home_name !== null ? (
          <span className="num t-caption">{info.home_name}</span>
        ) : null}
        {info.home_type !== null ? (
          <span className="t-caption">{info.home_type}</span>
        ) : null}
        {info.home_size !== null ? (
          <span className="num t-caption">{info.home_size} m²</span>
        ) : null}
        <span className="label-micro ml-auto">
          {countLabel(rooms.length, "room")} · {countLabel(info.members.length, "member")} ·{" "}
          {countLabel(info.appliances.length, "appliance")}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        <section className="flex flex-col gap-2">
          <span className="label-micro">Rooms &amp; appliances</span>
          {emptyRooms ? (
            <p className="t-caption">No rooms recorded for this household.</p>
          ) : (
            <ul className="flex flex-col gap-1.5">
              {rooms.map((room) => (
                <RoomRow
                  key={room.name}
                  name={room.name}
                  size={room.size}
                  appliances={grouped.get(room.name) ?? []}
                />
              ))}
              {extraRooms.map((name) => (
                <RoomRow key={name} name={name} size={null} appliances={grouped.get(name) ?? []} />
              ))}
              {unassigned.length > 0 ? (
                <RoomRow name="Unassigned" size={null} appliances={unassigned} />
              ) : null}
            </ul>
          )}
        </section>

        <section className="flex flex-col gap-2">
          <span className="label-micro">Members</span>
          {info.members.length === 0 ? (
            <p className="t-caption">No members recorded for this household.</p>
          ) : (
            <ul className="flex flex-col gap-1.5">
              {info.members.map((member) => (
                <MemberRow key={member.id} member={member} />
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}
