import { useEffect, useState, useCallback, type FormEvent } from 'react'
import api from '../../api/client'
import type { SupplierRead, SupplierCreate } from '../../types/supplier'

export function SupplierList() {
  const [items, setItems] = useState<SupplierRead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await api.get<SupplierRead[]>('/suppliers')
      setItems(data)
    } catch { setError('Erro ao carregar fornecedores.') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Fornecedores</h1>
        <button className="btn btn-primary" onClick={() => setModalOpen(true)} type="button">+ Novo Fornecedor</button>
      </div>
      {error && <div className="login-error" style={{ marginBottom: 16 }}>{error}</div>}
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>CNPJ</th>
              <th>Contato</th>
              <th>E-mail</th>
              <th>Telefone</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="table-loading">Carregando...</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={6} className="table-empty">Nenhum fornecedor cadastrado.</td></tr>
            ) : (
              items.map((s) => (
                <tr key={s.id}>
                  <td><strong>{s.nome}</strong></td>
                  <td><code>{s.cnpj || '---'}</code></td>
                  <td>{s.nome_contato || '---'}</td>
                  <td>{s.email || '---'}</td>
                  <td>{s.telefone || '---'}</td>
                  <td><span className={`badge ${s.ativo ? 'badge-success' : 'badge-secondary'}`}>{s.ativo ? 'Ativo' : 'Inativo'}</span></td>
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
              <h2>Novo Fornecedor</h2>
              <button className="modal-close" onClick={() => setModalOpen(false)} type="button">×</button>
            </div>
            <div className="modal-body">
              <SupplierForm onSaved={() => { setModalOpen(false); fetch() }} onCancel={() => setModalOpen(false)} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function SupplierForm({ onSaved, onCancel }: { onSaved: () => void; onCancel: () => void }) {
  const [form, setForm] = useState({ nome: '', cnpj: '', nome_contato: '', email: '', telefone: '', endereco: '', observacoes: '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      await api.post('/suppliers', form as SupplierCreate)
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
      <div className="form-row">
        <div className="form-group">
          <label>CNPJ</label>
          <input value={form.cnpj} onChange={e => set('cnpj', e.target.value)} placeholder="00.000.000/0000-00" />
        </div>
        <div className="form-group">
          <label>Nome para Contato</label>
          <input value={form.nome_contato} onChange={e => set('nome_contato', e.target.value)} />
        </div>
      </div>
      <div className="form-row">
        <div className="form-group">
          <label>E-mail</label>
          <input type="email" value={form.email} onChange={e => set('email', e.target.value)} />
        </div>
        <div className="form-group">
          <label>Telefone</label>
          <input value={form.telefone} onChange={e => set('telefone', e.target.value)} />
        </div>
      </div>
      <div className="form-group">
        <label>Endereço</label>
        <textarea value={form.endereco} onChange={e => set('endereco', e.target.value)} rows={2} />
      </div>
      <div className="form-group">
        <label>Observações</label>
        <textarea value={form.observacoes} onChange={e => set('observacoes', e.target.value)} rows={2} />
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
