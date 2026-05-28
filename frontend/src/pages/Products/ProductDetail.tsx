import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../api/client'
import { formatCurrency } from '../../utils/format'
import type { ProductRead } from '../../types/product'

export function ProductDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [product, setProduct] = useState<ProductRead | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    setLoading(true)
    api.get<ProductRead>(`/products/${id}`)
      .then(({ data }) => setProduct(data))
      .catch(() => setError('Produto não encontrado.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="page"><div className="table-loading">Carregando...</div></div>
  if (error || !product) return (
    <div className="page">
      <div className="empty-state">
        <span className="empty-icon" style={{ fontSize: '3rem' }}>🔍</span>
        <h2>{error || 'Produto não encontrado'}</h2>
        <button className="btn btn-primary" onClick={() => navigate('/products')} type="button">← Voltar para Produtos</button>
      </div>
    </div>
  )

  return (
    <div className="page">
      <button className="btn btn-ghost" style={{ marginBottom: 16 }} onClick={() => navigate('/products')} type="button">
        ← Voltar para Produtos
      </button>

      <div className="product-detail">
        <div className="product-detail-image">
          <div style={{ width: 64, height: 64, fontSize: 64, color: 'var(--text-muted)', opacity: 0.4 }}>📦</div>
        </div>

        <div className="product-info">
          <h1 className="product-name">{product.nome}</h1>
          <p className="product-sku">SKU: <code>{product.sku}</code> {product.ean && <>| EAN: <code>{product.ean}</code></>}</p>

          <div className="product-meta">
            <span className={`badge ${product.ativo ? 'badge-success' : 'badge-secondary'}`}>
              {product.ativo ? 'Ativo' : 'Inativo'}
            </span>
            <span className="badge badge-secondary">{product.categoria}</span>
          </div>

          <div className="product-prices">
            <div className="product-price-row">
              <span className="product-price-label">Preço de Custo</span>
              <span className="product-price-value">{formatCurrency(product.preco_custo)}</span>
            </div>
            <div className="product-price-row">
              <span className="product-price-label">Preço de Venda</span>
              <span className="product-price-value product-price-sale">{formatCurrency(product.preco_venda)}</span>
            </div>
          </div>

          <div className="product-stock-section">
            <div className="product-stock-info">
              <span className="product-stock-label">Estoque Atual</span>
              <span className={`product-stock-value ${product.quantidade_estoque <= product.estoque_minimo ? 'text-warning' : ''}`}>
                {product.quantidade_estoque} unidades
              </span>
            </div>
            <div className="product-stock-info">
              <span className="product-stock-label">Estoque Mínimo</span>
              <span className="product-stock-value">{product.estoque_minimo} unidades</span>
            </div>
          </div>

          {product.descricao && (
            <div className="product-description">
              <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 6 }}>Descrição</h3>
              <p>{product.descricao}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
