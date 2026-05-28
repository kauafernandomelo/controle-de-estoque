import { Outlet } from 'react-router-dom'
import { Sidebar } from '../components/Layout/Sidebar'
import { Topbar } from '../components/Layout/Topbar'

export function DashboardLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Topbar />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
