import { apiFetch } from './client'
import type { Floor } from '../types/floor'
import type { Room } from '../types/room'

export async function getFloors(): Promise<Floor[]> {
  return apiFetch<Floor[]>('/floors')
}

export async function getRoomsForFloor(floorId: string): Promise<Room[]> {
  return apiFetch<Room[]>(`/floors/${floorId}/rooms`)
}
