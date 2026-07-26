import { useEffect, useMemo, useState } from 'react'
import type { Floor } from '../../types/floor'
import type { Room } from '../../types/room'
import * as floorsApi from '../../api/floors'
import { FloorSwitcher } from '../../components/FloorSwitcher'
import { FloorPlanImage } from './FloorPlanImage'
import { RoomDetail } from './RoomDetail'

export function RoomView() {
  const [floors, setFloors] = useState<Floor[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [selectedFloorId, setSelectedFloorId] = useState<string | null>(null)
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null)

  useEffect(() => {
    floorsApi.getFloors().then((f) => {
      setFloors(f)
      if (f.length > 0) setSelectedFloorId(f[0].id)
    })
  }, [])

  useEffect(() => {
    if (!selectedFloorId) return
    setSelectedRoomId(null)
    floorsApi.getRoomsForFloor(selectedFloorId).then(setRooms)
  }, [selectedFloorId])

  const selectedRoom = useMemo(
    () => rooms.find((r) => r.id === selectedRoomId) ?? null,
    [rooms, selectedRoomId],
  )
  const selectedFloor = useMemo(
    () => floors.find((f) => f.id === selectedFloorId) ?? null,
    [floors, selectedFloorId],
  )

  return (
    <div className="page">
      <FloorSwitcher floors={floors} selectedFloorId={selectedFloorId} onSelect={setSelectedFloorId} />
      <div className="room-view">
        <FloorPlanImage
          planImagePath={selectedFloor?.planImagePath ?? null}
          rooms={rooms}
          selectedRoomId={selectedRoomId}
          onSelectRoom={setSelectedRoomId}
        />
        <RoomDetail room={selectedRoom} />
      </div>
    </div>
  )
}
