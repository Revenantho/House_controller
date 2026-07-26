import { apiFetch } from './client'
import type { Scenario } from '../types/scenario'

export async function getScenarios(): Promise<Scenario[]> {
  return apiFetch<Scenario[]>('/scenarios')
}
