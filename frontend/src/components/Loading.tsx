export function Loading({ text = 'Carregando...' }: { text?: string }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', padding: '64px 24px', gap: 16,
    }}>
      <div className="spinner" />
      <span style={{ color: '#64748b', fontSize: '0.95rem' }}>{text}</span>
      <style>{`
        .spinner {
          width: 36px; height: 36px;
          border: 3px solid #e2e8f0;
          border-top-color: #2563eb;
          border-radius: 50%;
          animation: spin 0.7s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}

export function PageLoading({ text = 'Carregando...' }: { text?: string }) {
  return (
    <div className="page">
      <Loading text={text} />
    </div>
  )
}
