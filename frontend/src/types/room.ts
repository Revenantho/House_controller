export interface ZonePoint {
  xPct: number
  yPct: number
}

export interface Room {
  id: string
  floorId: string
  name: string
  zoneShape: ZonePoint[]
}
