<script setup lang="ts">
import type { AgentRecord } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { agentIconForRole, agentStatusLabel } from '@/lib/council-ui'

import AppIcon from './AppIcon.vue'

defineProps<{
  agent: AgentRecord
}>()

const statusVariant = {
  active: 'success',
  draft: 'outline',
  paused: 'warning',
} as const
</script>

<template>
  <article
    class="relative overflow-hidden rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl"
  >
    <!-- Glass reflection -->
    <div
      class="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/50 via-transparent to-transparent opacity-50"
    />

    <div class="relative grid gap-8 pt-8 md:grid-cols-[minmax(0,1fr)_300px]">
      <!-- Left: Profile Info -->
      <div class="flex items-start gap-5">
        <div class="ornament-ring flex size-18 items-center justify-center text-slate-900">
          <AppIcon :name="agentIconForRole(agent.role)" :size="28" />
        </div>
        <div class="space-y-4">
          <div class="flex flex-wrap items-center gap-2">
            <Badge :variant="statusVariant[agent.status]">
              {{ agentStatusLabel[agent.status] }}
            </Badge>
            <Badge variant="outline">{{ agent.role }}</Badge>
          </div>
          <div>
            <h1
              class="font-display text-[clamp(2.5rem,5vw,4.25rem)] leading-[0.94] tracking-tight text-slate-900"
            >
              {{ agent.name }}
            </h1>
            <p class="mt-3 text-base font-light text-slate-400">
              {{ agent.role }}
            </p>
          </div>
          <p class="max-w-2xl text-sm font-light leading-7 text-slate-500 sm:text-base">
            {{
              agent.description ||
              'Агент настроен для участия в совете и публикации проверяемых выводов.'
            }}
          </p>
        </div>
      </div>

      <!-- Right: Stats -->
      <div class="grid grid-cols-2 gap-4">
        <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5">
          <p class="text-xs font-light tracking-tight text-slate-400">Документы</p>
          <p class="mt-3 text-2xl font-light text-slate-900">
            {{ agent.documents.length }}
          </p>
        </div>
        <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5">
          <p class="text-xs font-light tracking-tight text-slate-400">Навыки</p>
          <p class="mt-3 text-2xl font-light text-slate-900">
            {{ agent.skills.length }}
          </p>
        </div>
        <div class="col-span-2 rounded-2xl border border-slate-100 bg-white/60 p-5">
          <p class="text-xs font-light tracking-tight text-slate-400">Роль в совете</p>
          <p class="mt-3 text-sm font-light leading-7 text-slate-700">
            {{ agent.system_prompt }}
          </p>
        </div>
      </div>
    </div>
  </article>
</template>
