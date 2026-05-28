export interface SupplierRead {
  id: string
  nome: string
  cnpj: string | null
  nome_contato: string | null
  email: string | null
  telefone: string | null
  endereco: string | null
  observacoes: string | null
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface SupplierCreate {
  nome: string
  cnpj?: string | null
  nome_contato?: string | null
  email?: string | null
  telefone?: string | null
  endereco?: string | null
  observacoes?: string | null
  ativo?: boolean
}
