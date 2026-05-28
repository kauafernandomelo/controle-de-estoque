export type MovementType = 'ENTRADA' | 'SAIDA' | 'AJUSTE'

export interface MovementCreate {
  produto_id: string
  tipo_movimentacao: MovementType
  quantidade: number
  observacao?: string | null
}

export interface MovementRead {
  id: string
  produto_id: string
  usuario_id: string
  tipo_movimentacao: MovementType
  quantidade: number
  observacao: string | null
  created_at: string
}
