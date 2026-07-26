import { FloorsConfig } from './FloorsConfig'
import { RoomsConfig } from './RoomsConfig'
import { DevicesConfig } from './DevicesConfig'

export function ConfigView() {
  return (
    <div className="page">
      <h2>Configuration de la maison</h2>
      <FloorsConfig />
      <RoomsConfig />
      <DevicesConfig />
    </div>
  )
}
