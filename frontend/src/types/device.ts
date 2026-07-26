export type DeviceType = 'ROLLER_SHUTTER' | 'GARAGE_DOOR'

export type Command = 'OPEN' | 'CLOSE' | 'STOP' | 'SET_POSITION'

export interface DeviceState {
  isOpen: boolean | null
  position: number | null
  raw: Record<string, unknown>
}

export interface Device {
  id: string
  name: string
  deviceType: DeviceType
  roomId: string | null
  adapterName: string
  supportedCommands: Command[]
  lastState: DeviceState | null
  lastSyncedAt: string | null
}
