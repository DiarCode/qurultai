import type { LandingNode } from '@/types/council'

export const landingNodes: LandingNode[] = [
  {
    id: 'state',
    label: 'Государство',
    description: 'Регуляторные рамки и общественный интерес',
    icon: 'building',
  },
  {
    id: 'business',
    label: 'Бизнес',
    description: 'Экономические последствия и операционная устойчивость',
    icon: 'briefcase',
  },
  {
    id: 'citizens',
    label: 'Граждане',
    description: 'Доверие, доступность и понятность решений',
    icon: 'users',
  },
  {
    id: 'documents',
    label: 'Документы',
    description: 'Источники, выдержки и проверяемые основания',
    icon: 'aiBook',
  },
  {
    id: 'agents',
    label: 'Агенты',
    description: 'Специализированные участники совета',
    icon: 'agent',
  },
  {
    id: 'debate',
    label: 'Дебаты',
    description: 'Возражения, уточнения и проверка гипотез',
    icon: 'bubbleChat',
  },
  {
    id: 'decision',
    label: 'Итоговое решение',
    description: 'Синтез аргументов в одно заключение',
    icon: 'target',
  },
]
