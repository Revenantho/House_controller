import type { Command } from './device'

export interface ScenarioAction {
  id: string
  deviceId: string
  command: Command
  params: Record<string, unknown>
  order: number
}

export interface Scenario {
  id: string
  name: string
  enabled: boolean
  daysOfWeek: number[]
  time: string
  actions: ScenarioAction[]
}
