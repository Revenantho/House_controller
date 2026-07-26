import type { Command, Device } from '../types/device'
import { useDeviceState } from '../context/DeviceStateContext'

const COMMAND_LABELS: Record<Command, string> = {
  OPEN: 'Ouvrir',
  CLOSE: 'Fermer',
  STOP: 'Stop',
  SET_POSITION: 'Position',
}

function stateLabel(device: Device): string {
  if (!device.lastState || device.lastState.isOpen === null) return 'État inconnu'
  return device.lastState.isOpen ? 'Ouvert' : 'Fermé'
}

export function DeviceCard({ device }: { device: Device }) {
  const { sendCommand } = useDeviceState()

  return (
    <div className="device-card">
      <h4>{device.name}</h4>
      <div className="state">{stateLabel(device)}</div>
      <div className="actions">
        {device.supportedCommands
          .filter((c) => c !== 'SET_POSITION')
          .map((command) => (
            <button key={command} onClick={() => sendCommand(device.id, command)}>
              {COMMAND_LABELS[command]}
            </button>
          ))}
      </div>
    </div>
  )
}
