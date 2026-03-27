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
  <aside id="debate-panel" class="min-w-0 xl:w-[30rem] 2xl:w-[32rem]">
    <section class="surface-panel overflow-hidden xl:sticky xl:top-6">
      <div class="border-b border-border/70 px-5 py-5">
        <div class="flex flex-col gap-5">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div class="max-w-xl space-y-3">
              <p class="section-kicker">Внутренний круг</p>
              <div class="space-y-2">
                <h2
                  class="font-display text-[clamp(2rem,3vw,2.9rem)] leading-[0.96] tracking-[-0.03em] text-foreground"
                >
                  Живое обсуждение агентов
                </h2>
                <p class="text-sm leading-7 text-muted-foreground">
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

          <div class="grid gap-3">
            <div
              class="rounded-[1.5rem] border border-border/70 bg-[color:var(--surface-muted)] p-4"
            >
              <div class="flex items-start gap-3">
                <div
                  class="ornament-ring flex size-11 shrink-0 items-center justify-center text-primary"
                >
                  <AppIcon name="user" :size="18" />
                </div>
                <div class="min-w-0 space-y-2">
                  <div class="flex flex-wrap items-center gap-2">
                    <Badge variant="secondary">Ваш запрос</Badge>
                    <span class="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                      {{ request.timestamp }}
                    </span>
                  </div>
                  <p class="text-sm leading-7 text-foreground">
                    {{ request.content }}
                  </p>
                </div>
              </div>
            </div>

            <div class="grid gap-3 md:grid-cols-[minmax(0,1fr)_auto]">
              <div class="flex flex-wrap gap-2">
                <Badge
                  v-for="stage in stageSummary"
                  :key="stage.id"
                  :variant="activeMessage?.stage === stage.id ? 'secondary' : 'outline'"
                  class="px-3 py-1.5"
                >
                  {{ stage.label }} · {{ stage.count }}
                </Badge>
              </div>

              <div
                class="inline-flex items-center gap-2 rounded-full border border-border/70 bg-background/80 px-3 py-1.5 text-xs text-muted-foreground"
              >
                <AppIcon
                  :name="isFinished ? 'check' : 'loading'"
                  :size="14"
                  :class="isFinished ? 'text-emerald-600' : 'animate-spin text-primary'"
                />
                <span v-if="currentAgent"> Сейчас отвечает {{ currentAgent.name }} </span>
                <span v-else>Цикл завершён</span>
              </div>
            </div>

            <div class="rounded-[1.5rem] border border-border/70 bg-background/75 px-4 py-3">
              <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                {{ currentStageLabel }}
              </p>
              <p class="mt-2 text-sm leading-7 text-foreground">
                Показано {{ visibleMessages.length }} из {{ messages.length }} сообщений внутреннего
                круга.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="px-5 py-4">
        <div class="flex items-center justify-between gap-3">
          <p class="text-sm font-medium text-foreground">Поток сообщений совета</p>
          <span class="text-xs uppercase tracking-[0.18em] text-muted-foreground">
            В реальном времени
          </span>
        </div>

        <Separator class="mt-4" />

        <div
          ref="feedRef"
          class="mt-4 max-h-[34rem] space-y-4 overflow-y-auto pr-1 xl:max-h-[calc(100vh-26rem)]"
        >
          <TransitionGroup name="debate-flow" tag="div" class="space-y-4">
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
