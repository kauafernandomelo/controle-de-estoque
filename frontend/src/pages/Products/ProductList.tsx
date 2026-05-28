import { useEffect, useState, useCallback, type FormEvent } from 'react'
import api from '../../api/client'
import { useAuth } from '../../hooks/useAuth'
import { formatCurrency } from '../../utils/format'
import type { ProductRead, ProductCreate, ProductUpdate } from '../../types/product'

export function ProductList() {
  const { isAdmin } = useAuth()
  const [products, setProducts] = useState<ProductRead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<ProductRead | null>(null)
  const [saving, setSaving] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  const fetchProducts = useCallback(async (name?: string) => {
    setLoading(true)
    setError('')
    try {
      const params = name ? { nome: name } : {}
      const { data } = await api.get<ProductRead[]>('/products', { params })
      setProducts(data)
    } catch {
      setError('Erro ao carregar produtos.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchProducts() }, [fetchProducts])

  const handleSearch = (e: FormEvent) => {
    e.preventDefault()
    fetchProducts(search || undefined)
  }

  const handleDelete = async (id: string) => {
    setDeleteError('')
    try {
      await api.delete(`/products/${id}`)
      setProducts((prev) => prev.filter((p) => p.id !== id))
    } catch {
      setDeleteError('Não foi possível excluir. O produto pode ter movimentações vinculadas.')
    }
  }

  const openNew = () => { setEditing(null); setModalOpen(true); setDeleteError('') }
  const openEdit = (p: ProductRead) => { setEditing(p); setModalOpen(true); setDeleteError('') }

  const closeModal = () => { setModalOpen(false); setEditing(null) }

  const handleSaved = () => {
    closeModal()
    fetchProducts()
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Produtos</h1>
        <button className="btn btn-primary" onClick={openNew} type="button">
          + Novo Produto
        </button>
      </div>

      {deleteError && (
        <div className="login-error" style={{ marginBottom: 16 }}>
          {deleteError}
          <button className="btn btn-sm btn-ghost" style={{ marginLeft: 8, color: '#991b1b' }} onClick={() => setDeleteError('')} type="button">×</button>
        </div>
      )}

      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Buscar por nome..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button className="btn btn-outline" type="submit">Buscar</button>
        {search && (
          <button className="btn btn-ghost" type="button" onClick={() => { setSearch(''); fetchProducts() }}>
            Limpar
          </button>
        )}
      </form>

      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>SKU</th>
              <th>Categoria</th>
              <th>Preço Venda</th>
              <th>Estoque</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="table-loading">Carregando...</td></tr>
            ) : products.length === 0 ? (
              <tr><td colSpan={7} className="table-empty">Nenhum produto encontrado.</td></tr>
            ) : (
              products.map((p) => (
                <tr key={p.id}>
                  <td>{p.nome}</td>
                  <td><code>{p.sku}</code></td>
                  <td><span className="badge badge-secondary">{p.categoria}</span></td>
                  <td>{formatCurrency(p.preco_venda)}</td>
                  <td>
                    <span className={p.quantidade_estoque <= p.estoque_minimo ? 'text-warning' : ''}>
                      {p.quantidade_estoque}
                      {p.quantidade_estoque <= p.estoque_minimo && ' ⚠️'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${p.ativo ? 'badge-success' : 'badge-secondary'}`}>
                      {p.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td>
                    <div className="actions">
                      <button className="btn btn-sm btn-outline" onClick={() => openEdit(p)} type="button">
                        Editar
                      </button>
                      {isAdmin && (
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleDelete(p.id)}
                          type="button"
                        >
                          Excluir
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

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
                onSave={handleSaved}
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
  initial,
  onSave,
  onCancel,
}: {
  initial: ProductRead | null
  onSave: () => void
  onCancel: () => void
}) {
  const [form, setForm] = useState({
    nome: initial?.nome ?? '',
    sku: initial?.sku ?? '',
    descricao: initial?.descricao ?? '',
    categoria: initial?.categoria ?? '',
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
    setSaving(true)
    setError('')
    try {
      if (initial) {
        await api.patch(`/products/${initial.id}`, form as ProductUpdate)
      } else {
        await api.post('/products', form as ProductCreate)
      }
      onSave()
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Erro ao salvar.'
          : 'Erro ao salvar.'
      setError(msg)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      {error && <div className="login-error">{error}</div>}

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="nome">Nome *</label>
          <input id="nome" value={form.nome} onChange={(e) => set('nome', e.target.value)} required minLength={2} />
        </div>
        <div className="form-group">
          <label htmlFor="sku">SKU *</label>
          <input id="sku" value={form.sku} onChange={(e) => set('sku', e.target.value)} required minLength={2} />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="descricao">Descrição</label>
        <textarea id="descricao" value={form.descricao} onChange={(e) => set('descricao', e.target.value)} rows={3} />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="categoria">Categoria *</label>
          <input id="categoria" value={form.categoria} onChange={(e) => set('categoria', e.target.value)} required />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="preco_custo">Preço de Custo *</label>
          <input id="preco_custo" type="number" step="0.01" min="0" value={form.preco_custo} onChange={(e) => set('preco_custo', e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="preco_venda">Preço de Venda *</label>
          <input id="preco_venda" type="number" step="0.01" min="0" value={form.preco_venda} onChange={(e) => set('preco_venda', e.target.value)} required />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="quantidade_estoque">Estoque *</label>
          <input id="quantidade_estoque" type="number" min="0" value={form.quantidade_estoque} onChange={(e) => set('quantidade_estoque', Number(e.target.value))} required />
        </div>
        <div className="form-group">
          <label htmlFor="estoque_minimo">Estoque Mínimo *</label>
          <input id="estoque_minimo" type="number" min="0" value={form.estoque_minimo} onChange={(e) => set('estoque_minimo', Number(e.target.value))} required />
        </div>
      </div>

      <div className="form-group">
        <label className="checkbox-label">
          <input type="checkbox" checked={form.ativo} onChange={(e) => set('ativo', e.target.checked)} />
          Produto ativo
        </label>
      </div>

      <div className="form-actions">
        <button className="btn btn-outline" type="button" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? (
            <span className="btn-loading">
              <span className="btn-spinner" />
              Salvando...
            </span>
          ) : initial ? 'Atualizar' : 'Criar'}
        </button>
      </div>
    </form>
  )
}
