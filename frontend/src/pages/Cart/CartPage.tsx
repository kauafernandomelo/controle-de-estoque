import { useEffect, useState } from 'react'
import api from '../../api/client'
import { useToast } from '../../components/Toast'
import { PageLoading } from '../../components/Loading'
import { formatCurrency } from '../../utils/format'
import type { CartRead } from '../../types/cart'

export function CartPage() {
  const [cart, setCart] = useState<CartRead | null>(null)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  const fetchCart = async () => {
    setLoading(true)
    try {
      const { data } = await api.get<CartRead>('/cart')
      setCart(data)
    } catch { toast('Erro ao carregar carrinho.', 'error') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchCart() }, [])

  const updateQty = async (itemId: string, quantity: number) => {
    if (quantity < 1) return
    try {
      const { data } = await api.patch<CartRead>(`/cart/items/${itemId}`, { quantidade: quantity })
      setCart(data)
      toast('Quantidade atualizada.', 'success')
    } catch { toast('Erro ao atualizar quantidade.', 'error') }
  }

  const removeItem = async (itemId: string) => {
    try {
      const { data } = await api.delete<CartRead>(`/cart/items/${itemId}`)
      setCart(data)
      toast('Item removido.', 'info')
    } catch { toast('Erro ao remover item.', 'error') }
  }

  const clearCart = async () => {
    try {
      const { data } = await api.delete<CartRead>('/cart')
      setCart(data)
      toast('Carrinho limpo.', 'info')
    } catch { toast('Erro ao limpar carrinho.', 'error') }
  }

  if (loading) return <PageLoading text="Carregando carrinho..." />

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Carrinho</h1>
        {cart && cart.items.length > 0 && (
          <button className="btn btn-danger" onClick={clearCart} type="button">Limpar Carrinho</button>
        )}
      </div>

      {!cart || cart.items.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">🛒</span>
          <h2>Carrinho vazio</h2>
          <p>Adicione produtos a partir da página de produtos.</p>
        </div>
      ) : (
        <>
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Produto</th>
                  <th>SKU</th>
                  <th>Preço Unit.</th>
                  <th>Qtd</th>
                  <th>Total</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {cart.items.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        {item.product_image && (
                          <img src={item.product_image} alt="" style={{ width: 48, height: 48, borderRadius: 6, objectFit: 'cover', background: '#f1f5f9' }} />
                        )}
                        <span>{item.product_name}</span>
                      </div>
                    </td>
                    <td><code>{item.product_sku}</code></td>
                    <td>{item.unit_price ? formatCurrency(item.unit_price) : '---'}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <button className="btn btn-sm btn-outline" onClick={() => updateQty(item.id, item.quantity - 1)} type="button">−</button>
                        <span style={{ minWidth: 24, textAlign: 'center', fontWeight: 600 }}>{item.quantity}</span>
                        <button className="btn btn-sm btn-outline" onClick={() => updateQty(item.id, item.quantity + 1)} type="button">+</button>
                      </div>
                    </td>
                    <td><strong>{item.total ? formatCurrency(item.total) : '---'}</strong></td>
                    <td>
                      <button className="btn btn-sm btn-danger" onClick={() => removeItem(item.id)} type="button">Remover</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 24, gap: 24, alignItems: 'center' }}>
            <span style={{ fontSize: '0.95rem' }}>
              Total: <strong style={{ fontSize: '1.2rem' }}>{formatCurrency(cart.total_value)}</strong>
            </span>
          </div>
        </>
      )}
    </div>
  )
}
