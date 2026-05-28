import { useEffect, useState, useCallback, type FormEvent } from 'react'
import api from '../../api/client'
import type { BrandRead, BrandCreate } from '../../types/brand'

export function BrandList() {
  const [items, setItems] = useState<BrandRead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await api.get<BrandRead[]>('/brands')
      setItems(data)
    } catch { setError('Erro ao carregar marcas.') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Marcas</h1>
        <button className="btn btn-primary" onClick={() => setModalOpen(true)} type="button">+ Nova Marca</button>
      </div>
      {error && <div className="login-error" style={{ marginBottom: 16 }}>{error}</div>}
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Slug</th>
              <th>Descrição</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={4} className="table-loading">Carregando...</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={4} className="table-empty">Nenhuma marca cadastrada.</td></tr>
            ) : (
              items.map((b) => (
                <tr key={b.id}>
                  <td><strong>{b.nome}</strong></td>
                  <td><code>{b.slug}</code></td>
                  <td className="text-muted">{b.descricao || '---'}</td>
                  <td><span className={`badge ${b.ativo ? 'badge-success' : 'badge-secondary'}`}>{b.ativo ? 'Ativa' : 'Inativa'}</span></td>
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
              <h2>Nova Marca</h2>
              <button className="modal-close" onClick={() => setModalOpen(false)} type="button">×</button>
            </div>
            <div className="modal-body">
              <BrandForm onSaved={() => { setModalOpen(false); fetch() }} onCancel={() => setModalOpen(false)} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function BrandForm({ onSaved, onCancel }: { onSaved: () => void; onCancel: () => void }) {
  const [form, setForm] = useState({ nome: '', slug: '', descricao: '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      await api.post('/brands', { ...form, slug: form.slug || form.nome.toLowerCase().replace(/\s+/g, '-') } as BrandCreate)
      onSaved()
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Erro ao salvar.'
        : 'Erro ao salvar.'
      setError(msg)
    } finally { setSaving(false) }
  }

  const set = (f: string, v: string) => setForm(p => ({ ...p, [f]: v }))

  return (
    <form onSubmit={handleSubmit} className="form">
      {error && <div className="login-error">{error}</div>}
      <div className="form-group">
        <label>Nome *</label>
        <input value={form.nome} onChange={e => set('nome', e.target.value)} required minLength={2} />
      </div>
      <div className="form-group">
        <label>Slug</label>
        <input value={form.slug} onChange={e => set('slug', e.target.value)} placeholder="Deixe em branco para gerar automaticamente" />
      </div>
      <div className="form-group">
        <label>Descrição</label>
        <textarea value={form.descricao} onChange={e => set('descricao', e.target.value)} rows={3} />
      </div>
      <div className="form-actions">
        <button className="btn btn-outline" type="button" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? <span className="btn-loading"><span className="btn-spinner" /> Salvando...</span> : 'Criar'}
        </button>
      </div>
    </form>
  )
}
