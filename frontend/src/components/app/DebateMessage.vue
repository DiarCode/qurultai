<script setup lang="ts">
import { computed } from 'vue'

import { renderMarkdownHtml } from '@/lib/richText'
import type { DebateMessageRecord, ChatParticipantRecord } from '@/types/chat'

import { Badge } from '@/components/ui/badge'
import { agentIconForRole } from '@/lib/council-ui'

import AppIcon from './AppIcon.vue'
import ReferenceChip from './ReferenceChip.vue'

const props = defineProps<{
  message: DebateMessageRecord
  participant?: ChatParticipantRecord | null
}>()

const title = computed(() => {
  if (props.message.source_agent_name) {
    return props.message.source_agent_name
  }

  switch (props.message.role) {
    case 'orchestrator':
      return 'Orchestrator'
    case 'critic':
      return 'Critic'
    case 'final':
      return 'Final Report Agent'
    default:
      return 'Council'
  }
})

const roleLabel = computed(() => props.participant?.role ?? props.message.role)

const badgeVariant = computed(() => {
  switch (props.message.role) {
    case 'critic':
      return 'warning'
    case 'final':
      return 'secondary'
    case 'orchestrator':
      return 'outline'
    default:
      return 'success'
  }
})

const stageLabel = computed(() => {
  switch (props.message.stage) {
    case 'analysis':
      return 'Analysis'
    case 'critique':
      return 'Critique'
    case 'final_report':
      return 'Finalization'
    case 'orchestration':
      return 'Orchestration'
    default:
      return 'Debate message'
  }
})

const messageHtml = computed(() => renderMarkdownHtml(props.message.content))
</script>

<template>
  <article
    class="surface-panel space-y-5 border-l-4 p-5 transition-all duration-500"
    :class="
      message.role === 'final'
        ? 'border-l-slate-900 bg-gradient-to-br from-white/95 via-slate-50/80 to-white/90'
        : 'border-l-slate-200'
    "
  >
    <div class="flex items-start gap-4">
      <div class="ornament-ring flex size-14 shrink-0 items-center justify-center text-slate-900">
        <AppIcon :name="agentIconForRole(roleLabel)" :size="22" />
      </div>

      <div class="min-w-0 flex-1 space-y-4">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="space-y-2">
            <div class="flex flex-wrap items-center gap-2">
              <h3 class="text-sm font-light tracking-tight text-slate-900">
                {{ title }}
              </h3>
              <Badge :variant="badgeVariant">{{ stageLabel }}</Badge>
              <Badge variant="muted">{{ roleLabel }}</Badge>
            </div>
            <div class="flex flex-wrap items-center gap-2 text-xs font-light text-slate-400">
              <span>{{ new Date(message.created_at).toLocaleTimeString('en-US') }}</span>
              <span v-if="message.is_partial" class="inline-flex items-center gap-2">
                <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-slate-400" />
                Typing
              </span>
            </div>
          </div>
        </div>

        <div class="qurultai-richtext q-debate-prose" v-html="messageHtml" />

        <div v-if="message.tool_calls.length" class="flex flex-wrap gap-2">
          <Badge
            v-for="toolCall in message.tool_calls"
            :key="`${message.id}-${toolCall.name}`"
            variant="outline"
          >
            {{ toolCall.name }} · {{ toolCall.output_summary || toolCall.status }}
          </Badge>
        </div>

        <div v-if="message.citations.length" class="flex flex-wrap gap-2">
          <ReferenceChip
            v-for="reference in message.citations"
            :key="reference.id"
            :reference="reference"
          />
        </div>
      </div>
    </div>
  </article>
</template>
