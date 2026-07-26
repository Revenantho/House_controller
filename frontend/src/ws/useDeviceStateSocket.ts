import { useEffect, useRef } from 'react'
import type { Device } from '../types/device'

// Phase 1 : le backend et son endpoint WS n'existent pas encore (phase 2).
// Ce hook tente la connexion mais échoue silencieusement tant que /api/ws/state n'existe pas,
// pour ne pas casser le mode mock. Une fois le backend prêt, il alimentera DeviceStateContext.
export function useDeviceStateSocket(onDeviceUpdate: (device: Device) => void) {
  const onUpdateRef = useRef(onDeviceUpdate)
  onUpdateRef.current = onDeviceUpdate

  useEffect(() => {
    let socket: WebSocket | null = null
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      socket = new WebSocket(`${protocol}://${window.location.host}/api/ws/state`)

      socket.onmessage = (event) => {
        try {
          const device = JSON.parse(event.data) as Device
          onUpdateRef.current(device)
        } catch {
          // message non reconnu, ignoré
        }
      }
      socket.onerror = () => {
        // pas de backend en phase 1 : attendu, on n'affiche rien à l'utilisateur
      }
    } catch {
      // WebSocket indisponible, on reste en mode mock
    }

    return () => socket?.close()
  }, [])
}
