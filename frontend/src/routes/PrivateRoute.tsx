import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

function PageLoader() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
      Carregando...
    </div>
  )
}

export function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { token, loading } = useAuth()
  if (loading) return <PageLoader />
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { token, isAdmin, loading } = useAuth()
  if (loading) return <PageLoader />
  if (!token) return <Navigate to="/login" replace />
  if (!isAdmin) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}
