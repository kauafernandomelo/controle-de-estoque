export interface BrandRead {
  id: string
  nome: string
  slug: string
  descricao: string | null
  logo_url: string | null
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface BrandCreate {
  nome: string
  slug: string
  descricao?: string | null
  logo_url?: string | null
  ativo?: boolean
}

export interface BrandUpdate {
  nome?: string
  slug?: string
  descricao?: string | null
  logo_url?: string | null
  ativo?: boolean
}
