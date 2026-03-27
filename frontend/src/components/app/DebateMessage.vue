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
    class="surface-panel space-y-5 border-l-4 p-5 transition-all duration-500"
    :class="
      message.tone === 'synthesis'
        ? 'border-l-slate-900 bg-gradient-to-br from-white/95 via-slate-50/80 to-white/90'
        : isLatest
          ? 'border-l-slate-400'
          : 'border-l-transparent'
    "
  >
    <div class="flex items-start gap-4">
      <div
        class="ornament-ring flex size-14 shrink-0 items-center justify-center text-slate-900 transition-transform duration-500"
        :class="isTyping ? 'scale-[1.04]' : ''"
      >
        <AppIcon :name="agent.icon" :size="22" />
      </div>

      <div class="min-w-0 flex-1 space-y-4">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="space-y-2">
            <div class="flex flex-wrap items-center gap-2">
              <h3 class="text-sm font-light tracking-tight text-slate-900">
                {{ agent.name }}
              </h3>
              <Badge :variant="toneVariant">{{ message.stance }}</Badge>
              <Badge variant="muted">{{ agent.role }}</Badge>
            </div>
            <div class="flex flex-wrap items-center gap-2 text-xs font-light text-slate-400">
              <span>{{ stageLabel }}</span>
              <span class="h-1 w-1 rounded-full bg-slate-200" />
              <span>{{ message.timestamp }}</span>
            </div>
          </div>

          <div
            v-if="isTyping"
            class="inline-flex items-center gap-2.5 rounded-full bg-slate-900/5 px-4 py-1.5"
          >
            <AppIcon name="loading" :size="14" class="animate-spin text-slate-400" />
            <span class="text-xs font-light text-slate-600">Печатает</span>
          </div>
        </div>

        <p
          v-if="message.replyToLabel"
          class="inline-flex rounded-full border border-slate-100 bg-white/70 px-4 py-1.5 text-xs font-light tracking-tight text-slate-400"
        >
          {{ message.replyToLabel }}
        </p>

        <p class="whitespace-pre-line text-sm font-light leading-7 text-slate-700">
          {{ renderedContent }}
          <span
            v-if="isTyping"
            aria-hidden="true"
            class="ml-1 inline-block h-5 w-0.5 animate-pulse rounded-full bg-slate-400 align-middle"
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