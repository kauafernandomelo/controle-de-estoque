export interface ProductCreate {
  nome: string
  sku: string
  descricao?: string | null
  categoria: string
  categoria_id?: string | null
  marca_id?: string | null
  fornecedor_id?: string | null
  ean?: string | null
  preco_custo: string
  preco_venda: string
  quantidade_estoque: number
  estoque_minimo: number
  peso_g?: number | null
  altura_cm?: string | null
  largura_cm?: string | null
  profundidade_cm?: string | null
  destaque?: boolean
  ativo?: boolean
  tags?: string[] | null
}

export interface ProductUpdate {
  nome?: string
  sku?: string
  descricao?: string | null
  categoria?: string
  categoria_id?: string | null
  marca_id?: string | null
  fornecedor_id?: string | null
  ean?: string | null
  preco_custo?: string
  preco_venda?: string
  quantidade_estoque?: number
  estoque_minimo?: number
  peso_g?: number | null
  altura_cm?: string | null
  largura_cm?: string | null
  profundidade_cm?: string | null
  destaque?: boolean
  ativo?: boolean
  tags?: string[] | null
}

export interface ProductImageRead {
  id: string
  product_id: string
  url: string
  alt: string | null
  is_primary: boolean
  sort_order: number
  created_at: string
}

export interface ProductRead {
  id: string
  nome: string
  sku: string
  descricao: string | null
  categoria: string
  categoria_id: string | null
  marca_id: string | null
  fornecedor_id: string | null
  ean: string | null
  preco_custo: string
  preco_venda: string
  quantidade_estoque: number
  estoque_minimo: number
  peso_g: number | null
  altura_cm: string | null
  largura_cm: string | null
  profundidade_cm: string | null
  destaque: boolean
  ativo: boolean
  rating_avg: string
  rating_count: number
  images: ProductImageRead[]
  tag_ids: string[]
  created_at: string
  updated_at: string
}
