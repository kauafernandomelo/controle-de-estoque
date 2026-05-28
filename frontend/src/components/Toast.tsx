import { createContext, useCallback, useContext, useState } from 'react'

type ToastType = 'success' | 'error' | 'info'

interface Toast {
  id: number
  type: ToastType
  message: string
}

interface ToastContextType {
  toast: (message: string, type?: ToastType) => void
}

const ToastContext = createContext<ToastContextType>({ toast: () => {} })

export const useToast = () => useContext(ToastContext)

let nextId = 0

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = ++nextId
    setToasts((prev) => [...prev, { id, type, message }])
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500)
  }, [])

  return (
    <ToastContext.Provider value={{ toast: addToast }}>
      {children}
      <div style={{
        position: 'fixed', top: 16, right: 16, zIndex: 9999,
        display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 400,
      }}>
        {toasts.map((t) => (
          <div
            key={t.id}
            style={{
              padding: '12px 16px', borderRadius: 8,
              background: t.type === 'success' ? '#16a34a'
                : t.type === 'error' ? '#dc2626' : '#2563eb',
              color: '#fff', fontSize: '0.9rem',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              animation: 'slideIn 0.25s ease-out',
            }}
          >
            {t.message}
          </div>
        ))}
      </div>
      <style>{`
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
      `}</style>
    </ToastContext.Provider>
  )
}
