<script setup lang="ts">
import { RouterLink } from 'vue-router'

import type { AgentProfile } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

import AppIcon from './AppIcon.vue'

defineProps<{
  agent: AgentProfile
}>()

const statusVariant = {
  active: 'success',
  draft: 'outline',
  paused: 'warning',
} as const

const statusLabel = {
  active: 'Активен',
  draft: 'Черновик',
  paused: 'На паузе',
} as const
</script>

<template>
  <RouterLink :to="`/agents/${agent.id}`" class="group block">
    <Card
      class="h-full rounded-[2rem] border-border/80 bg-card/88 transition-all duration-300 group-hover:-translate-y-1 group-hover:border-primary/35"
    >
      <CardHeader class="gap-4">
        <div class="flex items-center justify-between gap-4">
          <div class="ornament-ring flex size-14 items-center justify-center text-primary">
            <AppIcon :name="agent.icon" :size="22" />
          </div>
          <Badge :variant="statusVariant[agent.status]">
            {{ statusLabel[agent.status] }}
          </Badge>
        </div>
        <div class="space-y-2">
          <CardTitle class="text-xl">
            {{ agent.name }}
          </CardTitle>
          <p class="text-sm text-[color:var(--ornament-strong)]">
            {{ agent.role }}
          </p>
        </div>
      </CardHeader>
      <CardContent class="space-y-5">
        <p class="text-sm leading-7 text-muted-foreground">
          {{ agent.description }}
        </p>
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div
            class="rounded-[1.25rem] border border-border/70 bg-[color:var(--surface-muted)] p-3"
          >
            <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Документы</p>
            <p class="mt-2 text-lg font-medium text-foreground">
              {{ agent.documentsCount }}
            </p>
          </div>
          <div
            class="rounded-[1.25rem] border border-border/70 bg-[color:var(--surface-muted)] p-3"
          >
            <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Навыки</p>
            <p class="mt-2 text-lg font-medium text-foreground">
              {{ agent.skillsCount }}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  </RouterLink>
</template>
