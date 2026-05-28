export interface ProductCreate {
  nome: string
  sku: string
  descricao?: string | null
  categoria: string
  preco_custo: string
  preco_venda: string
  quantidade_estoque: number
  estoque_minimo: number
  ativo: boolean
}

export interface ProductUpdate {
  nome?: string
  sku?: string
  descricao?: string | null
  categoria?: string
  preco_custo?: string
  preco_venda?: string
  quantidade_estoque?: number
  estoque_minimo?: number
  ativo?: boolean
}

export interface ProductRead extends ProductCreate {
  id: string
  created_at: string
  updated_at: string
}
