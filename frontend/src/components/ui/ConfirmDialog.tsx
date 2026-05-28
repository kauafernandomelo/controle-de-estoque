interface ConfirmDialogProps {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'danger' | 'primary'
  loading?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  open, title, message, confirmLabel = 'Confirmar', cancelLabel = 'Cancelar',
  variant = 'danger', loading = false, onConfirm, onCancel,
}: ConfirmDialogProps) {
  if (!open) return null

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div
        className="modal-content confirm-dialog"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: 400 }}
      >
        <div className="modal-header">
          <h2>{title}</h2>
        </div>
        <div className="modal-body">
          <p style={{ color: 'var(--text-secondary)', margin: '8px 0 20px', lineHeight: 1.5 }}>{message}</p>
          <div className="form-actions">
            <button className="btn btn-outline" type="button" onClick={onCancel} disabled={loading}>
              {cancelLabel}
            </button>
            <button
              className={`btn ${variant === 'danger' ? 'btn-danger' : 'btn-primary'}`}
              type="button"
              onClick={onConfirm}
              disabled={loading}
            >
              {loading ? <span className="btn-loading"><span className="btn-spinner" /> Excluindo...</span> : confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
