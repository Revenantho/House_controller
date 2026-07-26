import { useMemo } from 'react'
import type { Room } from '../../types/room'
import { useDeviceState } from '../../context/DeviceStateContext'
import { DeviceCard } from '../../components/DeviceCard'

export function RoomDetail({ room }: { room: Room | null }) {
  const { devices } = useDeviceState()

  const roomDevices = useMemo(
    () => (room ? devices.filter((d) => d.roomId === room.id) : []),
    [devices, room],
  )

  if (!room) {
    return (
      <div className="room-detail">
        <p className="stub-note">Clique sur une pièce du plan pour voir ses équipements.</p>
      </div>
    )
  }

  return (
    <div className="room-detail">
      <h3>{room.name}</h3>
      {roomDevices.length === 0 ? (
        <p className="stub-note">Aucun équipement associé à cette pièce.</p>
      ) : (
        <div className="device-grid">
          {roomDevices.map((device) => (
            <DeviceCard key={device.id} device={device} />
          ))}
        </div>
      )}
    </div>
  )
}
