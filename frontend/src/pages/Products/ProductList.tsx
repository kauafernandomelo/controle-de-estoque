import { useEffect, useState, useCallback, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'
import { useAuth } from '../../hooks/useAuth'
import { formatCurrency } from '../../utils/format'
import type { ProductRead, ProductCreate, ProductUpdate } from '../../types/product'
import type { BrandRead } from '../../types/brand'

export function ProductList() {
  const { isAdmin } = useAuth()
  const navigate = useNavigate()
  const [products, setProducts] = useState<ProductRead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [view, setView] = useState<'grid' | 'list'>('grid')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterLowStock, setFilterLowStock] = useState(false)
  const [filterFeatured, setFilterFeatured] = useState(false)
  const [filterBrand, setFilterBrand] = useState('')
  const [brands, setBrands] = useState<BrandRead[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<ProductRead | null>(null)
  const [deleteError, setDeleteError] = useState('')

  const fetchProducts = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params: Record<string, string | boolean> = {}
      if (search) params.nome = search
      if (filterCategory) params.categoria = filterCategory
      if (filterLowStock) params.estoque_baixo = true
      if (filterFeatured) params.destaque = true
      if (filterBrand) params.marca_id = filterBrand
      const { data } = await api.get<ProductRead[]>('/products', { params })
      setProducts(data)
    } catch { setError('Erro ao carregar produtos.') }
    finally { setLoading(false) }
  }, [search, filterCategory, filterLowStock, filterFeatured, filterBrand])

  useEffect(() => { fetchProducts() }, [fetchProducts])

  useEffect(() => {
    api.get<BrandRead[]>('/brands', { params: { active_only: true } })
      .then(({ data }) => setBrands(data)).catch(() => {})
  }, [])

  const handleSearch = (e: FormEvent) => { e.preventDefault(); fetchProducts() }

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/products/${id}`)
      setProducts((prev) => prev.filter((p) => p.id !== id))
    } catch { setDeleteError('Não foi possível excluir. O produto pode ter movimentações.') }
  }

  const openNew = () => { setEditing(null); setModalOpen(true) }
  const openEdit = (p: ProductRead) => { setEditing(p); setModalOpen(true) }
  const closeModal = () => { setModalOpen(false); setEditing(null) }

  const categories = [...new Set(products.map((p) => p.categoria).filter(Boolean))]

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Produtos ({products.length})</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <div className="view-toggle">
            <button className={view === 'grid' ? 'active' : ''} onClick={() => setView('grid')} type="button">📇 Grid</button>
            <button className={view === 'list' ? 'active' : ''} onClick={() => setView('list')} type="button">📋 Lista</button>
          </div>
          <button className="btn btn-primary" onClick={openNew} type="button">+ Novo Produto</button>
        </div>
      </div>

      {deleteError && <div className="login-error" style={{ marginBottom: 16 }}>{deleteError}<button className="btn btn-sm btn-ghost" style={{ marginLeft: 8, color: '#991b1b' }} onClick={() => setDeleteError('')} type="button">×</button></div>}
      {error && <div className="login-error" style={{ marginBottom: 16 }}>{error}</div>}

      <form className="search-bar" onSubmit={handleSearch}>
        <input type="text" placeholder="Buscar por nome..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <button className="btn btn-outline" type="submit">Buscar</button>
        {search && <button className="btn btn-ghost" type="button" onClick={() => { setSearch(''); setFilterCategory(''); setFilterLowStock(false); setFilterFeatured(false); setFilterBrand('') }}>Limpar</button>}
      </form>

      <div className="filters-bar">
        <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}>
          <option value="">Todas categorias</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={filterBrand} onChange={(e) => setFilterBrand(e.target.value)}>
          <option value="">Todas marcas</option>
          {brands.map((b) => <option key={b.id} value={b.id}>{b.nome}</option>)}
        </select>
        <label className="checkbox-label" style={{ fontSize: '0.85rem' }}>
          <input type="checkbox" checked={filterLowStock} onChange={(e) => setFilterLowStock(e.target.checked)} />
          Estoque baixo
        </label>
        <label className="checkbox-label" style={{ fontSize: '0.85rem' }}>
          <input type="checkbox" checked={filterFeatured} onChange={(e) => setFilterFeatured(e.target.checked)} />
          Destaque
        </label>
      </div>

      {loading ? (
        view === 'grid' ? (
          <div className="product-grid">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="skeleton-card" style={{ height: 320 }} />
            ))}
          </div>
        ) : (
          <div className="table-loading">Carregando...</div>
        )
      ) : products.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">📦</span>
          <h2>Nenhum produto encontrado</h2>
          <button className="btn btn-primary" onClick={openNew} type="button">+ Novo Produto</button>
        </div>
      ) : view === 'grid' ? (
        <div className="product-grid">
          {products.map((p) => (
            <div key={p.id} className="product-card" onClick={() => navigate(`/products/${p.id}`)}>
              <div className="product-card-image">
                {p.images && p.images[0] ? (
                  <img src={p.images[0].url} alt={p.nome} />
                ) : (
                  <span className="no-image">📦</span>
                )}
                {p.destaque && <span className="badge badge-warning product-card-featured">Destaque</span>}
              </div>
              <div className="product-card-body">
                <div className="product-card-name">{p.nome}</div>
                <div className="product-card-sku">{p.sku}</div>
                {p.rating_count > 0 && (
                  <div className="product-card-rating">
                    {'★'.repeat(Math.round(Number(p.rating_avg)))}{'☆'.repeat(5 - Math.round(Number(p.rating_avg)))}
                    <span className="text-muted" style={{ fontSize: '0.78rem' }}> ({p.rating_count})</span>
                  </div>
                )}
                <div className="product-card-price">{formatCurrency(p.preco_venda)}</div>
                <div className="product-card-stock">
                  {p.quantidade_estoque <= p.estoque_minimo ? (
                    <span className="text-warning">⚠️ {p.quantidade_estoque} em estoque</span>
                  ) : (
                    <span className="text-muted">{p.quantidade_estoque} em estoque</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr>
                <th>Produto</th>
                <th>SKU</th>
                <th>Categoria</th>
                <th>Preço</th>
                <th>Estoque</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }} onClick={() => navigate(`/products/${p.id}`)}>
                      <div style={{ width: 40, height: 40, borderRadius: 6, background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>
                        {p.images?.[0] ? <img src={p.images[0].url} alt="" style={{ width: 40, height: 40, borderRadius: 6, objectFit: 'cover' }} /> : '📦'}
                      </div>
                      <span style={{ fontWeight: 500 }}>{p.nome}</span>
                    </div>
                  </td>
                  <td><code>{p.sku}</code></td>
                  <td><span className="badge badge-secondary">{p.categoria}</span></td>
                  <td>{formatCurrency(p.preco_venda)}</td>
                  <td><span className={p.quantidade_estoque <= p.estoque_minimo ? 'text-warning' : ''}>{p.quantidade_estoque}</span></td>
                  <td><span className={`badge ${p.ativo ? 'badge-success' : 'badge-secondary'}`}>{p.ativo ? 'Ativo' : 'Inativo'}</span></td>
                  <td>
                    <div className="actions" onClick={(e) => e.stopPropagation()}>
                      <button className="btn btn-sm btn-outline" onClick={() => openEdit(p)} type="button">Editar</button>
                      {isAdmin && <button className="btn btn-sm btn-danger" onClick={() => handleDelete(p.id)} type="button">Excluir</button>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editing ? 'Editar Produto' : 'Novo Produto'}</h2>
              <button className="modal-close" onClick={closeModal} type="button">×</button>
            </div>
            <div className="modal-body">
              <ProductForm
                key={editing?.id ?? 'new'}
                initial={editing}
                brands={brands}
                onSaved={() => { closeModal(); fetchProducts() }}
                onCancel={closeModal}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ProductForm({
  initial, brands, onSaved, onCancel,
}: {
  initial: ProductRead | null
  brands: BrandRead[]
  onSaved: () => void
  onCancel: () => void
}) {
  const [form, setForm] = useState({
    nome: initial?.nome ?? '',
    sku: initial?.sku ?? '',
    descricao: initial?.descricao ?? '',
    categoria: initial?.categoria ?? '',
    marca_id: initial?.marca_id ?? '',
    ean: initial?.ean ?? '',
    preco_custo: initial?.preco_custo ?? '',
    preco_venda: initial?.preco_venda ?? '',
    quantidade_estoque: initial?.quantidade_estoque ?? 0,
    estoque_minimo: initial?.estoque_minimo ?? 0,
    peso_g: initial?.peso_g ?? '',
    destaque: initial?.destaque ?? false,
    ativo: initial?.ativo ?? true,
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const existingImages = initial?.images ?? []
  const [deletedImageIds, setDeletedImageIds] = useState<string[]>([])
  const [newFiles, setNewFiles] = useState<File[]>([])

  const set = (field: string, value: string | number | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }))

  const visibleImages = existingImages.filter((img) => !deletedImageIds.includes(img.id))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      const payload: Record<string, unknown> = {
        nome: form.nome, sku: form.sku, categoria: form.categoria,
        preco_custo: form.preco_custo, preco_venda: form.preco_venda,
        quantidade_estoque: form.quantidade_estoque, estoque_minimo: form.estoque_minimo,
        ativo: form.ativo, destaque: form.destaque,
      }
      if (form.descricao) payload.descricao = form.descricao
      if (form.marca_id) payload.marca_id = form.marca_id
      if (form.ean) payload.ean = form.ean
      if (form.peso_g) payload.peso_g = Number(form.peso_g)

      let productId: string
      if (initial) {
        await api.patch(`/products/${initial.id}`, payload as ProductUpdate)
        productId = initial.id
      } else {
        const { data } = await api.post('/products', payload as unknown as ProductCreate)
        productId = data.id
      }

      for (const imgId of deletedImageIds) {
        await api.delete(`/products/${productId}/images/${imgId}`).catch(() => {})
      }

      for (const file of newFiles) {
        const fd = new FormData()
        fd.append('file', file)
        await api.post(`/products/${productId}/images`, fd).catch(() => {})
      }

      onSaved()
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Erro ao salvar.'
        : 'Erro ao salvar.'
      setError(msg)
    } finally { setSaving(false) }
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      {error && <div className="login-error">{error}</div>}
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="f_nome">Nome *</label>
          <input id="f_nome" value={form.nome} onChange={(e) => set('nome', e.target.value)} required minLength={2} />
        </div>
        <div className="form-group">
          <label htmlFor="f_sku">SKU *</label>
          <input id="f_sku" value={form.sku} onChange={(e) => set('sku', e.target.value)} required minLength={2} />
        </div>
      </div>
      <div className="form-group">
        <label htmlFor="f_desc">Descrição</label>
        <textarea id="f_desc" value={form.descricao} onChange={(e) => set('descricao', e.target.value)} rows={2} />
      </div>
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="f_cat">Categoria *</label>
          <input id="f_cat" value={form.categoria} onChange={(e) => set('categoria', e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="f_marca">Marca</label>
          <select id="f_marca" value={form.marca_id} onChange={(e) => set('marca_id', e.target.value)}>
            <option value="">Selecione...</option>
            {brands.map((b) => <option key={b.id} value={b.id}>{b.nome}</option>)}
          </select>
        </div>
      </div>
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="f_ean">EAN</label>
          <input id="f_ean" value={form.ean} onChange={(e) => set('ean', e.target.value)} maxLength={13} placeholder="Código de barras" />
        </div>
        <div className="form-group">
          <label htmlFor="f_peso">Peso (g)</label>
          <input id="f_peso" type="number" min="0" value={form.peso_g} onChange={(e) => set('peso_g', e.target.value)} />
        </div>
      </div>
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="f_custo">Preço Custo *</label>
          <input id="f_custo" type="number" step="0.01" min="0" value={form.preco_custo} onChange={(e) => set('preco_custo', e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="f_venda">Preço Venda *</label>
          <input id="f_venda" type="number" step="0.01" min="0" value={form.preco_venda} onChange={(e) => set('preco_venda', e.target.value)} required />
        </div>
      </div>
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="f_estq">Estoque *</label>
          <input id="f_estq" type="number" min="0" value={form.quantidade_estoque} onChange={(e) => set('quantidade_estoque', Number(e.target.value))} required />
        </div>
        <div className="form-group">
          <label htmlFor="f_estq_min">Estoque Mínimo *</label>
          <input id="f_estq_min" type="number" min="0" value={form.estoque_minimo} onChange={(e) => set('estoque_minimo', Number(e.target.value))} required />
        </div>
      </div>
      <div className="form-row">
        <label className="checkbox-label"><input type="checkbox" checked={form.ativo} onChange={(e) => set('ativo', e.target.checked)} /> Produto ativo</label>
        <label className="checkbox-label"><input type="checkbox" checked={form.destaque} onChange={(e) => set('destaque', e.target.checked)} /> Produto em destaque</label>
      </div>

      <fieldset className="form-images">
        <legend>Imagens</legend>
        {visibleImages.length > 0 && (
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
            {visibleImages.map((img) => (
              <div key={img.id} style={{ position: 'relative', width: 80, height: 80 }}>
                <img src={img.url} alt={img.alt || ''} style={{ width: 80, height: 80, borderRadius: 6, objectFit: 'cover', border: '1px solid #e2e8f0' }} />
                <button type="button" onClick={() => setDeletedImageIds((prev) => [...prev, img.id])}
                  style={{ position: 'absolute', top: -6, right: -6, width: 20, height: 20, borderRadius: '50%', border: 'none', background: '#dc2626', color: '#fff', fontSize: 12, cursor: 'pointer', lineHeight: '20px', textAlign: 'center', padding: 0 }}
                  title="Remover imagem">×</button>
              </div>
            ))}
          </div>
        )}
        {newFiles.length > 0 && (
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
            {newFiles.map((f, i) => (
              <div key={i} style={{ position: 'relative', width: 80, height: 80 }}>
                <img src={URL.createObjectURL(f)} alt="" style={{ width: 80, height: 80, borderRadius: 6, objectFit: 'cover', border: '1px dashed #94a3b8' }} />
                <button type="button" onClick={() => setNewFiles((prev) => prev.filter((_, j) => j !== i))}
                  style={{ position: 'absolute', top: -6, right: -6, width: 20, height: 20, borderRadius: '50%', border: 'none', background: '#dc2626', color: '#fff', fontSize: 12, cursor: 'pointer', lineHeight: '20px', textAlign: 'center', padding: 0 }}
                  title="Remover">×</button>
              </div>
            ))}
          </div>
        )}
        <label className="btn btn-outline" style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: '0.85rem' }}>
          📷 Adicionar imagem
          <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" style={{ display: 'none' }}
            onChange={(e) => {
              const files = Array.from(e.target.files || [])
              setNewFiles((prev) => [...prev, ...files])
              if (e.target) e.target.value = ''
            }} />
        </label>
        <span style={{ fontSize: '0.78rem', color: '#94a3b8', marginLeft: 8 }}>JPG, PNG, WEBP ou GIF</span>
      </fieldset>

      <div className="form-actions" style={{ marginTop: 20 }}>
        <button className="btn btn-outline" type="button" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? <span className="btn-loading"><span className="btn-spinner" /> Salvando...</span> : initial ? 'Atualizar' : 'Criar'}
        </button>
      </div>
    </form>
  )
}
