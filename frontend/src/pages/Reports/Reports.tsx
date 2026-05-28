import { useEffect, useState } from 'react'
import api from '../../api/client'
import { formatCurrency } from '../../utils/format'
import type { InventoryTotals, LowStockProduct, MostMovedProduct, PeriodMovementTotal } from '../../types/report'

export function Reports() {
  const [totals, setTotals] = useState<InventoryTotals | null>(null)
  const [lowStock, setLowStock] = useState<LowStockProduct[]>([])
  const [mostMoved, setMostMoved] = useState<MostMovedProduct[]>([])
  const [entries, setEntries] = useState<PeriodMovementTotal | null>(null)
  const [exits, setExits] = useState<PeriodMovementTotal | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const now = new Date()
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59)

    const load = async () => {
      try {
        const [totalsRes, lowRes, mostRes, entriesRes, exitsRes] = await Promise.all([
          api.get<InventoryTotals>('/reports/inventory-totals'),
          api.get<LowStockProduct[]>('/reports/low-stock'),
          api.get<MostMovedProduct[]>('/reports/most-moved'),
          api.get<PeriodMovementTotal>('/reports/entries', {
            params: { start_at: startOfMonth.toISOString(), end_at: endOfMonth.toISOString() },
          }),
          api.get<PeriodMovementTotal>('/reports/exits', {
            params: { start_at: startOfMonth.toISOString(), end_at: endOfMonth.toISOString() },
          }),
        ])
        setTotals(totalsRes.data)
        setLowStock(lowRes.data)
        setMostMoved(mostRes.data)
        setEntries(entriesRes.data)
        setExits(exitsRes.data)
      } catch {
        setError('Erro ao carregar relatórios.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="page">
        <h1 className="page-title" style={{ marginBottom: 24 }}>Relatórios</h1>
        <div className="skeleton-grid">
          {[1, 2, 3, 4].map((i) => <div key={i} className="skeleton-card" />)}
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Relatórios</h1>
      </div>

      {error && <div className="login-error" style={{ marginBottom: 16 }}>{error}</div>}

      <div className="cards-grid" style={{ marginBottom: 32 }}>
        <div className="card">
          <div className="card-label">Valor em Estoque</div>
          <div className="card-value">{totals ? formatCurrency(totals.valor_total_estoque) : '---'}</div>
        </div>
        <div className="card">
          <div className="card-label">Total de Itens</div>
          <div className="card-value">{totals?.quantidade_total_itens ?? '---'}</div>
        </div>
        <div className="card">
          <div className="card-label">Entradas (Mês)</div>
          <div className="card-value" style={{ color: 'var(--success)' }}>{entries?.quantidade_total ?? '---'}</div>
        </div>
        <div className="card">
          <div className="card-label">Saídas (Mês)</div>
          <div className="card-value" style={{ color: 'var(--danger)' }}>{exits?.quantidade_total ?? '---'}</div>
        </div>
      </div>

      <div style={{ marginBottom: 32 }}>
        <h3 style={{ marginBottom: 12, fontSize: '0.95rem' }}>Produtos Mais Movimentados</h3>
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr>
                <th>Produto</th>
                <th>SKU</th>
                <th>Total Movimentado</th>
              </tr>
            </thead>
            <tbody>
              {mostMoved.length === 0 ? (
                <tr><td colSpan={3} className="table-empty">Nenhum dado disponível.</td></tr>
              ) : (
                mostMoved.map((p) => (
                  <tr key={p.product_id}>
                    <td>{p.nome}</td>
                    <td><code>{p.sku}</code></td>
                    <td><strong>{p.quantidade_total}</strong></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ marginBottom: 32 }}>
        <h3 style={{ marginBottom: 12, fontSize: '0.95rem' }}>Produtos com Estoque Baixo</h3>
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr>
                <th>Produto</th>
                <th>SKU</th>
                <th>Estoque Atual</th>
                <th>Estoque Mínimo</th>
              </tr>
            </thead>
            <tbody>
              {lowStock.length === 0 ? (
                <tr><td colSpan={4} className="table-empty">Nenhum produto com estoque baixo.</td></tr>
              ) : (
                lowStock.map((p) => (
                  <tr key={p.id}>
                    <td>{p.nome}</td>
                    <td><code>{p.sku}</code></td>
                    <td><span className="badge badge-danger">{p.quantidade_estoque}</span></td>
                    <td>{p.estoque_minimo}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
