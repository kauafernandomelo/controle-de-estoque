export interface UserRead {
  id: string
  nome: string
  email: string
  perfil: 'ADMINISTRADOR' | 'OPERADOR'
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserRegister {
  nome: string
  email: string
  senha: string
}

export interface UserCreate extends UserRegister {
  perfil: 'ADMINISTRADOR' | 'OPERADOR'
}

export interface AuthState {
  user: UserRead | null
  token: string | null
  refreshToken: string | null
  loading: boolean
}
