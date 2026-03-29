import { computed, onBeforeUnmount, ref } from 'vue'

import { apiRequest, buildWebSocketUrl } from '@/lib/api'
import type {
  CitationRecord,
  RunCreateResponse,
  RunEvent,
  RunMessage,
  RunParticipant,
  RunRecord,
  RunReport,
} from '@/types/council'

interface DeltaPayload {
  message_id: string
  role: string
  source_agent_id?: string | null
  source_agent_name?: string | null
  stage?: string | null
  delta: string
}

interface FinalPayload {
  message: RunMessage
}

interface ParticipantPayload {
  participant: RunParticipant
}

interface StatusPayload {
  status: RunRecord['status']
}

interface ReportPayload {
  report: RunReport
}

export function useCouncilRun() {
  const run = ref<RunRecord | null>(null)
  const connecting = ref(false)
  const submitting = ref(false)
  const error = ref<string | null>(null)
  const socketState = ref<'idle' | 'connecting' | 'open' | 'closed'>('idle')

  let socket: WebSocket | null = null

  function sortMessages() {
    if (!run.value) {
      return
    }

    run.value.messages = [...run.value.messages].sort((left, right) => {
      return new Date(left.created_at).getTime() - new Date(right.created_at).getTime()
    })
  }

  function upsertMessage(message: RunMessage) {
    if (!run.value) {
      return
    }

    const index = run.value.messages.findIndex((item) => item.id === message.id)
    if (index >= 0) {
      run.value.messages[index] = message
    } else {
      run.value.messages.push(message)
    }
    sortMessages()
  }

  function upsertParticipant(participant: RunParticipant) {
    if (!run.value) {
      return
    }

    const index = run.value.participants.findIndex((item) => item.id === participant.id)
    if (index >= 0) {
      run.value.participants[index] = participant
      return
    }
    run.value.participants.push(participant)
  }

  function appendEvent(event: RunEvent) {
    if (!run.value) {
      return
    }

    if (run.value.events.some((item) => item.id === event.id)) {
      return
    }

    run.value.events.push(event)
    run.value.events.sort((left, right) => left.sequence - right.sequence)
  }

  function handleEvent(event: RunEvent) {
    appendEvent(event)

    if (!run.value) {
      return
    }

    switch (event.event_type) {
      case 'run_status_changed': {
        const payload = event.payload as unknown as StatusPayload
        run.value.status = payload.status
        break
      }
      case 'agent_selected': {
        const payload = event.payload as unknown as ParticipantPayload
        upsertParticipant(payload.participant)
        break
      }
      case 'agent_message_delta': {
        const payload = event.payload as unknown as DeltaPayload
        const existing = run.value.messages.find((item) => item.id === payload.message_id)
        const nextMessage: RunMessage = existing ?? {
          id: payload.message_id,
          run_id: run.value.id,
          role: payload.role,
          source_agent_id: payload.source_agent_id ?? null,
          source_agent_name: payload.source_agent_name ?? null,
          stage: payload.stage ?? null,
          status: 'streaming',
          content: '',
          citations: [] as CitationRecord[],
          tool_calls: [],
          is_partial: true,
          created_at: new Date().toISOString(),
        }
        nextMessage.content += payload.delta
        nextMessage.is_partial = true
        upsertMessage(nextMessage)
        break
      }
      case 'agent_message_final': {
        const payload = event.payload as unknown as FinalPayload
        upsertMessage({
          ...payload.message,
          is_partial: false,
        })
        break
      }
      case 'final_report_ready': {
        const payload = event.payload as unknown as ReportPayload
        run.value.final_report = payload.report
        break
      }
      default:
        break
    }
  }

  function closeSocket() {
    socket?.close()
    socket = null
    socketState.value = 'closed'
  }

  async function loadRun(runId: string) {
    connecting.value = true
    error.value = null
    try {
      run.value = await apiRequest<RunRecord>(`/runs/${runId}`)
      if (run.value.status === 'queued' || run.value.status === 'processing') {
        connectToRun(runId)
      }
      return run.value
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить запуск.'
      throw cause
    } finally {
      connecting.value = false
    }
  }

  async function createRun(prompt: string, files: File[]) {
    submitting.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.set('prompt', prompt)
      for (const file of files) {
        formData.append('files', file)
      }
      const response = await apiRequest<RunCreateResponse>('/runs', {
        method: 'POST',
        body: formData,
      })
      await loadRun(response.run_id)
      connectToRun(response.run_id)
      return response.run_id
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Не удалось запустить совет.'
      throw cause
    } finally {
      submitting.value = false
    }
  }

  function connectToRun(runId: string) {
    if (socket && run.value?.id === runId && socket.readyState <= WebSocket.OPEN) {
      return
    }

    closeSocket()
    socketState.value = 'connecting'
    socket = new WebSocket(buildWebSocketUrl(`/runs/${runId}/events/ws`))

    socket.addEventListener('open', () => {
      socketState.value = 'open'
    })

    socket.addEventListener('message', (messageEvent) => {
      const payload = JSON.parse(messageEvent.data) as RunEvent | { event_type: 'connection_ready' }
      if (payload.event_type === 'connection_ready') {
        return
      }
      handleEvent(payload as RunEvent)
    })

    socket.addEventListener('close', () => {
      socketState.value = 'closed'
    })

    socket.addEventListener('error', () => {
      socketState.value = 'closed'
    })
  }

  const recentEvents = computed(() => run.value?.events.slice(-12) ?? [])
  const participantMap = computed(
    () => new Map((run.value?.participants ?? []).map((item) => [item.id, item])),
  )

  onBeforeUnmount(() => {
    closeSocket()
  })

  return {
    run,
    connecting,
    submitting,
    error,
    socketState,
    participantMap,
    recentEvents,
    loadRun,
    createRun,
    connectToRun,
    closeSocket,
  }
}
