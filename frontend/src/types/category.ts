export interface CategoryRead {
  id: string
  nome: string
  slug: string
  descricao: string | null
  categoria_pai_id: string | null
  ordem: number
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface CategoryCreate {
  nome: string
  slug: string
  descricao?: string | null
  categoria_pai_id?: string | null
  ordem?: number
  ativo?: boolean
}
