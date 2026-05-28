export interface ProductImageRead {
  id: string
  product_id: string
  url: string
  alt: string | null
  principal: boolean
  ordem: number
  created_at: string
}
