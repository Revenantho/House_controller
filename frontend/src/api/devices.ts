import { apiFetch } from './client'
import type { Command, Device } from '../types/device'

export async function getDevices(filter?: { roomId?: string; deviceType?: string }): Promise<Device[]> {
  const params = new URLSearchParams()
  if (filter?.roomId) params.set('room_id', filter.roomId)
  if (filter?.deviceType) params.set('type', filter.deviceType)
  const query = params.toString() ? `?${params.toString()}` : ''
  return apiFetch<Device[]>(`/devices${query}`)
}

export async function sendCommand(deviceId: string, command: Command): Promise<Device> {
  return apiFetch<Device>(`/devices/${deviceId}/command`, {
    method: 'POST',
    body: JSON.stringify({ command, params: {} }),
  })
}
