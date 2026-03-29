<script setup lang="ts">
import { computed } from 'vue'

import type {
  ChatParticipantRecord,
  ChatRunRecord,
  ChatSessionRecord,
  DebateMessageRecord,
  ToolCallRecord,
} from '@/types/chat'

import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'

import AppIcon from './AppIcon.vue'
import DebateMessage from './DebateMessage.vue'

const props = defineProps<{
  currentSession: ChatSessionRecord | null
  currentRun: ChatRunRecord | null
  socketState: 'idle' | 'connecting' | 'open' | 'closed'
}>()

interface DeltaPayload {
  message_id: string
  role: string
  source_agent_id?: string | null
  source_agent_name?: string | null
  stage?: string | null
  delta: string
}

interface FinalPayload {
  message: DebateMessageRecord
}

function statusTone(status: ChatRunRecord['status'] | undefined) {
  switch (status) {
    case 'completed':
      return 'text-emerald-700'
    case 'failed':
      return 'text-rose-700'
    case 'processing':
      return 'text-sky-700'
    default:
      return 'text-slate-700'
  }
}

const participantMap = computed(
  () =>
    new Map<string, ChatParticipantRecord>(
      (props.currentRun?.selected_agents ?? []).map((participant) => [participant.id, participant]),
    ),
)

const debateMessages = computed<DebateMessageRecord[]>(() => {
  const ordered = [...(props.currentRun?.events ?? [])].sort((left, right) => left.sequence - right.sequence)
  const byId = new Map<string, DebateMessageRecord>()

  for (const event of ordered) {
    if (event.event_type === 'agent_message_delta') {
      const payload = event.payload as unknown as DeltaPayload
      const existing = byId.get(payload.message_id)
      byId.set(payload.message_id, {
        id: payload.message_id,
        run_id: props.currentRun?.id ?? '',
        role: payload.role,
        source_agent_id: payload.source_agent_id ?? null,
        source_agent_name: payload.source_agent_name ?? null,
        stage: payload.stage ?? null,
        status: 'processing',
        content: `${existing?.content ?? ''}${payload.delta}`,
        citations: existing?.citations ?? [],
        tool_calls: existing?.tool_calls ?? [],
        is_partial: true,
        created_at: existing?.created_at ?? event.created_at,
      })
      continue
    }

    if (event.event_type === 'agent_message_final') {
      const payload = event.payload as unknown as FinalPayload
      byId.set(payload.message.id, {
        ...payload.message,
        is_partial: false,
      })
    }
  }

  return [...byId.values()].sort(
    (left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime(),
  )
})

const debateToolCalls = computed(() => {
  const calls: Array<{ id: string; agentName: string; tool: ToolCallRecord }> = []
  for (const message of debateMessages.value) {
    for (const toolCall of message.tool_calls) {
      calls.push({
        id: `${message.id}-${toolCall.name}`,
        agentName: message.source_agent_name || 'Qurultai',
        tool: toolCall,
      })
    }
  }
  return calls.slice(-6).reverse()
})

const recentEvents = computed(() => [...(props.currentRun?.events ?? [])].slice(-8).reverse())

function labelForEvent(eventType: string) {
  return (
    {
      run_created: 'Run created',
      mode_selected: 'Routing decision',
      retrieval_completed: 'Evidence prepared',
      agent_selected: 'Institution selected',
      agent_started: 'Institution started',
      agent_completed: 'Institution finished',
      critic_started: 'Critic started',
      quality_check_completed: 'Critic finished',
      tool_called: 'Evidence review',
      tool_result: 'Evidence review completed',
      report_ready: 'Report prepared',
      assistant_message_delta: 'Answer streaming',
      assistant_message_completed: 'Answer completed',
      run_status_changed: 'Status updated',
      run_completed: 'Run completed',
      run_failed: 'Run failed',
    }[eventType] || eventType
  )
}

function eventSummary(event: ChatRunRecord['events'][number]) {
  switch (event.event_type) {
    case 'mode_selected':
      return String((event.payload.mode as string | undefined) ?? 'Mode selected')
    case 'retrieval_completed':
      return `${String((event.payload.citation_count as number | undefined) ?? 0)} evidence items ready`
    case 'agent_selected':
    case 'agent_started':
    case 'agent_completed':
      return String(
        (event.payload.participant as { name?: string } | undefined)?.name ||
          (event.payload.summary as string | undefined) ||
          'Institution update',
      )
    case 'tool_result':
    case 'tool_called':
      return String(
        ((event.payload.tool as { output_summary?: string; name?: string } | undefined)?.output_summary ||
          (event.payload.tool as { name?: string } | undefined)?.name ||
          'Evidence review')
      )
    case 'quality_check_completed':
    case 'critic_started':
      return String((event.payload.summary as string | undefined) ?? 'Critic update')
    case 'report_ready':
      return 'HTML and PDF downloads are ready'
    case 'run_status_changed':
    case 'run_completed':
    case 'run_failed':
      return String((event.payload.status as string | undefined) ?? 'Status updated')
    default:
      return String((event.payload.summary as string | undefined) ?? 'Live update')
  }
}

function timestamp(value: string) {
  return new Date(value).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  })
}
</script>

<template>
  <aside class="min-w-0">
    <section class="surface-panel overflow-hidden xl:sticky xl:top-8">
      <div class="border-b border-slate-100 px-6 py-6">
        <div class="space-y-5">
          <div class="flex items-start justify-between gap-4">
            <div class="space-y-3">
              <p class="section-kicker">Decision Room</p>
              <h2 class="font-display text-[clamp(1.9rem,3vw,2.75rem)] leading-[0.98] tracking-tight text-slate-900">
                Institutional debate
              </h2>
              <p class="text-sm leading-7 text-slate-500">
                Review the live institutional discussion, evidence use, and decision posture behind the final answer.
              </p>
            </div>

            <Badge variant="outline">Socket {{ socketState }}</Badge>
          </div>

          <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-1">
            <div class="rounded-3xl border border-slate-100 bg-white/70 p-4">
              <p class="text-xs uppercase tracking-[0.18em] text-slate-400">Current mode</p>
              <p class="mt-3 text-sm font-medium text-slate-900">
                {{ currentRun ? currentRun.mode.replace('_', ' ') : 'Awaiting message' }}
              </p>
            </div>

            <div class="rounded-3xl border border-slate-100 bg-white/70 p-4">
              <p class="text-xs uppercase tracking-[0.18em] text-slate-400">Run status</p>
              <p class="mt-3 text-sm font-medium" :class="statusTone(currentRun?.status)">
                {{ currentRun?.status || 'idle' }}
              </p>
            </div>
          </div>

          <div v-if="currentRun?.selected_agents.length" class="space-y-3">
            <p class="text-sm font-medium text-slate-900">Institutions in the room</p>
            <div class="flex flex-wrap gap-2">
              <Badge
                v-for="participant in currentRun.selected_agents"
                :key="participant.id"
                variant="secondary"
                class="px-4 py-2"
              >
                {{ participant.name }}
              </Badge>
            </div>
          </div>

          <div v-if="currentSession?.documents.length" class="space-y-3">
            <p class="text-sm font-medium text-slate-900">Evidence docket</p>
            <div class="space-y-2">
              <div
                v-for="document in currentSession.documents.slice(0, 4)"
                :key="document.id"
                class="rounded-2xl border border-slate-100 bg-white/80 px-4 py-3"
              >
                <p class="text-sm font-medium text-slate-900">{{ document.name }}</p>
                <p class="mt-1 text-xs text-slate-400">{{ document.mime_type || 'Document' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="max-h-[72vh] overflow-y-auto px-6 py-5">
        <div class="flex items-center justify-between gap-4">
          <p class="text-sm font-medium tracking-tight text-slate-900">Debate feed</p>
          <AppIcon name="workflow" :size="16" />
        </div>

        <Separator class="mt-4" />

        <div class="mt-5 space-y-4">
          <DebateMessage
            v-for="message in debateMessages"
            :key="message.id"
            :message="message"
            :participant="message.source_agent_id ? participantMap.get(message.source_agent_id) : null"
          />

          <div
            v-if="!debateMessages.length && currentRun?.mode === 'direct_answer'"
            class="rounded-3xl border border-dashed border-slate-200 bg-white/70 px-4 py-5 text-sm leading-6 text-slate-500"
          >
            Direct mode keeps the internal process lightweight. Ask for `specialist assist` or `council` when you want a visible institutional debate.
          </div>

          <div
            v-else-if="!debateMessages.length"
            class="rounded-3xl border border-dashed border-slate-200 bg-white/70 px-4 py-5 text-sm leading-6 text-slate-500"
          >
            Send a message to see institutions debate, attach evidence, and converge toward the final answer.
          </div>
        </div>

        <div v-if="debateToolCalls.length" class="mt-8 space-y-3">
          <p class="text-sm font-medium tracking-tight text-slate-900">Evidence operations</p>
          <div class="space-y-2">
            <div
              v-for="item in debateToolCalls"
              :key="item.id"
              class="rounded-2xl border border-slate-100 bg-white/80 px-4 py-3"
            >
              <p class="text-sm font-medium text-slate-900">{{ item.agentName }}</p>
              <p class="mt-1 text-sm leading-6 text-slate-500">
                {{ item.tool.output_summary || `${item.tool.name} · ${item.tool.status}` }}
              </p>
            </div>
          </div>
        </div>

        <div v-if="recentEvents.length" class="mt-8 space-y-3">
          <p class="text-sm font-medium tracking-tight text-slate-900">Timeline</p>
          <div class="space-y-2">
            <div
              v-for="event in recentEvents"
              :key="event.id"
              class="rounded-2xl border border-slate-100 bg-white/75 px-4 py-3"
            >
              <div class="flex items-center justify-between gap-4">
                <p class="text-sm font-medium text-slate-900">{{ labelForEvent(event.event_type) }}</p>
                <span class="text-xs text-slate-400">{{ timestamp(event.created_at) }}</span>
              </div>
              <p class="mt-1 text-sm leading-6 text-slate-500">{{ eventSummary(event) }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </aside>
</template>
