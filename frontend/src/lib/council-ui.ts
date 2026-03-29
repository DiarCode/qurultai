import type { AppIconName } from '@/lib/icon-registry'

export function agentIconForRole(role: string): AppIconName {
  const normalized = role.toLowerCase()
  if (normalized.includes('legal') || normalized.includes('прав')) {
    return 'shield'
  }
  if (
    normalized.includes('finance') ||
    normalized.includes('budget') ||
    normalized.includes('econ')
  ) {
    return 'briefcase'
  }
  if (normalized.includes('critic') || normalized.includes('audit')) {
    return 'reference'
  }
  if (normalized.includes('report') || normalized.includes('final')) {
    return 'notebook'
  }
  if (normalized.includes('orchestr')) {
    return 'workflow'
  }
  return 'agent'
}

export const agentStatusLabel: Record<string, string> = {
  active: 'Активен',
  draft: 'Черновик',
  paused: 'На паузе',
}

export const runStatusLabel: Record<string, string> = {
  queued: 'В очереди',
  processing: 'Выполняется',
  completed: 'Завершён',
  failed: 'Ошибка',
}
