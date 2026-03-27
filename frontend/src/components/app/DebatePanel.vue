<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'

import type { AgentProfile, ChatMessage, DebateMessage } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

import { useDebatePlayback } from '@/composables/useDebatePlayback'

import AppIcon from './AppIcon.vue'
import DebateMessageCard from './DebateMessage.vue'

const props = defineProps<{
  agents: AgentProfile[]
  messages: DebateMessage[]
  request: ChatMessage
}>()

const agentMap = computed(() => {
  return new Map(props.agents.map((agent) => [agent.id, agent]))
})

const stageSummary = computed(() => {
  return [
    {
      id: 'position',
      label: 'Позиции',
      count: props.messages.filter((message) => message.stage === 'position').length,
    },
    {
      id: 'debate',
      label: 'Ответы',
      count: props.messages.filter((message) => message.stage === 'debate').length,
    },
    {
      id: 'synthesis',
      label: 'Синтез',
      count: props.messages.filter((message) => message.stage === 'synthesis').length,
    },
  ] as const
})

const { activeMessage, isFinished, restartPlayback, visibleMessages } = useDebatePlayback(
  () => props.messages,
)

const currentAgent = computed(() => {
  return activeMessage.value ? (agentMap.value.get(activeMessage.value.agentId) ?? null) : null
})

const latestVisibleMessageId = computed(() => {
  return visibleMessages.value.length
    ? (visibleMessages.value[visibleMessages.value.length - 1]?.id ?? null)
    : null
})

const currentStageLabel = computed(() => {
  switch (activeMessage.value?.stage) {
    case 'position':
      return 'Раунд начальных позиций'
    case 'debate':
      return 'Раунд взаимных ответов'
    case 'synthesis':
      return 'Формируется итоговый синтез'
    default:
      return 'Совет завершил текущий цикл'
  }
})

const feedRef = ref<HTMLElement | null>(null)

watch(
  () => visibleMessages.value.length,
  async () => {
    await nextTick()
    feedRef.value?.scrollTo({
      top: feedRef.value.scrollHeight,
      behavior: 'smooth',
    })
  },
)
</script>

<template>
  <aside id="debate-panel" class="min-w-0 xl:w-[32rem] 2xl:w-[36rem]">
    <section class="surface-panel overflow-hidden xl:sticky xl:top-8">
      <!-- Header -->
      <div class="border-b border-slate-100 px-6 py-6">
        <div class="flex flex-col gap-6">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div class="max-w-xl space-y-4">
              <p class="section-kicker">Внутренний круг</p>
              <div class="space-y-3">
                <h2
                  class="font-display text-[clamp(2rem,3.5vw,3rem)] leading-[0.96] tracking-tight text-slate-900"
                >
                  Живое обсуждение агентов
                </h2>
                <p class="text-sm font-light leading-7 text-slate-500">
                  Рядом с координационным чатом виден полный ход рассуждения: кто начал, кто
                  возразил, на что сослался и как совет пришёл к финальному выводу.
                </p>
              </div>
            </div>

            <Button variant="outline" class="rounded-full" @click="restartPlayback">
              <AppIcon name="workflow" :size="16" />
              Повторить поток
            </Button>
          </div>

          <!-- Request Card -->
          <div class="space-y-4">
            <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5">
              <div class="flex items-start gap-4">
                <div class="ornament-ring flex size-12 shrink-0 items-center justify-center text-slate-900">
                  <AppIcon name="user" :size="18" />
                </div>
                <div class="min-w-0 space-y-3">
                  <div class="flex flex-wrap items-center gap-3">
                    <Badge variant="secondary">Ваш запрос</Badge>
                    <span class="text-xs font-light tracking-tight text-slate-400">
                      {{ request.timestamp }}
                    </span>
                  </div>
                  <p class="text-sm font-light leading-7 text-slate-700">
                    {{ request.content }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Stage Badges -->
            <div class="flex flex-wrap items-center gap-4">
              <div class="flex flex-wrap gap-2">
                <Badge
                  v-for="stage in stageSummary"
                  :key="stage.id"
                  :variant="activeMessage?.stage === stage.id ? 'secondary' : 'outline'"
                  class="px-4 py-2"
                >
                  {{ stage.label }} · {{ stage.count }}
                </Badge>
              </div>

              <div
                class="inline-flex items-center gap-2.5 rounded-full border border-slate-100 bg-white/80 px-4 py-2 text-xs font-light text-slate-500"
              >
                <AppIcon
                  :name="isFinished ? 'check' : 'loading'"
                  :size="14"
                  :class="isFinished ? 'text-emerald-600' : 'animate-spin text-slate-400'"
                />
                <span v-if="currentAgent"> Сейчас отвечает {{ currentAgent.name }} </span>
                <span v-else>Цикл завершён</span>
              </div>
            </div>

            <!-- Stage Info -->
            <div class="rounded-2xl border border-slate-100 bg-white/60 px-5 py-4">
              <p class="text-xs font-light tracking-tight text-slate-400">
                {{ currentStageLabel }}
              </p>
              <p class="mt-2 text-sm font-light leading-7 text-slate-700">
                Показано {{ visibleMessages.length }} из {{ messages.length }} сообщений внутреннего
                круга.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Messages Feed -->
      <div class="px-6 py-5">
        <div class="flex items-center justify-between gap-4">
          <p class="text-sm font-light tracking-tight text-slate-900">Поток сообщений совета</p>
          <span class="text-xs font-light tracking-tight text-slate-400">
            В реальном времени
          </span>
        </div>

        <Separator class="mt-5" />

        <div
          ref="feedRef"
          class="mt-5 max-h-[36rem] space-y-5 overflow-y-auto pr-1 xl:max-h-[calc(100vh-28rem)]"
        >
          <TransitionGroup name="debate-flow" tag="div" class="space-y-5">
            <DebateMessageCard
              v-for="message in visibleMessages"
              :key="message.id"
              :message="message"
              :agent="agentMap.get(message.agentId)!"
              :display-content="message.displayContent"
              :is-typing="message.isTyping"
              :is-latest="message.id === latestVisibleMessageId"
            />
          </TransitionGroup>
        </div>
      </div>
    </section>
  </aside>
</template>