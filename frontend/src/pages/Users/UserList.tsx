import { useEffect, useState, useCallback, type FormEvent } from 'react'
import api from '../../api/client'
import { formatDate, translateRole } from '../../utils/format'
import type { UserRead, UserCreate } from '../../types/auth'

export function UserList() {
  const [users, setUsers] = useState<UserRead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)

  const fetchUsers = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get<UserRead[]>('/users')
      setUsers(data)
    } catch {
      setError('Erro ao carregar usuários.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchUsers() }, [fetchUsers])

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Usuários</h1>
        <button className="btn btn-primary" onClick={() => setModalOpen(true)} type="button">
          + Novo Usuário
        </button>
      </div>

      {error && <div className="login-error" style={{ marginBottom: 16 }}>{error}</div>}

      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Perfil</th>
              <th>Status</th>
              <th>Criado em</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="table-loading">Carregando...</td></tr>
            ) : users.length === 0 ? (
              <tr><td colSpan={5} className="table-empty">Nenhum usuário encontrado.</td></tr>
            ) : (
              users.map((u) => (
                <tr key={u.id}>
                  <td>{u.nome}</td>
                  <td>{u.email}</td>
                  <td>
                    <span className={`badge ${u.perfil === 'ADMINISTRADOR' ? 'badge-info' : 'badge-secondary'}`}>
                      {translateRole(u.perfil)}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${u.ativo ? 'badge-success' : 'badge-danger'}`}>
                      {u.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td>{formatDate(u.created_at)}</td>
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
              <h2>Novo Usuário</h2>
              <button className="modal-close" onClick={() => setModalOpen(false)} type="button">×</button>
            </div>
            <div className="modal-body">
              <UserForm
                onSaved={() => { setModalOpen(false); fetchUsers() }}
                onCancel={() => setModalOpen(false)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function UserForm({
  onSaved,
  onCancel,
}: {
  onSaved: () => void
  onCancel: () => void
}) {
  const [form, setForm] = useState({
    nome: '',
    email: '',
    senha: '',
    perfil: 'OPERADOR' as UserCreate['perfil'],
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const set = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.post('/users', form)
      onSaved()
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Erro ao criar usuário.'
          : 'Erro ao criar usuário.'
      setError(msg)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      {error && <div className="login-error">{error}</div>}

      <div className="form-group">
        <label htmlFor="nome">Nome *</label>
        <input id="nome" value={form.nome} onChange={(e) => set('nome', e.target.value)} required minLength={2} />
      </div>
      <div className="form-group">
        <label htmlFor="email">E-mail *</label>
        <input id="email" type="email" value={form.email} onChange={(e) => set('email', e.target.value)} required />
      </div>
      <div className="form-group">
        <label htmlFor="senha">Senha *</label>
        <input id="senha" type="password" value={form.senha} onChange={(e) => set('senha', e.target.value)} required minLength={8} />
      </div>
      <div className="form-group">
        <label htmlFor="perfil">Perfil *</label>
        <select id="perfil" value={form.perfil} onChange={(e) => set('perfil', e.target.value)} required>
          <option value="OPERADOR">Operador</option>
          <option value="ADMINISTRADOR">Administrador</option>
        </select>
      </div>
      <div className="form-actions">
        <button className="btn btn-outline" type="button" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? (
            <span className="btn-loading">
              <span className="btn-spinner" />
              Criando...
            </span>
          ) : 'Criar Usuário'}
        </button>
      </div>
    </form>
  )
}
