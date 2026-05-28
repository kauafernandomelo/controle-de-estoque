import { useEffect, useState, useCallback, type FormEvent } from 'react'
import api from '../../api/client'
import { formatDate, translateMovementType } from '../../utils/format'
import type { MovementRead, MovementType } from '../../types/movement'

const typeColors: Record<MovementType, string> = {
  ENTRADA: 'badge-success',
  SAIDA: 'badge-danger',
  AJUSTE: 'badge-warning',
}

export function MovementList() {
  const [movements, setMovements] = useState<MovementRead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [successMsg, setSuccessMsg] = useState('')

  const fetchMovements = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get<MovementRead[]>('/movements')
      setMovements(data)
    } catch {
      setError('Erro ao carregar movimentações.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchMovements() }, [fetchMovements])

  const handleSaved = () => {
    setModalOpen(false)
    setSuccessMsg('Movimentação registrada com sucesso!')
    fetchMovements()
    setTimeout(() => setSuccessMsg(''), 3000)
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Movimentações</h1>
        <button className="btn btn-primary" onClick={() => setModalOpen(true)} type="button">
          + Nova Movimentação
        </button>
      </div>

      {successMsg && <div className="login-error" style={{ background: '#f0fdf4', color: '#166534', borderColor: '#bbf7d0', marginBottom: 16 }}>{successMsg}</div>}
      {error && <div className="login-error" style={{ marginBottom: 16 }}>{error}</div>}

      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Produto</th>
              <th>Quantidade</th>
              <th>Observação</th>
              <th>Data</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="table-loading">Carregando...</td></tr>
            ) : movements.length === 0 ? (
              <tr><td colSpan={5} className="table-empty">
                <div className="empty-state" style={{ margin: '20px auto', padding: 20 }}>
                  <span className="empty-icon" style={{ fontSize: '2rem' }}>📋</span>
                  <h2>Nenhuma movimentação</h2>
                  <p>Registre entrada, saída ou ajuste de estoque.</p>
                  <button className="btn btn-primary" onClick={() => setModalOpen(true)} type="button">
                    + Nova Movimentação
                  </button>
                </div>
              </td></tr>
            ) : (
              movements.map((m) => (
                <tr key={m.id}>
                  <td><span className={`badge ${typeColors[m.tipo_movimentacao]}`}>{translateMovementType(m.tipo_movimentacao)}</span></td>
                  <td><code>{m.produto_id.slice(0, 8)}...</code></td>
                  <td>{m.quantidade}</td>
                  <td className="text-muted">{m.observacao || '---'}</td>
                  <td>{formatDate(m.created_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Nova Movimentação</h2>
              <button className="modal-close" onClick={() => setModalOpen(false)} type="button">×</button>
            </div>
            <div className="modal-body">
              <MovementForm onSaved={handleSaved} onCancel={() => setModalOpen(false)} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function MovementForm({
  onSaved,
  onCancel,
}: {
  onSaved: () => void
  onCancel: () => void
}) {
  const [products, setProducts] = useState<{ id: string; nome: string; sku: string }[]>([])
  const [form, setForm] = useState({
    produto_id: '',
    tipo_movimentacao: 'ENTRADA' as MovementType,
    quantidade: 1,
    observacao: '',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/products').then(({ data }) => setProducts(data)).catch(() => {})
  }, [])

  const set = (field: string, value: string | number) =>
    setForm((prev) => ({ ...prev, [field]: value }))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!form.produto_id) { setError('Selecione um produto.'); return }
    setSaving(true)
    setError('')
    try {
      await api.post('/movements', form)
      onSaved()
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Erro ao registrar movimentação.'
          : 'Erro ao registrar movimentação.'
      setError(msg)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      {error && <div className="login-error">{error}</div>}

      <div className="form-group">
        <label htmlFor="produto">Produto *</label>
        <select id="produto" value={form.produto_id} onChange={(e) => set('produto_id', e.target.value)} required>
          <option value="">Selecione um produto...</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>{p.nome} ({p.sku})</option>
          ))}
        </select>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="tipo">Tipo *</label>
          <select id="tipo" value={form.tipo_movimentacao} onChange={(e) => set('tipo_movimentacao', e.target.value)} required>
            <option value="ENTRADA">📥 Entrada</option>
            <option value="SAIDA">📤 Saída</option>
            <option value="AJUSTE">⚙️ Ajuste</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="quantidade">Quantidade *</label>
          <input id="quantidade" type="number" min="1" value={form.quantidade} onChange={(e) => set('quantidade', Number(e.target.value))} required />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="observacao">Observação</label>
        <textarea id="observacao" value={form.observacao} onChange={(e) => set('observacao', e.target.value)} rows={3} placeholder="Motivo da movimentação (opcional)" />
      </div>

      <div className="form-actions">
        <button className="btn btn-outline" type="button" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? (
            <span className="btn-loading">
              <span className="btn-spinner" />
              Registrando...
            </span>
          ) : 'Registrar'}
        </button>
      </div>
    </form>
  )
}
