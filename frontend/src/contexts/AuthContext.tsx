import { createContext, useCallback, useState, type ReactNode } from 'react'
import type { AuthState, LoginResponse, UserRead } from '../types/auth'
import api from '../api/client'

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
}

function decodeToken(token: string): { sub: string } | null {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch {
    return null
  }
}

const STORAGE_USER = 'stored_user'

export const AuthContext = createContext<AuthContextType>(null!)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    if (!token) {
      return { user: null, token: null, refreshToken: null, loading: false }
    }
    let user: UserRead | null = null
    try {
      const stored = localStorage.getItem(STORAGE_USER)
      if (stored) user = JSON.parse(stored)
    } catch {}
    if (!user) {
      const payload = decodeToken(token)
      if (payload) {
        user = {
          id: payload.sub,
          nome: '',
          email: '',
          ativo: true,
          created_at: '',
          updated_at: '',
        }
      }
    }
    return { user, token, refreshToken, loading: false }
  })

  const saveSession = useCallback((token: string, refreshToken: string, user: UserRead) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('refresh_token', refreshToken)
    localStorage.setItem(STORAGE_USER, JSON.stringify(user))
    setState({ user, token, refreshToken, loading: false })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)
    const { data } = await api.post<LoginResponse>('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    const payload = decodeToken(data.access_token)
    const user: UserRead = {
      id: payload?.sub ?? '',
      nome: email.split('@')[0],
      email,
      ativo: true,
      created_at: '',
      updated_at: '',
    }
    saveSession(data.access_token, data.refresh_token, user)
  }, [saveSession])

  const register = useCallback(async (name: string, email: string, password: string) => {
    const { data } = await api.post<UserRead>('/auth/register', {
      nome: name,
      email,
      senha: password,
    })
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)
    const loginRes = await api.post<LoginResponse>('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    saveSession(loginRes.data.access_token, loginRes.data.refresh_token, data)
  }, [saveSession])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem(STORAGE_USER)
    setState({ user: null, token: null, refreshToken: null, loading: false })
  }, [])

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
