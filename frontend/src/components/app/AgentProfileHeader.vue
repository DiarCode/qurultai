<script setup lang="ts">
import type { AgentProfile } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

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
  <Card class="rounded-[2rem] border-border/80 bg-card/88">
    <CardContent class="grid gap-6 pt-6 md:grid-cols-[minmax(0,1fr)_280px]">
      <div class="flex items-start gap-4">
        <div class="ornament-ring flex size-16 items-center justify-center text-primary">
          <AppIcon :name="agent.icon" :size="26" />
        </div>
        <div class="space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <Badge :variant="statusVariant[agent.status]">
              {{ statusLabel[agent.status] }}
            </Badge>
            <Badge variant="outline">{{ agent.focus }}</Badge>
          </div>
          <div>
            <h1
              class="font-display text-[clamp(2.4rem,4vw,4rem)] leading-[0.95] tracking-[-0.04em] text-foreground"
            >
              {{ agent.name }}
            </h1>
            <p class="mt-2 text-base text-[color:var(--ornament-strong)]">
              {{ agent.role }}
            </p>
          </div>
          <p class="max-w-2xl text-sm leading-7 text-muted-foreground md:text-base">
            {{ agent.description }}
          </p>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="rounded-[1.5rem] border border-border/70 bg-[color:var(--surface-muted)] p-4">
          <p class="text-xs uppercase tracking-[0.22em] text-muted-foreground">Документы</p>
          <p class="mt-3 text-2xl font-medium text-foreground">
            {{ agent.documentsCount }}
          </p>
        </div>
        <div class="rounded-[1.5rem] border border-border/70 bg-[color:var(--surface-muted)] p-4">
          <p class="text-xs uppercase tracking-[0.22em] text-muted-foreground">Навыки</p>
          <p class="mt-3 text-2xl font-medium text-foreground">
            {{ agent.skillsCount }}
          </p>
        </div>
        <div class="col-span-2 rounded-[1.5rem] border border-border/70 bg-background/85 p-4">
          <p class="text-xs uppercase tracking-[0.22em] text-muted-foreground">Роль в совете</p>
          <p class="mt-3 text-sm leading-7 text-foreground">
            {{ agent.systemPrompt }}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
