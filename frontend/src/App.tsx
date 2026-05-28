import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { PrivateRoute, AdminRoute } from './routes/PrivateRoute'
import { DashboardLayout } from './layouts/DashboardLayout'
import { ToastProvider } from './components/Toast'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { ProductList } from './pages/Products/ProductList'
import { ProductDetail } from './pages/Products/ProductDetail'
import { MovementList } from './pages/Movements/MovementList'
import { Reports } from './pages/Reports/Reports'
import { UserList } from './pages/Users/UserList'
import { BrandList } from './pages/Brands/BrandList'
import { SupplierList } from './pages/Suppliers/SupplierList'
import { CategoryList } from './pages/Categories/CategoryList'
import { CartPage } from './pages/Cart/CartPage'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
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
            <Route path="/products/:id" element={<ProductDetail />} />
            <Route path="/movements" element={<MovementList />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/cart" element={<CartPage />} />
            <Route
              path="/users"
              element={
                <AdminRoute>
                  <UserList />
                </AdminRoute>
              }
            />
            <Route
              path="/brands"
              element={
                <AdminRoute>
                  <BrandList />
                </AdminRoute>
              }
            />
            <Route
              path="/suppliers"
              element={
                <AdminRoute>
                  <SupplierList />
                </AdminRoute>
              }
            />
            <Route
              path="/categories"
              element={
                <AdminRoute>
                  <CategoryList />
                </AdminRoute>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
