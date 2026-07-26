import { useDeviceState } from '../../context/DeviceStateContext'

// Stub phase 1 : lecture seule. La réassignation de pièce / renommage (PATCH /api/devices/{id})
// arrive en phase 2.
export function DevicesConfig() {
  const { devices, loading } = useDeviceState()

  if (loading) return <p>Chargement...</p>

  return (
    <div className="equipment-group">
      <h3>Équipements</h3>
      <ul>
        {devices.map((device) => (
          <li key={device.id}>
            {device.name} — {device.deviceType} — pièce : {device.roomId ?? 'non assignée'}
          </li>
        ))}
      </ul>
      <p className="stub-note">Réassignation de pièce et renommage disponibles une fois le backend connecté.</p>
    </div>
  )
}
