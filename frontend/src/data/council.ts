import type {
  AgentProfile,
  AgentSkill,
  ChatMessage,
  DebateMessage,
  ExportOption,
  LandingNode,
  SourceReference,
} from '@/types/council'

const references: SourceReference[] = [
  {
    id: 'ref-national-plan',
    title: 'Национальный план цифровой трансформации',
    type: 'PDF',
    location: 'стр. 14-18',
    summary:
      'Фиксирует приоритет прозрачности решений, публичной отчётности и поэтапного внедрения сервисов с высоким влиянием на граждан.',
  },
  {
    id: 'ref-regions',
    title: 'Сводка региональных обращений',
    type: 'Аналитика',
    location: 'кластер C-12',
    summary:
      'Показывает, что пользователи ожидают не только ответ, но и видимость аргументов, источников и расхождений между позициями.',
  },
  {
    id: 'ref-charter',
    title: 'Хартия агентного взаимодействия',
    type: 'Markdown',
    location: 'раздел 3.2',
    summary:
      'Описывает порядок: начальная позиция, взаимные возражения, критика синтеза и выпуск итогового заключения с цитированием.',
  },
  {
    id: 'ref-brief',
    title: 'Отраслевой бриф по экономическим рискам',
    type: 'Протокол',
    location: 'фрагмент 07',
    summary:
      'Содержит сценарии влияния на бизнес и указывает на важность стресс-тестов перед внедрением новых регуляторных решений.',
  },
]

const [nationalPlanRef, regionalAppealsRef, charterRef, economicBriefRef] = references

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

export const chatMessages: ChatMessage[] = [
  {
    id: 'chat-1',
    author: 'user',
    label: 'Вы',
    content:
      'Подготовьте рекомендацию по запуску региональной программы цифровых общественных приёмных и покажите, какие риски нужно снять до пилота.',
    timestamp: '09:12',
  },
  {
    id: 'chat-2',
    author: 'system',
    label: 'Координатор совета',
    content:
      'Совет уже собрал предварительные позиции. Я веду общую линию разговора, а детали внутреннего обсуждения можно открыть отдельно.',
    timestamp: '09:13',
  },
  {
    id: 'chat-3',
    author: 'system',
    label: 'Координатор совета',
    content:
      'На текущем этапе консенсус складывается вокруг поэтапного запуска: сначала пилот в двух регионах, затем аудит понятности, нагрузки и качества ссылок на источники.',
    timestamp: '09:15',
  },
]

export const debateMessages: DebateMessage[] = [
  {
    id: 'debate-1',
    agentId: 'adal-guardian',
    stage: 'position',
    stance: 'Базовая позиция',
    tone: 'support',
    timestamp: '09:13',
    content:
      'Пилот допустим, если каждое итоговое сообщение сопровождается ссылкой на первичный документ и если для граждан сохраняется ясная траектория обжалования решения.',
    citations: [nationalPlanRef!, regionalAppealsRef!],
  },
  {
    id: 'debate-2',
    agentId: 'dala-economist',
    stage: 'position',
    stance: 'Экономическая оценка',
    tone: 'caution',
    timestamp: '09:14',
    content:
      'Масштабировать программу сразу рискованно: расходы на сопровождение и проверку источников растут быстрее, чем экономия от автоматизации на раннем этапе.',
    citations: [economicBriefRef!],
  },
  {
    id: 'debate-3',
    agentId: 'arhivist',
    stage: 'debate',
    stance: 'Уточнение по источникам',
    tone: 'question',
    timestamp: '09:14',
    content:
      'Если мы хотим доверия, нужно выводить не только документ, но и конкретный фрагмент: страницу, chunk или выдержку, на которую опирается тезис.',
    replyToLabel: 'Ответ на экономическую оценку',
    citations: [nationalPlanRef!, charterRef!],
  },
  {
    id: 'debate-4',
    agentId: 'syntez',
    stage: 'synthesis',
    stance: 'Синтез',
    tone: 'synthesis',
    timestamp: '09:15',
    content:
      'Итог совета: запускать пилот в ограниченном контуре, публично показывать аргументы агентов, логировать ссылки на документы и проводить независимую проверку понятности выводов после первого месяца.',
    citations: [nationalPlanRef!, regionalAppealsRef!, charterRef!, economicBriefRef!],
  },
]

const sharedSkills: AgentSkill[] = [
  {
    id: 'skill-rag-audit',
    name: 'Аудит ссылок',
    description:
      'Проверяет, что тезисы опираются на конкретные выдержки и корректные локации в источниках.',
    category: 'risk',
  },
  {
    id: 'skill-policy-diff',
    name: 'Сравнение норм',
    description: 'Сопоставляет новые предложения с действующими нормами и выявляет противоречия.',
    category: 'analysis',
  },
  {
    id: 'skill-scenario',
    name: 'Сценарный анализ',
    description: 'Строит осторожный, базовый и ускоренный сценарии развития ситуации.',
    category: 'research',
  },
  {
    id: 'skill-briefing',
    name: 'Редакционное резюме',
    description: 'Собирает аргументы в ясное заключение для руководителя или рабочей группы.',
    category: 'writing',
  },
]

const [ragAuditSkill, policyDiffSkill, scenarioSkill, briefingSkill] = sharedSkills

export const availableSkills = sharedSkills

export const agents: AgentProfile[] = [
  {
    id: 'adal-guardian',
    name: 'Адал',
    role: 'Агент общественного доверия',
    description:
      'Следит за прозрачностью аргументов, формулировками для граждан и корректностью объяснения итогового вывода.',
    systemPrompt:
      'Оценивай предложения с позиции доверия, проверяемости, понятности для граждан и корректного раскрытия ограничений.',
    goals: [
      'Сохранять ясность решения для граждан',
      'Требовать видимые ссылки на документы',
      'Подсвечивать риск непрозрачных формулировок',
    ],
    constraints: [
      'Не предлагать запуск без понятного механизма обжалования',
      'Не принимать тезисы без документального основания',
    ],
    status: 'active',
    icon: 'shield',
    documentsCount: 12,
    skillsCount: 3,
    focus: 'Доверие и проверяемость',
    documents: [
      {
        id: 'doc-1',
        title: 'Памятка по стандартам объяснимости',
        type: 'PDF',
        status: 'Проверен',
        date: '12 марта 2026',
        tags: ['прозрачность', 'UX'],
        summary: 'Содержит требования к объяснению решений и работе с цитатами.',
      },
      {
        id: 'doc-2',
        title: 'Жалобы пользователей за IV квартал',
        type: 'CSV',
        status: 'Новый',
        date: '18 марта 2026',
        tags: ['обратная связь', 'регионы'],
        summary: 'Кластеризованные обращения о непонятных автоматизированных ответах.',
      },
    ],
    skills: [ragAuditSkill!, policyDiffSkill!, briefingSkill!],
  },
  {
    id: 'dala-economist',
    name: 'Дала',
    role: 'Агент экономической устойчивости',
    description:
      'Оценивает стоимость внедрения, нагрузку на операционные команды и масштабируемость инициативы.',
    systemPrompt:
      'Делай осторожную оценку стоимости, рисков нагрузки и выгод от поэтапного внедрения.',
    goals: [
      'Удерживать реалистичный масштаб пилота',
      'Оценивать косвенные операционные затраты',
      'Проверять устойчивость на росте нагрузки',
    ],
    constraints: [
      'Не рекомендовать резкое масштабирование без стресс-теста',
      'Учитывать стоимость ручной проверки качества',
    ],
    status: 'active',
    icon: 'briefcase',
    documentsCount: 8,
    skillsCount: 2,
    focus: 'Экономика и масштабирование',
    documents: [
      {
        id: 'doc-3',
        title: 'Бриф по стоимости пилотов',
        type: 'Markdown',
        status: 'Проверен',
        date: '21 марта 2026',
        tags: ['стоимость', 'пилот'],
        summary: 'Содержит диапазоны затрат на пилоты в двух и пяти регионах.',
      },
    ],
    skills: [scenarioSkill!, briefingSkill!],
  },
  {
    id: 'arhivist',
    name: 'Архивист',
    role: 'Агент документальной базы',
    description:
      'Собирает корпус документов, структурирует выдержки и следит за точностью указания страниц и фрагментов.',
    systemPrompt:
      'Ставь документальную точность выше риторики, проверяй цитируемость каждого содержательного тезиса.',
    goals: [
      'Упорядочивать источники по темам и статусам',
      'Поддерживать точность ссылок до страницы или фрагмента',
      'Помогать совету быстро проверять тезисы',
    ],
    constraints: [
      'Не использовать недокументированные утверждения',
      'Помечать спорные или неполные фрагменты',
    ],
    status: 'draft',
    icon: 'reference',
    documentsCount: 23,
    skillsCount: 3,
    focus: 'Источники и RAG-контур',
    documents: [
      {
        id: 'doc-4',
        title: 'Реестр нормативных источников',
        type: 'PDF',
        status: 'Проверен',
        date: '25 марта 2026',
        tags: ['нормы', 'реестр'],
        summary: 'Каталог действующих документов с версионностью и темами.',
      },
      {
        id: 'doc-5',
        title: 'Методика разметки фрагментов',
        type: 'Markdown',
        status: 'Черновик',
        date: '24 марта 2026',
        tags: ['RAG', 'chunking'],
        summary: 'Описывает правила разбиения документов на фрагменты и требования к метаданным.',
      },
    ],
    skills: [ragAuditSkill!, policyDiffSkill!, scenarioSkill!],
  },
  {
    id: 'syntez',
    name: 'Синтез',
    role: 'Агент итогового заключения',
    description:
      'Собирает позиции совета, отмечает расхождения и выпускает аккуратное финальное заключение для пользователя.',
    systemPrompt:
      'Собирай аргументы разных агентов в одно ясное заключение, не скрывай разногласия и указывай основания.',
    goals: [
      'Формировать ясное заключение для руководителя',
      'Сохранять видимость разногласий внутри совета',
      'Отдавать компактный и проверяемый итог',
    ],
    constraints: [
      'Не сглаживать содержательные противоречия',
      'Не выпускать итог без краткой логики решения',
    ],
    status: 'paused',
    icon: 'sparkles',
    documentsCount: 5,
    skillsCount: 2,
    focus: 'Синтез и редактура',
    documents: [],
    skills: [scenarioSkill!, briefingSkill!],
  },
]

export const exportOptions: ExportOption[] = [
  {
    id: 'html',
    label: 'HTML',
    description: 'Структурированный веб-отчёт',
    icon: 'globe',
  },
  {
    id: 'pdf',
    label: 'PDF',
    description: 'Официальная версия для распространения',
    icon: 'filePdf',
  },
  {
    id: 'markdown',
    label: 'Markdown',
    description: 'Версия для совместной правки',
    icon: 'notebook',
  },
  {
    id: 'summary',
    label: 'Краткая справка',
    description: 'Компактное текстовое резюме',
    icon: 'mail',
  },
]

export const finalSummary = {
  title: 'Итоговое заключение',
  overview:
    'Совет рекомендует запуск пилота в двух регионах с открытым показом аргументов агентов, обязательным указанием источников и ежемесячной проверкой понятности для граждан.',
  bullets: [
    'Ограничить пилот двумя регионами с разной нагрузкой и профилем обращений.',
    'Показывать в пользовательском ответе не только вывод, но и логическую основу решения.',
    'Привязывать каждый содержательный тезис к проверяемому документу и фрагменту.',
  ],
  confidence: 'Умеренно высокая уверенность',
}
