<script setup lang="ts">
import { RouterLink } from 'vue-router'

import type { AgentProfile } from '@/types/council'

import { Badge } from '@/components/ui/badge'

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
    <article
      class="relative h-full overflow-hidden rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl transition-all duration-700 group-hover:-translate-y-1.5 group-hover:border-slate-200 group-hover:shadow-lg"
    >
      <!-- Glass reflection -->
      <div
        class="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/50 via-transparent to-transparent opacity-50"
      />

      <div class="relative p-6 sm:p-8">
        <!-- Header -->
        <div class="flex items-start justify-between gap-4 mb-5">
          <div class="ornament-ring flex size-16 items-center justify-center text-slate-900">
            <AppIcon :name="agent.icon" :size="24" />
          </div>
          <Badge :variant="statusVariant[agent.status]">
            {{ statusLabel[agent.status] }}
          </Badge>
        </div>

        <!-- Title -->
        <div class="space-y-2 mb-5">
          <h3 class="text-xl font-light tracking-tight text-slate-900">
            {{ agent.name }}
          </h3>
          <p class="text-sm font-light text-slate-400">
            {{ agent.role }}
          </p>
        </div>

        <!-- Description -->
        <p class="text-sm font-light leading-7 text-slate-500 mb-6">
          {{ agent.description }}
        </p>

        <!-- Stats -->
        <div class="grid grid-cols-2 gap-3">
          <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-4">
            <p class="text-xs font-light tracking-tight text-slate-400">Документы</p>
            <p class="mt-2 text-xl font-light text-slate-900">
              {{ agent.documentsCount }}
            </p>
          </div>
          <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-4">
            <p class="text-xs font-light tracking-tight text-slate-400">Навыки</p>
            <p class="mt-2 text-xl font-light text-slate-900">
              {{ agent.skillsCount }}
            </p>
          </div>
        </div>
      </div>
    </article>
  </RouterLink>
</template>