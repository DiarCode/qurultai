<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { Badge } from '@/components/ui/badge'

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
    class="fixed inset-x-0 bottom-4 z-40 flex justify-center px-4 lg:inset-x-auto lg:bottom-auto lg:left-6 lg:top-1/2 lg:-translate-y-1/2 lg:px-0"
  >
    <div
      class="flex items-center gap-2 rounded-full border border-border/80 bg-background/85 p-2 shadow-[0_18px_40px_-28px_rgba(73,48,24,0.45)] backdrop-blur-md lg:flex-col lg:rounded-[2rem]"
    >
      <RouterLink
        to="/"
        class="ornament-ring hidden size-12 items-center justify-center text-primary transition-colors hover:text-primary/85 lg:flex"
        aria-label="На главную"
      >
        <AppIcon name="yurt" :size="22" />
      </RouterLink>

      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        :aria-label="item.label"
        class="group relative flex size-12 items-center justify-center rounded-full transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60"
        :class="
          activePath === item.to
            ? 'bg-primary text-primary-foreground shadow-[0_12px_24px_-20px_rgba(188,118,58,0.85)]'
            : 'text-muted-foreground hover:bg-[color:var(--surface-muted)] hover:text-foreground'
        "
      >
        <AppIcon :name="item.icon" :size="20" />
        <span class="sr-only">{{ item.label }}</span>
      </RouterLink>

      <Badge
        variant="outline"
        class="hidden rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.24em] lg:inline-flex"
      >
        Совет
      </Badge>
    </div>
  </nav>
</template>
