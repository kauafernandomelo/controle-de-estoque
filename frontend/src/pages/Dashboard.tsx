import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { formatCurrency, translateMovementType } from '../utils/format'
import type { InventoryTotals, LowStockProduct } from '../types/report'
import type { MovementRead } from '../types/movement'

export function Dashboard() {
  const navigate = useNavigate()
  const [totals, setTotals] = useState<InventoryTotals | null>(null)
  const [lowStock, setLowStock] = useState<LowStockProduct[]>([])
  const [recentMovements, setRecentMovements] = useState<MovementRead[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [totalsRes, lowRes, movRes] = await Promise.all([
          api.get<InventoryTotals>('/reports/inventory-totals'),
          api.get<LowStockProduct[]>('/reports/low-stock'),
          api.get<MovementRead[]>('/movements', { params: { limit: 5 } }),
        ])
        setTotals(totalsRes.data)
        setLowStock(lowRes.data)
        setRecentMovements(movRes.data)
      } catch {
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="page">
        <div className="skeleton-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      </div>
    )
  }

  const hasProducts = totals && (totals.quantidade_total_itens > 0 || parseFloat(totals.valor_total_estoque) > 0)

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
      </div>

      {!hasProducts && (
        <div className="empty-state">
          <span className="empty-icon">📦</span>
          <h2>Seu estoque está vazio</h2>
          <p>Cadastre seu primeiro produto para começar.</p>
          <button className="btn btn-primary" onClick={() => navigate('/products')} type="button">
            + Novo Produto
          </button>
        </div>
      )}

      {hasProducts && (
        <>
          <div className="cards-grid">
            <div className="card">
              <div className="card-label">Valor em Estoque</div>
              <div className="card-value">{formatCurrency(totals!.valor_total_estoque)}</div>
            </div>
            <div className="card">
              <div className="card-label">Total de Itens</div>
              <div className="card-value">{totals!.quantidade_total_itens}</div>
            </div>
            <div className="card">
              <div className="card-label">Estoque Baixo</div>
              <div className={`card-value ${lowStock.length > 0 ? 'text-warning' : ''}`}>
                {lowStock.length}
              </div>
            </div>
            <div className="card">
              <div className="card-label">Movimentações</div>
              <div className="card-value">{recentMovements.length}</div>
            </div>
          </div>

          <div className="dashboard-grid">
            <div className="card">
              <div className="card-header">
                <h3>Estoque Baixo</h3>
                <button className="btn btn-sm btn-ghost" onClick={() => navigate('/reports')} type="button">
                  Ver mais →
                </button>
              </div>
              {lowStock.length === 0 ? (
                <p className="card-empty">Nenhum produto com estoque baixo.</p>
              ) : (
                <div className="table-mini">
                  {lowStock.slice(0, 5).map((p) => (
                    <div key={p.id} className="table-mini-row">
                      <span className="table-mini-name">{p.nome}</span>
                      <span className="table-mini-value text-warning">{p.quantidade_estoque} / {p.estoque_minimo}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="card">
              <div className="card-header">
                <h3>Últimas Movimentações</h3>
                <button className="btn btn-sm btn-ghost" onClick={() => navigate('/movements')} type="button">
                  Ver todas →
                </button>
              </div>
              {recentMovements.length === 0 ? (
                <p className="card-empty">Nenhuma movimentação registrada.</p>
              ) : (
                <div className="table-mini">
                  {recentMovements.map((m) => (
                    <div key={m.id} className="table-mini-row">
                      <span className="table-mini-name">{translateMovementType(m.tipo_movimentacao)}</span>
                      <span className="table-mini-value">{m.quantidade} unidades</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
