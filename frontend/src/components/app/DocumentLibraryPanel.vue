<script setup lang="ts">
import { toast } from 'vue-sonner'

import type { AgentDocument } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

import AppIcon from './AppIcon.vue'
import EmptyStateCouncil from './EmptyStateCouncil.vue'

defineProps<{
  documents: AgentDocument[]
}>()

function notifyUpload() {
  toast('Загрузка документов будет подключена к реальному хранилищу', {
    description: 'Интерфейс уже готов для drag-and-drop и статусов индексации.',
  })
}
</script>

<template>
  <div class="space-y-6">
    <div class="surface-panel flex flex-col gap-5 p-6 md:flex-row md:items-center md:justify-between">
      <div class="space-y-3">
        <p class="section-kicker">Документы агента</p>
        <p class="text-sm font-light leading-7 text-slate-500">
          Загружайте источники для RAG-контура, отслеживайте статус и сохраняйте тематические теги
          для быстрой проверки аргументов.
        </p>
      </div>
      <Button class="rounded-full px-6" @click="notifyUpload">
        <AppIcon name="attachment" :size="16" />
        Загрузить документ
      </Button>
    </div>

    <button
      type="button"
      class="surface-panel flex w-full flex-col items-center justify-center gap-4 border-dashed border-slate-200 px-8 py-12 text-center transition-all duration-500 hover:border-slate-300 hover:shadow-lg"
      @click="notifyUpload"
    >
      <div class="ornament-ring flex size-16 items-center justify-center text-slate-900">
        <AppIcon name="document" :size="24" />
      </div>
      <div>
        <p class="text-base font-light tracking-tight text-slate-900">Перетащите файл сюда</p>
        <p class="mt-2 text-sm font-light leading-6 text-slate-500">
          Или выберите документ вручную: PDF, Markdown, таблицы и протоколы.
        </p>
      </div>
    </button>

    <div v-if="documents.length" class="grid gap-5">
      <article
        v-for="document in documents"
        :key="document.id"
        class="relative overflow-hidden rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl"
      >
        <div
          class="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/50 via-transparent to-transparent opacity-50"
        />
        <div class="relative flex flex-col gap-5 p-6 md:flex-row md:items-start md:justify-between">
          <div class="flex gap-5">
            <div class="ornament-ring flex size-14 items-center justify-center text-slate-900">
              <AppIcon :name="document.type === 'PDF' ? 'filePdf' : 'documentAlt'" :size="18" />
            </div>
            <div class="space-y-3">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-base font-light tracking-tight text-slate-900">
                  {{ document.title }}
                </h3>
                <Badge variant="outline">{{ document.type }}</Badge>
                <Badge variant="secondary">{{ document.status }}</Badge>
              </div>
              <p class="text-sm font-light leading-7 text-slate-500">
                {{ document.summary }}
              </p>
              <div class="flex flex-wrap gap-2">
                <Badge v-for="tag in document.tags" :key="tag" variant="muted">
                  {{ tag }}
                </Badge>
              </div>
            </div>
          </div>
          <p class="text-xs font-light tracking-tight text-slate-400">
            {{ document.date }}
          </p>
        </div>
      </article>
    </div>

    <EmptyStateCouncil
      v-else
      icon="document"
      title="Документы ещё не добавлены"
      description="Подключите корпус источников, чтобы агент мог ссылаться на документы и строить аргументацию на проверяемой базе."
      action-label="Загрузить первый документ"
      @action="notifyUpload"
    />
  </div>
</template>