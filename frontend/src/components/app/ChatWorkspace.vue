<script setup lang="ts">
import { ref } from 'vue'
import { toast } from 'vue-sonner'

import type { ChatMessage, ExportOption } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'

import AppIcon from './AppIcon.vue'
import ExportActions from './ExportActions.vue'
import OrnamentDivider from './OrnamentDivider.vue'

defineProps<{
  messages: ChatMessage[]
  exports: ExportOption[]
  summary: {
    title: string
    overview: string
    bullets: string[]
    confidence: string
  }
}>()

defineEmits<{ openDebate: [] }>()

const prompt = ref(
  'Подготовьте осторожный сценарий запуска с требованиями к прозрачности, понятности ответа и ссылкам на документы.',
)

function notifyAttachment() {
  toast('Загрузка документа будет подключена к API позже', {
    description: 'Интерфейс уже готов к привязке реального хранилища.',
  })
}

function notifySend() {
  toast('Сообщение добавлено в демонстрационный контур совета', {
    description: prompt.value,
  })
}
</script>

<template>
  <div class="space-y-6">
    <section class="surface-panel p-5 md:p-6">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div class="max-w-2xl space-y-3">
          <p class="section-kicker">Координационный чат</p>
          <h1
            class="font-display text-[clamp(2.1rem,5vw,4rem)] leading-[0.95] tracking-[-0.04em] text-foreground"
          >
            Центральный разговор с советом.
          </h1>
          <p class="text-sm leading-7 text-muted-foreground md:text-base">
            Пользователь говорит с координатором, а внутренний круг работает рядом: вы видите
            исходный запрос, ход обсуждения агентов и прозрачный переход к итоговому заключению.
          </p>
        </div>

        <div class="surface-card max-w-md space-y-4 p-4">
          <div class="flex items-center gap-3">
            <div class="ornament-ring flex size-11 items-center justify-center text-primary">
              <AppIcon name="workflow" :size="18" />
            </div>
            <div>
              <p class="text-sm font-medium text-foreground">Внутренний поток уже идёт</p>
              <p class="text-xs text-muted-foreground">
                Вы видите запрос слева и живое обсуждение агентов рядом
              </p>
            </div>
          </div>

          <Button class="w-full rounded-full" @click="$emit('openDebate')">
            <AppIcon name="view" :size="18" />
            Перейти к живому потоку агентов
          </Button>
        </div>
      </div>
    </section>

    <section class="surface-panel p-4 md:p-6">
      <div class="space-y-4">
        <div
          v-for="message in messages"
          :key="message.id"
          class="flex"
          :class="message.author === 'user' ? 'justify-end' : 'justify-start'"
        >
          <article
            class="max-w-3xl rounded-[1.75rem] border px-5 py-4"
            :class="
              message.author === 'user'
                ? 'border-primary/20 bg-primary/10 text-foreground'
                : 'border-border/70 bg-background/90 text-foreground'
            "
          >
            <div class="mb-2 flex items-center gap-2">
              <Badge :variant="message.author === 'user' ? 'secondary' : 'outline'">
                {{ message.label }}
              </Badge>
              <span class="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                {{ message.timestamp }}
              </span>
            </div>
            <p class="text-sm leading-7">
              {{ message.content }}
            </p>
          </article>
        </div>
      </div>
    </section>

    <section class="surface-panel p-5 md:p-6">
      <div class="flex flex-col gap-4 md:flex-row md:items-end">
        <label class="flex-1 space-y-2">
          <span class="text-sm font-medium text-foreground">Новый запрос</span>
          <Textarea v-model="prompt" class="min-h-32 bg-background/90" />
        </label>
        <div class="flex gap-3 md:flex-col">
          <Button variant="outline" class="rounded-full" @click="notifyAttachment">
            <AppIcon name="attachment" :size="16" />
            Документ
          </Button>
          <Button class="rounded-full" @click="notifySend">
            <AppIcon name="arrowRight" :size="16" />
            Отправить
          </Button>
        </div>
      </div>
    </section>

    <section class="surface-panel p-5 md:p-6">
      <div class="flex flex-col gap-5">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="max-w-2xl space-y-3">
            <p class="section-kicker">{{ summary.title }}</p>
            <p class="text-base leading-8 text-foreground">
              {{ summary.overview }}
            </p>
          </div>
          <Badge variant="secondary" class="px-3 py-1.5">
            {{ summary.confidence }}
          </Badge>
        </div>

        <OrnamentDivider />

        <ul class="grid gap-3 md:grid-cols-3">
          <li
            v-for="bullet in summary.bullets"
            :key="bullet"
            class="rounded-[1.5rem] border border-border/70 bg-[color:var(--surface-muted)] p-4 text-sm leading-7 text-foreground"
          >
            {{ bullet }}
          </li>
        </ul>
      </div>
    </section>

    <section class="space-y-4">
      <div class="flex items-center justify-between gap-4">
        <div>
          <p class="section-kicker">Экспорт</p>
          <p class="text-sm leading-7 text-muted-foreground">
            Выгрузите итог в нужном формате для совета, ведомства или рабочей группы.
          </p>
        </div>
        <Input
          class="hidden max-w-72 rounded-full bg-background/85 md:flex"
          placeholder="Поиск по материалам совета"
        />
      </div>
      <ExportActions :options="exports" />
    </section>
  </div>
</template>
