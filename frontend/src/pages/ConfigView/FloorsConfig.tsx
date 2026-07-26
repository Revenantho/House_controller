import { useEffect, useState } from 'react'
import type { Floor } from '../../types/floor'
import * as floorsApi from '../../api/floors'

// Stub phase 1 : lecture seule. Le CRUD réel (POST/PATCH/DELETE /api/floors) arrive en phase 2.
export function FloorsConfig() {
  const [floors, setFloors] = useState<Floor[]>([])

  useEffect(() => {
    floorsApi.getFloors().then(setFloors)
  }, [])

  return (
    <div className="equipment-group">
      <h3>Étages</h3>
      <ul>
        {floors.map((floor) => (
          <li key={floor.id}>
            {floor.name} (ordre {floor.displayOrder})
          </li>
        ))}
      </ul>
      <p className="stub-note">Ajout/édition/suppression d'étage disponible une fois le backend connecté.</p>
    </div>
  )
}
