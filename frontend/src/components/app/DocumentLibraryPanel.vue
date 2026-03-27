<script setup lang="ts">
import { toast } from 'vue-sonner'

import type { AgentDocument } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

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
  <div class="space-y-5">
    <div
      class="surface-panel flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between"
    >
      <div class="space-y-2">
        <p class="section-kicker">Документы агента</p>
        <p class="text-sm leading-7 text-muted-foreground">
          Загружайте источники для RAG-контура, отслеживайте статус и сохраняйте тематические теги
          для быстрой проверки аргументов.
        </p>
      </div>
      <Button class="rounded-full px-5" @click="notifyUpload">
        <AppIcon name="attachment" :size="16" />
        Загрузить документ
      </Button>
    </div>

    <button
      type="button"
      class="surface-panel flex w-full flex-col items-center justify-center gap-3 border-dashed px-6 py-10 text-center transition-colors hover:border-primary/35"
      @click="notifyUpload"
    >
      <div class="ornament-ring flex size-16 items-center justify-center text-primary">
        <AppIcon name="document" :size="24" />
      </div>
      <div>
        <p class="text-base font-medium text-foreground">Перетащите файл сюда</p>
        <p class="mt-2 text-sm leading-6 text-muted-foreground">
          Или выберите документ вручную: PDF, Markdown, таблицы и протоколы.
        </p>
      </div>
    </button>

    <div v-if="documents.length" class="grid gap-4">
      <Card
        v-for="document in documents"
        :key="document.id"
        class="rounded-[2rem] border-border/80 bg-card/88"
      >
        <CardContent class="flex flex-col gap-4 pt-6 md:flex-row md:items-start md:justify-between">
          <div class="flex gap-4">
            <div class="ornament-ring flex size-12 items-center justify-center text-primary">
              <AppIcon :name="document.type === 'PDF' ? 'filePdf' : 'documentAlt'" :size="18" />
            </div>
            <div class="space-y-2">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-base font-medium text-foreground">
                  {{ document.title }}
                </h3>
                <Badge variant="outline">{{ document.type }}</Badge>
                <Badge variant="secondary">{{ document.status }}</Badge>
              </div>
              <p class="text-sm leading-7 text-muted-foreground">
                {{ document.summary }}
              </p>
              <div class="flex flex-wrap gap-2">
                <Badge v-for="tag in document.tags" :key="tag" variant="muted">
                  {{ tag }}
                </Badge>
              </div>
            </div>
          </div>
          <p class="text-xs uppercase tracking-[0.18em] text-muted-foreground">
            {{ document.date }}
          </p>
        </CardContent>
      </Card>
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
