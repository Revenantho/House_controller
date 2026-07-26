import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import * as devicesApi from '../api/devices'
import type { Command, Device } from '../types/device'
import { useDeviceStateSocket } from '../ws/useDeviceStateSocket'
import { useAuth } from './AuthContext'

interface DeviceStateContextValue {
  devices: Device[]
  loading: boolean
  refresh: () => Promise<void>
  sendCommand: (deviceId: string, command: Command) => Promise<void>
}

const DeviceStateContext = createContext<DeviceStateContextValue | undefined>(undefined)

export function DeviceStateProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    const all = await devicesApi.getDevices()
    setDevices(all)
    setLoading(false)
  }, [])

  // Le rafraîchissement complet ne doit se déclencher qu'une fois authentifié : sinon
  // le premier appel (fait au montage, avant tout login) échoue en 401 et ne se
  // relance jamais après la connexion. On réinitialise aussi au logout.
  useEffect(() => {
    if (user) {
      refresh()
    } else {
      setDevices([])
      setLoading(false)
    }
  }, [user, refresh])

  const applyDeviceUpdate = useCallback((updated: Device) => {
    setDevices((prev) => prev.map((d) => (d.id === updated.id ? updated : d)))
  }, [])

  // Se connecte au flux WebSocket temps réel dès que le backend (phase 2) l'exposera.
  useDeviceStateSocket(applyDeviceUpdate)

  const sendCommand = useCallback(
    async (deviceId: string, command: Command) => {
      const updated = await devicesApi.sendCommand(deviceId, command)
      applyDeviceUpdate(updated)
    },
    [applyDeviceUpdate],
  )

  return (
    <DeviceStateContext.Provider value={{ devices, loading, refresh, sendCommand }}>
      {children}
    </DeviceStateContext.Provider>
  )
}

export function useDeviceState(): DeviceStateContextValue {
  const ctx = useContext(DeviceStateContext)
  if (!ctx) throw new Error('useDeviceState doit être utilisé dans un DeviceStateProvider')
  return ctx
}
