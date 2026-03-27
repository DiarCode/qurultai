import { createRouter, createWebHistory } from 'vue-router'

import CouncilLayout from '@/layouts/CouncilLayout.vue'
import AgentDetailsPage from '@/pages/AgentDetailsPage.vue'
import AgentsPage from '@/pages/AgentsPage.vue'
import ChatPage from '@/pages/ChatPage.vue'
import LandingPage from '@/pages/LandingPage.vue'
import { applyRouteSeo } from '@/lib/seo'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingPage,
      meta: {
        title: 'Qurultai — цифровой совет ИИ',
        description:
          'Qurultai — мультиагентная AI-платформа с культурно выверенным интерфейсом, где совет агентов анализирует документы, спорит по источникам и собирает итоговый вывод.',
        keywords:
          'Qurultai, совет ИИ, мультиагентная платформа, AI council, deliberation platform, агенты, документы, дебаты',
      },
    },
    {
      path: '/',
      component: CouncilLayout,
      children: [
        {
          path: 'chat',
          name: 'chat',
          component: ChatPage,
          meta: {
            title: 'Qurultai — координационный чат и живой поток агентов',
            description:
              'Координационный чат Qurultai показывает пользовательский запрос, живое обсуждение агентов, ссылки на документы и итоговое заключение в одном рабочем пространстве.',
            keywords:
              'Qurultai chat, координационный чат, поток агентов, AI debate, RAG references, deliberation workspace',
          },
        },
        {
          path: 'agents',
          name: 'agents',
          component: AgentsPage,
          meta: {
            title: 'Qurultai — агенты совета',
            description:
              'Просматривайте, создавайте и настраивайте агентов Qurultai: роли, документы, навыки, статусы и фокус каждого участника совета.',
            keywords:
              'Qurultai agents, агенты ИИ, настройки агентов, документы агента, навыки агента, AI roster',
          },
        },
        {
          path: 'agents/:id',
          name: 'agent-details',
          component: AgentDetailsPage,
          meta: {
            title: 'Qurultai — профиль агента',
            description:
              'Профиль агента Qurultai с деталями роли, документами, RAG-источниками, навыками и параметрами внутреннего эксперта.',
            keywords:
              'Qurultai agent profile, профиль агента, RAG источники, навыки агента, конфигурация AI агента',
          },
        },
      ],
    },
  ],
})

router.afterEach((to) => {
  applyRouteSeo(to)
})

export default router
