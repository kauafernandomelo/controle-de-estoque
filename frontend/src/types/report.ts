export interface LowStockProduct {
  id: string
  nome: string
  sku: string
  quantidade_estoque: number
  estoque_minimo: number
}

export interface MostMovedProduct {
  product_id: string
  nome: string
  sku: string
  quantidade_total: number
}

export interface PeriodMovementTotal {
  tipo_movimentacao: string
  quantidade_total: number
}

export interface InventoryTotals {
  valor_total_estoque: string
  quantidade_total_itens: number
}
