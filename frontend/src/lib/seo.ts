import type { RouteLocationNormalizedLoaded } from 'vue-router'

import { agents } from '@/data/council'

export interface RouteSeoMeta {
  title: string
  description: string
  keywords: string
  type?: 'website' | 'article'
}

const defaultSeo: RouteSeoMeta = {
  title: 'Qurultai — мультиагентный совет ИИ',
  description:
    'Qurultai — культурно выверенная мультиагентная AI-платформа, где агенты обсуждают документы, спорят по основаниям и собирают итоговое заключение.',
  keywords:
    'Qurultai, ИИ, мультиагентная система, AI council, debate agents, документы, deliberation, RAG, совет агентов',
  type: 'website',
}

function upsertMeta(selector: string, attributes: Record<string, string>) {
  let element = document.head.querySelector<HTMLMetaElement>(selector)

  if (!element) {
    element = document.createElement('meta')
    document.head.append(element)
  }

  Object.entries(attributes).forEach(([key, value]) => {
    element?.setAttribute(key, value)
  })
}

function resolveRouteSeo(route: RouteLocationNormalizedLoaded): RouteSeoMeta {
  const routeSeo = route.meta as Partial<RouteSeoMeta>

  if (route.name === 'agent-details') {
    const agentId = String(route.params.id ?? '')
    const agent = agents.find((entry) => entry.id === agentId)

    if (agent) {
      return {
        title: `${agent.name} — агент совета Qurultai`,
        description: `${agent.role}. ${agent.description}`,
        keywords: `${defaultSeo.keywords}, ${agent.name}, ${agent.role}, ${agent.focus}`,
        type: 'article',
      }
    }
  }

  return {
    ...defaultSeo,
    ...routeSeo,
  }
}

export function applyRouteSeo(route: RouteLocationNormalizedLoaded) {
  const seo = resolveRouteSeo(route)

  document.documentElement.lang = 'ru'
  document.title = seo.title

  upsertMeta('meta[name="description"]', {
    name: 'description',
    content: seo.description,
  })
  upsertMeta('meta[name="keywords"]', {
    name: 'keywords',
    content: seo.keywords,
  })
  upsertMeta('meta[name="robots"]', {
    name: 'robots',
    content: 'index, follow, max-image-preview:large',
  })
  upsertMeta('meta[name="author"]', {
    name: 'author',
    content: 'Qurultai',
  })
  upsertMeta('meta[name="application-name"]', {
    name: 'application-name',
    content: 'Qurultai',
  })
  upsertMeta('meta[name="apple-mobile-web-app-title"]', {
    name: 'apple-mobile-web-app-title',
    content: 'Qurultai',
  })
  upsertMeta('meta[name="theme-color"]', {
    name: 'theme-color',
    content: '#f6efe4',
  })
  upsertMeta('meta[property="og:title"]', {
    property: 'og:title',
    content: seo.title,
  })
  upsertMeta('meta[property="og:description"]', {
    property: 'og:description',
    content: seo.description,
  })
  upsertMeta('meta[property="og:type"]', {
    property: 'og:type',
    content: seo.type ?? 'website',
  })
  upsertMeta('meta[property="og:locale"]', {
    property: 'og:locale',
    content: 'ru_RU',
  })
  upsertMeta('meta[property="og:site_name"]', {
    property: 'og:site_name',
    content: 'Qurultai',
  })
  upsertMeta('meta[property="og:url"]', {
    property: 'og:url',
    content: window.location.href,
  })
  upsertMeta('meta[name="twitter:card"]', {
    name: 'twitter:card',
    content: 'summary_large_image',
  })
  upsertMeta('meta[name="twitter:title"]', {
    name: 'twitter:title',
    content: seo.title,
  })
  upsertMeta('meta[name="twitter:description"]', {
    name: 'twitter:description',
    content: seo.description,
  })
}
