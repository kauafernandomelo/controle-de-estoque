import { useAuth } from '../../hooks/useAuth'
import { translateRole } from '../../utils/format'

export function Topbar() {
  const { user, logout } = useAuth()

  return (
    <header className="topbar">
      <div className="topbar-left">
        <span className="topbar-greeting">
          Olá, <strong>{user?.nome || 'Usuário'}</strong>
        </span>
      </div>
      <div className="topbar-right">
        <span className="topbar-role">{user ? translateRole(user.perfil) : ''}</span>
        <button className="btn btn-sm btn-outline" onClick={logout} type="button">
          Sair
        </button>
      </div>
    </header>
  )
}
