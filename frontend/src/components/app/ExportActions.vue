<script setup lang="ts">
import type { ReportVariant } from '@/types/council'

import { Button } from '@/components/ui/button'

import AppIcon from './AppIcon.vue'

defineProps<{
  variants: ReportVariant[]
}>()

function labelForFormat(format: ReportVariant['format']) {
  switch (format) {
    case 'markdown':
      return 'Markdown'
    case 'html':
      return 'HTML'
    case 'pdf':
      return 'PDF'
  }
}

function descriptionForFormat(format: ReportVariant['format']) {
  switch (format) {
    case 'markdown':
      return 'Исходный текст отчёта для редактирования и хранения в репозитории.'
    case 'html':
      return 'Готовая веб-версия с форматированием для просмотра и пересылки.'
    case 'pdf':
      return 'Фиксированный документ для архива и официального оборота.'
  }
}

function iconForFormat(format: ReportVariant['format']) {
  switch (format) {
    case 'markdown':
      return 'documentAlt'
    case 'html':
      return 'globe'
    case 'pdf':
      return 'filePdf'
  }
}
</script>

<template>
  <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
    <a
      v-for="variant in variants"
      :key="variant.format"
      class="group surface-panel flex items-center gap-5 p-5 text-left transition-all duration-500 hover:-translate-y-1 hover:border-slate-200 hover:shadow-lg"
      :href="variant.download_url"
      target="_blank"
      rel="noreferrer"
    >
      <div
        class="ornament-ring flex size-14 items-center justify-center text-slate-900 transition-transform duration-500 group-hover:scale-[1.03]"
      >
        <AppIcon :name="iconForFormat(variant.format)" :size="18" />
      </div>
      <div class="flex-1">
        <p class="text-sm font-light tracking-tight text-slate-900">
          Скачать {{ labelForFormat(variant.format) }}
        </p>
        <p class="text-xs font-light leading-5 text-slate-500">
          {{ descriptionForFormat(variant.format) }}
        </p>
      </div>
      <Button variant="ghost" size="icon-sm" class="rounded-full">
        <AppIcon name="arrowRight" :size="16" />
      </Button>
    </a>
  </div>
</template>
