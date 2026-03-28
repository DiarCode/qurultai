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
  <div class="space-y-8">
    <!-- Header Section -->
    <section class="surface-panel p-6 sm:p-8">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div class="max-w-2xl space-y-4">
          <p class="section-kicker">Координационный чат</p>
          <h1
            class="font-display text-[clamp(2.2rem,5.5vw,4.25rem)] leading-[0.94] tracking-tight text-slate-900"
          >
            Центральный разговор с советом.
          </h1>
          <p class="text-sm font-light leading-7 text-slate-500 sm:text-base">
            Пользователь говорит с координатором, а внутренний круг работает рядом: вы видите
            исходный запрос, ход обсуждения агентов и прозрачный переход к итоговому заключению.
          </p>
        </div>

        <!-- Info Card -->
        <div class="elevated-glass max-w-md space-y-5 p-5">
          <div class="flex items-center gap-4">
            <div class="ornament-ring flex size-12 items-center justify-center text-slate-900">
              <AppIcon name="workflow" :size="18" />
            </div>
            <div>
              <p class="text-sm font-light tracking-tight text-slate-900">Внутренний поток уже идёт</p>
              <p class="text-xs font-light text-slate-500">
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

    <!-- Messages Section -->
    <section class="surface-panel p-5 sm:p-8">
      <div class="space-y-5">
        <div
          v-for="message in messages"
          :key="message.id"
          class="flex"
          :class="message.author === 'user' ? 'justify-end' : 'justify-start'"
        >
          <article
            class="max-w-3xl rounded-2xl border px-6 py-5 transition-all duration-500"
            :class="
              message.author === 'user'
                ? 'border-slate-900 bg-slate-900 text-white'
                : 'border-slate-100 bg-white/90 text-slate-900'
            "
          >
            <div class="mb-3 flex items-center gap-3">
              <Badge
                :variant="message.author === 'user' ? 'secondary' : 'outline'"
                :class="message.author === 'user' ? 'bg-white/10 border-white/20 text-white' : ''"
              >
                {{ message.label }}
              </Badge>
              <span class="text-xs font-light tracking-tight text-slate-400">
                {{ message.timestamp }}
              </span>
            </div>
            <p class="text-sm font-light leading-7">
              {{ message.content }}
            </p>
          </article>
        </div>
      </div>
    </section>

    <!-- Input Section -->
    <section class="surface-panel p-6 sm:p-8">
      <div class="flex flex-col gap-5 md:flex-row md:items-end">
        <label class="flex-1 space-y-3">
          <span class="text-sm font-light tracking-tight text-slate-900">Новый запрос</span>
          <Textarea v-model="prompt" class="min-h-36 bg-white/90" />
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

    <!-- Summary Section -->
    <section class="surface-panel p-6 sm:p-8">
      <div class="flex flex-col gap-6">
        <div class="flex flex-wrap items-start justify-between gap-5">
          <div class="max-w-2xl space-y-4">
            <p class="section-kicker">{{ summary.title }}</p>
            <p class="text-base font-light leading-8 text-slate-700">
              {{ summary.overview }}
            </p>
          </div>
          <Badge variant="secondary" class="px-4 py-2">
            {{ summary.confidence }}
          </Badge>
        </div>

        <OrnamentDivider />

        <ul class="grid gap-4 md:grid-cols-3">
          <li
            v-for="bullet in summary.bullets"
            :key="bullet"
            class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5 text-sm font-light leading-7 text-slate-700"
          >
            {{ bullet }}
          </li>
        </ul>
      </div>
    </section>

    <!-- Export Section -->
    <section class="space-y-5">
      <div class="flex items-center justify-between gap-5">
        <div>
          <p class="section-kicker">Экспорт</p>
          <p class="text-sm font-light leading-7 text-slate-500">
            Выгрузите итог в нужном формате для совета, ведомства или рабочей группы.
          </p>
        </div>
        <Input
          class="hidden max-w-80 rounded-full bg-white/80 md:flex"
          placeholder="Поиск по материалам совета"
        />
      </div>
      <ExportActions :options="exports" />
    </section>
  </div>
</template>