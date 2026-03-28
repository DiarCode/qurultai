<script setup lang="ts">
import { toast } from 'vue-sonner'

import type { ExportOption } from '@/types/council'

import { Button } from '@/components/ui/button'

import AppIcon from './AppIcon.vue'

defineProps<{
  options: ExportOption[]
}>()

function exportReport(label: string) {
  toast('Экспорт подготовлен как демонстрационный сценарий', {
    description: `Формат: ${label}`,
  })
}
</script>

<template>
  <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
    <button
      v-for="option in options"
      :key="option.id"
      class="group surface-panel flex items-center gap-5 p-5 text-left transition-all duration-500 hover:-translate-y-1 hover:border-slate-200 hover:shadow-lg"
      type="button"
      @click="exportReport(option.label)"
    >
      <div
        class="ornament-ring flex size-14 items-center justify-center text-slate-900 transition-transform duration-500 group-hover:scale-[1.03]"
      >
        <AppIcon :name="option.icon" :size="18" />
      </div>
      <div class="flex-1">
        <p class="text-sm font-light tracking-tight text-slate-900">Скачать {{ option.label }}</p>
        <p class="text-xs font-light leading-5 text-slate-500">
          {{ option.description }}
        </p>
      </div>
      <Button variant="ghost" size="icon-sm" class="rounded-full">
        <AppIcon name="arrowRight" :size="16" />
      </Button>
    </button>
  </div>
</template>