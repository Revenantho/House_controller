import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  if (!user) return null

  return (
    <nav className="navbar">
      <NavLink to="/rooms">Pièces</NavLink>
      <NavLink to="/equipment">Équipements</NavLink>
      <NavLink to="/scenarios">Scénarios</NavLink>
      <NavLink to="/config">Configuration</NavLink>
      <span className="spacer" />
      <span>{user.username}</span>
      <button onClick={handleLogout}>Déconnexion</button>
    </nav>
  )
}
