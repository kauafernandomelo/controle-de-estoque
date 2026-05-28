import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊', adminOnly: false },
  { to: '/products', label: 'Produtos', icon: '📦', adminOnly: false },
  { to: '/movements', label: 'Movimentações', icon: '🔄', adminOnly: false },
  { to: '/cart', label: 'Carrinho', icon: '🛒', adminOnly: false },
  { to: '/reports', label: 'Relatórios', icon: '📈', adminOnly: false },
  { to: '/categories', label: 'Categorias', icon: '🏷️', adminOnly: true },
  { to: '/brands', label: 'Marcas', icon: '🏭', adminOnly: true },
  { to: '/suppliers', label: 'Fornecedores', icon: '🚚', adminOnly: true },
  { to: '/users', label: 'Usuários', icon: '👥', adminOnly: true },
]

export function Sidebar() {
  const { isAdmin } = useAuth()

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="sidebar-logo-icon">📋</span>
        <span className="sidebar-logo-text">Controle de Estoque</span>
      </div>
      <nav className="sidebar-nav">
        {navItems
          .filter((item) => !item.adminOnly || isAdmin)
          .map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
            >
              <span className="sidebar-link-icon">{item.icon}</span>
              <span className="sidebar-link-label">{item.label}</span>
            </NavLink>
          ))}
      </nav>
    </aside>
  )
}
