import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../../api/client'
import { formatCurrency, formatDate } from '../../utils/format'
import type { ProductRead } from '../../types/product'
import type { ReviewRead, ReviewCreate } from '../../types/review'

export function ProductDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [product, setProduct] = useState<ProductRead | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedImage, setSelectedImage] = useState(0)
  const [qty, setQty] = useState(1)
  const [cartMsg, setCartMsg] = useState('')
  const [reviews, setReviews] = useState<ReviewRead[]>([])
  const [reviewForm, setReviewForm] = useState({ avaliacao: 5, titulo: '', comentario: '' })
  const [reviewError, setReviewError] = useState('')

  useEffect(() => {
    if (!id) return
    setLoading(true)
    api.get<ProductRead>(`/products/${id}`)
      .then(({ data }) => {
        setProduct(data)
        return api.get<ReviewRead[]>(`/products/${id}/reviews`)
      })
      .then(({ data }) => setReviews(data))
      .catch(() => setError('Erro ao carregar produto.'))
      .finally(() => setLoading(false))
  }, [id])

  const addToCart = async () => {
    if (!product) return
    setCartMsg('')
    try {
      const { data } = await api.post('/cart/items', { produto_id: product.id, quantidade: qty })
      setCartMsg(`${qty}x "${product.nome}" adicionado ao carrinho! (${data.total_items} itens no total)`)
    } catch {
      setCartMsg('Erro ao adicionar ao carrinho.')
    }
  }

  const submitReview = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!product) return
    setReviewError('')
    try {
      const { data } = await api.post<ReviewRead>(`/products/${product.id}/reviews`, reviewForm as ReviewCreate)
      setReviews((prev) => [data, ...prev])
      setReviewForm({ avaliacao: 5, titulo: '', comentario: '' })
    } catch {
      setReviewError('Erro ao enviar avaliação.')
    }
  }

  if (loading) {
    return (
      <div className="page">
        <div className="skeleton-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
          <div className="skeleton-card" style={{ height: 400 }} />
          <div><div className="skeleton-card" style={{ height: 100, marginBottom: 16 }} /><div className="skeleton-card" style={{ height: 100 }} /></div>
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="page">
        <div className="empty-state">
          <span className="empty-icon">🔍</span>
          <h2>Produto não encontrado</h2>
          <button className="btn btn-primary" onClick={() => navigate('/products')} type="button">Ver todos os produtos</button>
        </div>
      </div>
    )
  }

  const stars = Math.round(Number(product.rating_avg))
  const images = product.images || []

  return (
    <div className="page">
      <button className="btn btn-ghost" onClick={() => navigate('/products')} style={{ marginBottom: 16 }} type="button">← Voltar</button>

      {error && <div className="login-error" style={{ marginBottom: 16 }}>{error}</div>}
      {cartMsg && <div className="login-error" style={{ background: '#f0fdf4', color: '#166534', borderColor: '#bbf7d0', marginBottom: 16 }}>{cartMsg}</div>}

      <div className="product-detail">
        <div className="product-gallery">
          {images.length > 0 ? (
            <>
              <div className="product-gallery-main">
                <img src={images[selectedImage]?.url} alt={images[selectedImage]?.alt || product.nome} />
              </div>
              {images.length > 1 && (
                <div className="product-gallery-thumbs">
                  {images.map((img, i) => (
                    <button
                      key={img.id}
                      className={`gallery-thumb ${i === selectedImage ? 'active' : ''}`}
                      onClick={() => setSelectedImage(i)}
                      type="button"
                    >
                      <img src={img.url} alt={img.alt || ''} />
                    </button>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="product-gallery-placeholder">
              <span>📷</span>
              <p>Sem imagem</p>
            </div>
          )}
        </div>

        <div className="product-info">
          <h1 className="product-name">{product.nome}</h1>
          {product.destaque && <span className="badge badge-warning" style={{ marginBottom: 8 }}>Destaque</span>}
          <p className="product-sku">SKU: <code>{product.sku}</code></p>

          {product.rating_count > 0 && (
            <div className="product-rating">
              <span>{'★'.repeat(stars)}{'☆'.repeat(5 - stars)}</span>
              <span className="text-muted"> ({product.rating_count} avaliações)</span>
            </div>
          )}

          <div className="product-price">
            <span className="product-price-value">{formatCurrency(product.preco_venda)}</span>
            {product.preco_custo && (
              <span className="product-price-cost">Custo: {formatCurrency(product.preco_custo)}</span>
            )}
          </div>

          <p className="product-description">{product.descricao || 'Sem descrição.'}</p>

          <div className="product-meta">
            <div className="meta-item"><span className="meta-label">Categoria</span><span>{product.categoria}</span></div>
            <div className="meta-item"><span className="meta-label">Estoque</span><span className={product.quantidade_estoque <= product.estoque_minimo ? 'text-warning' : ''}>{product.quantidade_estoque} un.</span></div>
            <div className="meta-item"><span className="meta-label">EAN</span><span>{product.ean || '---'}</span></div>
            {product.peso_g && <div className="meta-item"><span className="meta-label">Peso</span><span>{product.peso_g}g</span></div>}
          </div>

          {product.ativo && (
            <div className="product-cart-actions">
              <div className="qty-selector">
                <button className="btn btn-sm btn-outline" onClick={() => setQty(Math.max(1, qty - 1))} type="button">−</button>
                <span className="qty-value">{qty}</span>
                <button className="btn btn-sm btn-outline" onClick={() => setQty(qty + 1)} type="button">+</button>
              </div>
              <button className="btn btn-primary btn-lg" onClick={addToCart} type="button">
                🛒 Adicionar ao Carrinho
              </button>
            </div>
          )}
        </div>
      </div>

      <div style={{ marginTop: 40 }}>
        <h3 style={{ marginBottom: 16 }}>Avaliações ({reviews.length})</h3>

        <form onSubmit={submitReview} className="form" style={{ maxWidth: 500, marginBottom: 32 }}>
          {reviewError && <div className="login-error">{reviewError}</div>}
          <div className="form-row">
            <div className="form-group">
              <label>Avaliação</label>
              <select value={reviewForm.avaliacao} onChange={(e) => setReviewForm(p => ({ ...p, avaliacao: Number(e.target.value) }))}>
                {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{'★'.repeat(n)}{'☆'.repeat(5 - n)}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Título</label>
              <input value={reviewForm.titulo} onChange={(e) => setReviewForm(p => ({ ...p, titulo: e.target.value }))} placeholder="Resumo da avaliação" />
            </div>
          </div>
          <div className="form-group">
            <label>Comentário</label>
            <textarea value={reviewForm.comentario} onChange={(e) => setReviewForm(p => ({ ...p, comentario: e.target.value }))} rows={3} />
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">Enviar Avaliação</button>
          </div>
        </form>

        {reviews.length === 0 ? (
          <p className="text-muted">Nenhuma avaliação ainda. Seja o primeiro!</p>
        ) : (
          <div className="reviews-list">
            {reviews.map((r) => (
              <div key={r.id} className="review-card">
                <div className="review-stars">{'★'.repeat(r.avaliacao)}{'☆'.repeat(5 - r.avaliacao)}</div>
                {r.titulo && <strong className="review-title">{r.titulo}</strong>}
                {r.comentario && <p className="review-comment">{r.comentario}</p>}
                <span className="review-date">{formatDate(r.created_at)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
