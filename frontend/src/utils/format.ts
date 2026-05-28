export function formatCurrency(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(num)
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function formatDateShort(value: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
  }).format(new Date(value))
}

export function translateRole(role: string): string {
  const map: Record<string, string> = {
    ADMINISTRADOR: 'Administrador',
    OPERADOR: 'Operador',
  }
  return map[role] ?? role
}

export function translateMovementType(type: string): string {
  const map: Record<string, string> = {
    ENTRADA: 'Entrada',
    SAIDA: 'Saída',
    AJUSTE: 'Ajuste',
  }
  return map[type] ?? type
}
