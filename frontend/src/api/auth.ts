import { apiFetch } from './client'

export interface User {
  id: string
  username: string
}

export async function login(username: string, password: string): Promise<User> {
  return apiFetch<User>('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
}

export async function logout(): Promise<void> {
  await apiFetch<void>('/auth/logout', { method: 'POST' })
}

export async function me(): Promise<User | null> {
  try {
    return await apiFetch<User>('/auth/me')
  } catch {
    return null
  }
}
