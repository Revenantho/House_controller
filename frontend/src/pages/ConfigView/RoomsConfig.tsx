import { useEffect, useState } from 'react'
import type { Floor } from '../../types/floor'
import type { Room } from '../../types/room'
import * as floorsApi from '../../api/floors'

// Stub phase 1 : lecture seule. L'édition du zone_shape (formulaire, pas encore d'éditeur visuel
// à la souris — cf. tâche différée) arrive en phase 2.
export function RoomsConfig() {
  const [floors, setFloors] = useState<Floor[]>([])
  const [roomsByFloor, setRoomsByFloor] = useState<Record<string, Room[]>>({})

  useEffect(() => {
    floorsApi.getFloors().then(async (f) => {
      setFloors(f)
      const entries = await Promise.all(
        f.map(async (floor) => [floor.id, await floorsApi.getRoomsForFloor(floor.id)] as const),
      )
      setRoomsByFloor(Object.fromEntries(entries))
    })
  }, [])

  return (
    <div className="equipment-group">
      <h3>Pièces</h3>
      {floors.map((floor) => (
        <div key={floor.id}>
          <strong>{floor.name}</strong>
          <ul>
            {(roomsByFloor[floor.id] ?? []).map((room) => (
              <li key={room.id}>{room.name}</li>
            ))}
          </ul>
        </div>
      ))}
      <p className="stub-note">Édition des zones cliquables disponible une fois le backend connecté.</p>
    </div>
  )
}
