<script setup lang="ts">
import { computed } from 'vue'

import type { AgentProfile, DebateMessage as DebateMessageType } from '@/types/council'

import { Badge } from '@/components/ui/badge'

import AppIcon from './AppIcon.vue'
import ReferenceChip from './ReferenceChip.vue'

const props = withDefaults(
  defineProps<{
    message: DebateMessageType
    agent: AgentProfile
    displayContent?: string
    isTyping?: boolean
    isLatest?: boolean
  }>(),
  {
    displayContent: undefined,
    isTyping: false,
    isLatest: false,
  },
)

const toneVariant = computed(() => {
  switch (props.message.tone) {
    case 'support':
      return 'success'
    case 'caution':
      return 'warning'
    case 'question':
      return 'outline'
    case 'synthesis':
      return 'secondary'
    default:
      return 'default'
  }
})

const stageLabel = computed(() => {
  switch (props.message.stage) {
    case 'position':
      return 'Первая позиция'
    case 'debate':
      return 'Ответ и проверка'
    case 'synthesis':
      return 'Итоговый синтез'
    default:
      return 'Обсуждение'
  }
})

const renderedContent = computed(() => props.displayContent ?? props.message.content)
const shouldShowCitations = computed(() => !props.isTyping && props.message.citations.length > 0)
</script>

<template>
  <article
    class="surface-panel space-y-4 border-l-4 p-4 transition-all duration-500"
    :class="
      message.tone === 'synthesis'
        ? 'border-l-primary bg-[linear-gradient(180deg,rgba(255,252,247,0.98),rgba(246,237,226,0.88))]'
        : isLatest
          ? 'border-l-primary/40'
          : 'border-l-transparent'
    "
  >
    <div class="flex items-start gap-3">
      <div
        class="ornament-ring flex size-12 shrink-0 items-center justify-center text-primary transition-transform duration-300"
        :class="isTyping ? 'scale-[1.03]' : ''"
      >
        <AppIcon :name="agent.icon" :size="20" />
      </div>

      <div class="min-w-0 flex-1 space-y-3">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div class="space-y-2">
            <div class="flex flex-wrap items-center gap-2">
              <h3 class="text-sm font-medium text-foreground">
                {{ agent.name }}
              </h3>
              <Badge :variant="toneVariant">{{ message.stance }}</Badge>
              <Badge variant="muted">{{ agent.role }}</Badge>
            </div>
            <div class="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <span class="uppercase tracking-[0.2em]">{{ stageLabel }}</span>
              <span class="h-1 w-1 rounded-full bg-border" />
              <span>{{ message.timestamp }}</span>
            </div>
          </div>

          <div
            v-if="isTyping"
            class="inline-flex items-center gap-2 rounded-full bg-primary/8 px-3 py-1"
          >
            <AppIcon name="loading" :size="14" class="animate-spin text-primary" />
            <span class="text-xs font-medium text-primary">Печатает</span>
          </div>
        </div>

        <p
          v-if="message.replyToLabel"
          class="inline-flex rounded-full border border-border/70 bg-background/70 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-muted-foreground"
        >
          {{ message.replyToLabel }}
        </p>

        <p class="whitespace-pre-line text-sm leading-7 text-foreground">
          {{ renderedContent }}
          <span
            v-if="isTyping"
            aria-hidden="true"
            class="ml-1 inline-block h-5 w-0.5 animate-pulse rounded-full bg-primary/70 align-middle"
          />
        </p>

        <TransitionGroup
          v-if="shouldShowCitations"
          tag="div"
          name="debate-chip"
          class="flex flex-wrap gap-2"
        >
          <ReferenceChip
            v-for="reference in message.citations"
            :key="reference.id"
            :reference="reference"
          />
        </TransitionGroup>
      </div>
    </div>
  </article>
</template>
