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
  <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
    <button
      v-for="option in options"
      :key="option.id"
      class="surface-panel group flex items-center gap-4 p-4 text-left transition-all hover:border-primary/35 hover:bg-background"
      type="button"
      @click="exportReport(option.label)"
    >
      <div
        class="ornament-ring flex size-12 items-center justify-center text-primary transition-transform group-hover:scale-[1.03]"
      >
        <AppIcon :name="option.icon" :size="18" />
      </div>
      <div class="flex-1">
        <p class="text-sm font-medium text-foreground">Скачать {{ option.label }}</p>
        <p class="text-xs leading-5 text-muted-foreground">
          {{ option.description }}
        </p>
      </div>
      <Button variant="ghost" size="icon-sm" class="rounded-full">
        <AppIcon name="arrowRight" :size="16" />
      </Button>
    </button>
  </div>
</template>
