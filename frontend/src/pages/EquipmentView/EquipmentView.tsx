import { useMemo } from 'react'
import type { DeviceType } from '../../types/device'
import { useDeviceState } from '../../context/DeviceStateContext'
import { DeviceCard } from '../../components/DeviceCard'

const TYPE_LABELS: Record<DeviceType, string> = {
  ROLLER_SHUTTER: 'Volets roulants',
  GARAGE_DOOR: 'Portes de garage',
}

export function EquipmentView() {
  const { devices, loading } = useDeviceState()

  const groups = useMemo(() => {
    const map = new Map<DeviceType, typeof devices>()
    for (const device of devices) {
      const list = map.get(device.deviceType) ?? []
      list.push(device)
      map.set(device.deviceType, list)
    }
    return map
  }, [devices])

  if (loading) return <div className="page">Chargement des équipements...</div>

  return (
    <div className="page">
      {[...groups.entries()].map(([type, list]) => (
        <div key={type} className="equipment-group">
          <h3>{TYPE_LABELS[type] ?? type}</h3>
          <div className="device-grid">
            {list.map((device) => (
              <DeviceCard key={device.id} device={device} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
