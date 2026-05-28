import { useEffect, useState, useCallback, useRef, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'
import { formatCurrency } from '../../utils/format'
import type { ProductRead, ProductCreate, ProductUpdate } from '../../types/product'

const PAGE_SIZE = 20

export function ProductList() {
  const navigate = useNavigate()
  const [products, setProducts] = useState<ProductRead[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterLowStock, setFilterLowStock] = useState(false)
  const [page, setPage] = useState(0)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<ProductRead | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<ProductRead | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const fetchProducts = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params: Record<string, string | number | boolean> = { limit: PAGE_SIZE, offset: page * PAGE_SIZE }
      if (search) params.nome = search
      if (filterCategory) params.categoria = filterCategory
      if (filterLowStock) params.estoque_baixo = true
      const { data, headers } = await api.get<ProductRead[]>('/products', { params })
      setProducts(data)
      setTotalCount(Number(headers['x-total-count'] || data.length))
    } catch { setError('Erro ao carregar produtos.') }
    finally { setLoading(false) }
  }, [search, filterCategory, filterLowStock, page])

  useEffect(() => { fetchProducts() }, [fetchProducts])

  const handleSearch = (value: string) => {
    setSearch(value)
    setPage(0)
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => fetchProducts(), 300)
  }

  const totalPages = Math.ceil(totalCount / PAGE_SIZE)

  const handleDelete = async () => {
    if (!deleteTarget) return
    setDeleting(true)
    try {
      await api.delete(`/products/${deleteTarget.id}`)
      setProducts((prev) => prev.filter((p) => p.id !== deleteTarget.id))
      setTotalCount((c) => c - 1)
    } catch { setDeleteError('Não foi possível excluir. O produto pode ter movimentações.') }
    finally { setDeleting(false); setDeleteTarget(null) }
  }

  const openNew = () => { setEditing(null); setModalOpen(true) }
  const openEdit = (p: ProductRead) => { setEditing(p); setModalOpen(true) }
  const closeModal = () => { setModalOpen(false); setEditing(null) }

  const categories = [...new Set(products.map((p) => p.categoria).filter(Boolean))]

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Produtos {totalCount > 0 && <span className="text-muted" style={{fontSize:'0.9rem',fontWeight:400}}>({totalCount})</span>}</h1>
        <button className="btn btn-primary" onClick={openNew} type="button">+ Novo Produto</button>
      </div>

      {deleteError && <div className="login-error" style={{ marginBottom: 16 }}>{deleteError}<button className="btn btn-sm btn-ghost" style={{ marginLeft: 8 }} onClick={() => setDeleteError('')} type="button">×</button></div>}
      {error && <div className="login-error" style={{ marginBottom: 16 }}>{error}</div>}

      <div className="search-bar">
        <input type="text" placeholder="Buscar por nome..." value={search} onChange={(e) => handleSearch(e.target.value)} />
        {search && <button className="btn btn-ghost" type="button" onClick={() => { handleSearch(''); setFilterCategory(''); setFilterLowStock(false); setPage(0) }}>Limpar</button>}
      </div>

      <div className="filters-bar">
        <select value={filterCategory} onChange={(e) => { setFilterCategory(e.target.value); setPage(0) }}>
          <option value="">Todas categorias</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <label className="checkbox-label" style={{ fontSize: '0.85rem' }}>
          <input type="checkbox" checked={filterLowStock} onChange={(e) => { setFilterLowStock(e.target.checked); setPage(0) }} />
          Estoque baixo
        </label>
      </div>

      {loading ? (
        <div className="table-loading">Carregando...</div>
      ) : products.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">📦</span>
          <h2>Nenhum produto encontrado</h2>
          <button className="btn btn-primary" onClick={openNew} type="button">+ Novo Produto</button>
        </div>
      ) : (
        <>
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
                          <div style={{ width: 40, height: 40, borderRadius: 6, background: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, color: 'var(--text-muted)' }}>📦</div>
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
                        <button className="btn btn-sm btn-danger" onClick={() => setDeleteTarget(p)} type="button">Excluir</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button className="btn btn-sm btn-outline" disabled={page === 0} onClick={() => setPage(p => p - 1)} type="button">← Anterior</button>
              <span className="pagination-info">Página {page + 1} de {totalPages} ({totalCount} registros)</span>
              <button className="btn btn-sm btn-outline" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)} type="button">Próxima →</button>
            </div>
          )}
        </>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Excluir produto"
        message={`Tem certeza que deseja excluir "${deleteTarget?.nome}"?`}
        confirmLabel="Excluir"
        loading={deleting}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />

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
  initial, onSaved, onCancel,
}: {
  initial: ProductRead | null
  onSaved: () => void
  onCancel: () => void
}) {
  const [form, setForm] = useState({
    nome: initial?.nome ?? '',
    sku: initial?.sku ?? '',
    descricao: initial?.descricao ?? '',
    categoria: initial?.categoria ?? '',
    ean: initial?.ean ?? '',
    preco_custo: initial?.preco_custo ?? '',
    preco_venda: initial?.preco_venda ?? '',
    quantidade_estoque: initial?.quantidade_estoque ?? 0,
    estoque_minimo: initial?.estoque_minimo ?? 0,
    ativo: initial?.ativo ?? true,
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const set = (field: string, value: string | number | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      const payload: Record<string, unknown> = {
        nome: form.nome, sku: form.sku, categoria: form.categoria,
        preco_custo: form.preco_custo, preco_venda: form.preco_venda,
        quantidade_estoque: form.quantidade_estoque, estoque_minimo: form.estoque_minimo,
        ativo: form.ativo,
      }
      payload.descricao = form.descricao || null
      payload.ean = form.ean || null

      if (initial) {
        await api.patch(`/products/${initial.id}`, payload as ProductUpdate)
      } else {
        await api.post('/products', payload as unknown as ProductCreate)
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
          <label htmlFor="f_ean">EAN</label>
          <input id="f_ean" value={form.ean} onChange={(e) => set('ean', e.target.value)} maxLength={13} placeholder="Código de barras" />
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
      <label className="checkbox-label"><input type="checkbox" checked={form.ativo} onChange={(e) => set('ativo', e.target.checked)} /> Produto ativo</label>
      <div className="form-actions" style={{ marginTop: 20 }}>
        <button className="btn btn-outline" type="button" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? <span className="btn-loading"><span className="btn-spinner" /> Salvando...</span> : initial ? 'Atualizar' : 'Criar'}
        </button>
      </div>
    </form>
  )
}
