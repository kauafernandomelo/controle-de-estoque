export interface ReviewCreate {
  avaliacao: number
  titulo?: string | null
  comentario?: string | null
}

export interface ReviewRead {
  id: string
  product_id: string
  user_id: string
  avaliacao: number
  titulo: string | null
  comentario: string | null
  active: boolean
  created_at: string
  updated_at: string
}
