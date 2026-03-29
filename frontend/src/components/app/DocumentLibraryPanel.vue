<script setup lang="ts">
import { computed, ref } from 'vue'

import type { DocumentRecord } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

import AppIcon from './AppIcon.vue'
import EmptyStateCouncil from './EmptyStateCouncil.vue'

const props = defineProps<{
  documents: DocumentRecord[]
  uploading?: boolean
  removable?: boolean
}>()

const emit = defineEmits<{
  upload: [file: File]
  remove: [documentId: string]
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)

const visibleDocuments = computed(() => props.documents)

function openFilePicker() {
  fileInputRef.value?.click()
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) {
    return
  }

  emit('upload', file)
  input.value = ''
}

function formatDate(value: string) {
  return new Date(value).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function formatSize(size: number) {
  if (size < 1024) {
    return `${size} B`
  }
  if (size < 1024 * 1024) {
    return `${Math.round(size / 102.4) / 10} KB`
  }
  return `${Math.round(size / 104857.6) / 10} MB`
}

function statusLabel(status: string) {
  switch (status) {
    case 'completed':
      return 'Готово'
    case 'processing':
      return 'В работе'
    case 'failed':
      return 'Ошибка'
    case 'uploaded':
      return 'Загружен'
    default:
      return status
  }
}
</script>

<template>
  <div class="space-y-6">
    <input ref="fileInputRef" type="file" class="hidden" @change="handleFileChange" />

    <div
      class="surface-panel flex flex-col gap-5 p-6 md:flex-row md:items-center md:justify-between"
    >
      <div class="space-y-3">
        <p class="section-kicker">Документы агента</p>
        <p class="text-sm font-light leading-7 text-slate-500">
          Загружайте источники для RAG-контура, отслеживайте их статус и давайте агенту проверяемую
          доказательную базу.
        </p>
      </div>
      <Button class="rounded-full px-6" :disabled="uploading" @click="openFilePicker">
        <AppIcon name="attachment" :size="16" />
        {{ uploading ? 'Загрузка...' : 'Загрузить документ' }}
      </Button>
    </div>

    <button
      type="button"
      class="surface-panel flex w-full flex-col items-center justify-center gap-4 border-dashed border-slate-200 px-8 py-12 text-center transition-all duration-500 hover:border-slate-300 hover:shadow-lg"
      :disabled="uploading"
      @click="openFilePicker"
    >
      <div class="ornament-ring flex size-16 items-center justify-center text-slate-900">
        <AppIcon name="document" :size="24" />
      </div>
      <div>
        <p class="text-base font-light tracking-tight text-slate-900">
          Перетащите файл сюда или выберите вручную
        </p>
        <p class="mt-2 text-sm font-light leading-6 text-slate-500">
          Поддерживаются PDF, Markdown, DOCX и текстовые материалы.
        </p>
      </div>
    </button>

    <div v-if="visibleDocuments.length" class="grid gap-5">
      <article
        v-for="document in visibleDocuments"
        :key="document.id"
        class="relative overflow-hidden rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl"
      >
        <div
          class="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/50 via-transparent to-transparent opacity-50"
        />
        <div class="relative flex flex-col gap-5 p-6 md:flex-row md:items-start md:justify-between">
          <div class="flex gap-5">
            <div class="ornament-ring flex size-14 items-center justify-center text-slate-900">
              <AppIcon
                :name="document.mime_type === 'application/pdf' ? 'filePdf' : 'documentAlt'"
                :size="18"
              />
            </div>
            <div class="space-y-3">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-base font-light tracking-tight text-slate-900">
                  {{ document.title }}
                </h3>
                <Badge variant="outline">{{ document.mime_type || 'file' }}</Badge>
                <Badge variant="secondary">{{ formatSize(document.size_bytes) }}</Badge>
                <Badge variant="secondary"
                  >upload · {{ statusLabel(document.upload_status) }}</Badge
                >
                <Badge :variant="document.index_status === 'failed' ? 'warning' : 'outline'">
                  index · {{ statusLabel(document.index_status) }}
                </Badge>
              </div>
              <p class="text-sm font-light leading-7 text-slate-500">
                {{
                  document.text_preview || 'Предпросмотр текста станет доступен после индексации.'
                }}
              </p>
              <div class="flex flex-wrap gap-2 text-xs font-light tracking-tight text-slate-400">
                <span>{{ document.chunk_count }} чанков</span>
                <span v-if="document.parser_kind">{{ document.parser_kind }}</span>
                <span>{{ document.source_filename }}</span>
              </div>
              <div class="flex flex-wrap gap-3">
                <a
                  v-if="document.download_url"
                  :href="document.download_url"
                  class="inline-flex items-center gap-2 text-sm font-light text-slate-700 transition hover:text-slate-900"
                  target="_blank"
                  rel="noreferrer"
                >
                  <AppIcon name="download" :size="14" />
                  Скачать
                </a>
                <button
                  v-if="removable"
                  type="button"
                  class="inline-flex items-center gap-2 text-sm font-light text-rose-600 transition hover:text-rose-700"
                  @click="emit('remove', document.id)"
                >
                  <AppIcon name="cancel" :size="14" />
                  Удалить
                </button>
              </div>
            </div>
          </div>
          <p class="text-xs font-light tracking-tight text-slate-400">
            {{ formatDate(document.created_at) }}
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
      @action="openFilePicker"
    />
  </div>
</template>
