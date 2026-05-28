export interface CartItemCreate {
  produto_id: string
  quantidade: number
}

export interface CartItemUpdate {
  quantidade: number
}

export interface CartItemRead {
  id: string
  product_id: string
  product_name: string | null
  product_sku: string | null
  product_image: string | null
  unit_price: string | null
  quantity: number
  total: string | null
  created_at: string
}

export interface CartRead {
  id: string
  user_id: string
  items: CartItemRead[]
  total_items: number
  total_value: string
  created_at: string
  updated_at: string
}
