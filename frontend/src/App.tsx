import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { PrivateRoute, AdminRoute } from './routes/PrivateRoute'
import { DashboardLayout } from './layouts/DashboardLayout'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { ProductList } from './pages/Products/ProductList'
import { MovementList } from './pages/Movements/MovementList'
import { Reports } from './pages/Reports/Reports'
import { UserList } from './pages/Users/UserList'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            element={
              <PrivateRoute>
                <DashboardLayout />
              </PrivateRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/products" element={<ProductList />} />
            <Route path="/movements" element={<MovementList />} />
            <Route path="/reports" element={<Reports />} />
            <Route
              path="/users"
              element={
                <AdminRoute>
                  <UserList />
                </AdminRoute>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
