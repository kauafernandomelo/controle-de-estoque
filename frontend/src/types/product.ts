export interface ProductCreate {
  nome: string
  sku: string
  descricao?: string | null
  categoria: string
  ean?: string | null
  preco_custo: string
  preco_venda: string
  quantidade_estoque: number
  estoque_minimo: number
  ativo?: boolean
}

export interface ProductUpdate {
  nome?: string
  sku?: string
  descricao?: string | null
  categoria?: string
  ean?: string | null
  preco_custo?: string
  preco_venda?: string
  quantidade_estoque?: number
  estoque_minimo?: number
  ativo?: boolean
}

export interface ProductRead {
  id: string
  nome: string
  sku: string
  descricao: string | null
  categoria: string
  ean: string | null
  preco_custo: string
  preco_venda: string
  quantidade_estoque: number
  estoque_minimo: number
  ativo: boolean
  created_at: string
  updated_at: string
}
