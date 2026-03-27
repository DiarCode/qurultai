<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import AppIcon from './AppIcon.vue'

const route = useRoute()

const items = [
  { to: '/chat', label: 'Чат совета', icon: 'aiChat' },
  { to: '/agents', label: 'Агенты', icon: 'agent' },
] as const

const activePath = computed(() => {
  if (route.path.startsWith('/agents')) {
    return '/agents'
  }

  return '/chat'
})
</script>

<template>
  <nav
    class="fixed inset-x-0 bottom-5 z-40 flex justify-center px-5 lg:inset-x-auto lg:bottom-auto lg:left-8 lg:top-1/2 lg:-translate-y-1/2 lg:px-0"
  >
    <div
      class="relative flex items-center gap-2 rounded-full border border-slate-200/60 bg-white/75 backdrop-blur-xl p-2 shadow-[0_4px_24px_-8px_rgba(15,23,42,0.08)] lg:flex-col lg:rounded-4xl lg:p-3"
    >
      <!-- Glass reflection overlay -->
      <div
        class="pointer-events-none absolute inset-0 rounded-full lg:rounded-4xl bg-gradient-to-br from-white/30 via-transparent to-transparent"
      />

      <!-- Home link (desktop only) -->
      <RouterLink
        to="/"
        class="ornament-ring hidden size-12 items-center justify-center text-slate-900 transition-all duration-500 hover:scale-105 hover:shadow-md lg:flex"
        aria-label="На главную"
      >
        <AppIcon name="yurt" :size="22" />
      </RouterLink>

      <!-- Navigation items -->
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        :aria-label="item.label"
        class="group relative flex size-12 items-center justify-center rounded-full transition-all duration-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900/20"
        :class="
          activePath === item.to
            ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/20'
            : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
        "
      >
        <AppIcon :name="item.icon" :size="20" />
        <span class="sr-only">{{ item.label }}</span>
      </RouterLink>

      <!-- Council badge (desktop only) -->
      <div
        class="hidden rounded-full border border-slate-200/60 bg-slate-50/80 px-4 py-2 text-xs font-light tracking-tight text-slate-500 lg:inline-flex"
      >
        Совет
      </div>
    </div>
  </nav>
</template>