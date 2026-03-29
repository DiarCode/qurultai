import { computed, onBeforeUnmount, ref } from 'vue'

import { apiRequest, buildWebSocketUrl } from '@/lib/api'
import type {
  ChatModePreference,
  ChatMessageRecord,
  ChatRunEventRecord,
  ChatRunRecord,
  ChatSendMessageResponse,
  ChatSessionCreateResponse,
  ChatSessionListResponse,
  ChatSessionRecord,
  ChatSessionSummaryRecord,
} from '@/types/chat'

interface MessageDeltaPayload {
  message_id: string
  delta: string
}

interface MessageCompletedPayload {
  message: ChatMessageRecord
}

interface StatusPayload {
  status: ChatRunRecord['status']
}

interface ModePayload {
  mode: ChatRunRecord['mode']
  selected_agents: ChatRunRecord['selected_agents']
}

interface ReportReadyPayload {
  markdown_url?: string
  html_url?: string
  pdf_url?: string
}

export function useChatWorkspace() {
  const sessions = ref<ChatSessionSummaryRecord[]>([])
  const currentSession = ref<ChatSessionRecord | null>(null)
  const currentRun = ref<ChatRunRecord | null>(null)
  const loading = ref(false)
  const sending = ref(false)
  const error = ref<string | null>(null)
  const socketState = ref<'idle' | 'connecting' | 'open' | 'closed'>('idle')

  let socket: WebSocket | null = null

  function sortMessages() {
    if (!currentSession.value) {
      return
    }
    currentSession.value.messages = [...currentSession.value.messages].sort(
      (left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime(),
    )
  }

  function upsertSessionSummary(summary: ChatSessionSummaryRecord) {
    const index = sessions.value.findIndex((item) => item.id === summary.id)
    if (index >= 0) {
      sessions.value[index] = summary
    } else {
      sessions.value.unshift(summary)
    }
    sessions.value = [...sessions.value].sort(
      (left, right) => new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime(),
    )
  }

  function upsertMessage(message: ChatMessageRecord) {
    if (!currentSession.value) {
      return
    }
    const index = currentSession.value.messages.findIndex((item) => item.id === message.id)
    if (index >= 0) {
      currentSession.value.messages[index] = message
    } else {
      currentSession.value.messages.push(message)
    }
    sortMessages()
  }

  function appendRunEvent(event: ChatRunEventRecord) {
    if (!currentRun.value) {
      return
    }
    if (currentRun.value.events.some((item) => item.id === event.id)) {
      return
    }
    currentRun.value.events.push(event)
    currentRun.value.events.sort((left, right) => left.sequence - right.sequence)
  }

  function refreshCurrentRun(run: ChatRunRecord) {
    currentRun.value = run
    if (!currentSession.value) {
      return
    }
    const index = currentSession.value.runs.findIndex((item) => item.id === run.id)
    if (index >= 0) {
      currentSession.value.runs[index] = run
    } else {
      currentSession.value.runs.push(run)
    }
  }

  function closeSocket() {
    socket?.close()
    socket = null
    socketState.value = 'closed'
  }

  async function fetchSessions() {
    const response = await apiRequest<ChatSessionListResponse>('/chat/sessions')
    sessions.value = response.items
    return sessions.value
  }

  async function loadSession(sessionId: string) {
    loading.value = true
    error.value = null
    try {
      currentSession.value = await apiRequest<ChatSessionRecord>(`/chat/sessions/${sessionId}`)
      upsertSessionSummary({
        id: currentSession.value.id,
        title: currentSession.value.title,
        created_at: currentSession.value.created_at,
        updated_at: currentSession.value.updated_at,
        status: currentSession.value.status,
        last_message_preview: currentSession.value.last_message_preview,
      })

      const latestRun = [...currentSession.value.runs].sort(
        (left, right) =>
          new Date(right.started_at ?? right.finished_at ?? 0).getTime() -
          new Date(left.started_at ?? left.finished_at ?? 0).getTime(),
      )[0]

      currentRun.value = latestRun ?? null
      if (latestRun && ['queued', 'processing'].includes(latestRun.status)) {
        connectToRun(latestRun.id)
      } else {
        closeSocket()
      }
      return currentSession.value
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Failed to load the conversation.'
      throw cause
    } finally {
      loading.value = false
    }
  }

  async function createSession(title?: string) {
    error.value = null
    const response = await apiRequest<ChatSessionCreateResponse>('/chat/sessions', {
      method: 'POST',
      body: JSON.stringify({ title: title ?? null }),
    })
    upsertSessionSummary(response.session)
    await loadSession(response.session.id)
    return response.session
  }

  async function sendMessage(content: string, files: File[], modePreference: ChatModePreference) {
    if (!currentSession.value) {
      await createSession()
    }

    if (!currentSession.value) {
      throw new Error('No session is selected.')
    }

    sending.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.set('content', content)
      formData.set('mode_preference', modePreference)
      for (const file of files) {
        formData.append('files', file)
      }

      const response = await apiRequest<ChatSendMessageResponse>(
        `/chat/sessions/${currentSession.value.id}/messages`,
        {
          method: 'POST',
          body: formData,
        },
      )

      currentSession.value = response.session
      refreshCurrentRun(response.run)
      upsertSessionSummary({
        id: response.session.id,
        title: response.session.title,
        created_at: response.session.created_at,
        updated_at: response.session.updated_at,
        status: response.session.status,
        last_message_preview: response.session.last_message_preview,
      })
      connectToRun(response.run.id)
      return response
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Failed to send the message.'
      throw cause
    } finally {
      sending.value = false
    }
  }

  function handleEvent(event: ChatRunEventRecord) {
    appendRunEvent(event)

    if (!currentRun.value || !currentSession.value) {
      return
    }

    switch (event.event_type) {
      case 'run_status_changed': {
        const payload = event.payload as unknown as StatusPayload
        currentRun.value.status = payload.status
        break
      }
      case 'mode_selected': {
        const payload = event.payload as unknown as ModePayload
        currentRun.value.mode = payload.mode
        currentRun.value.selected_agents = payload.selected_agents
        break
      }
      case 'assistant_message_delta': {
        const payload = event.payload as unknown as MessageDeltaPayload
        const existing = currentSession.value.messages.find((item) => item.id === payload.message_id)
        if (!existing) {
          break
        }
        existing.content += payload.delta
        existing.status = 'processing'
        upsertMessage({ ...existing })
        break
      }
      case 'assistant_message_completed': {
        const payload = event.payload as unknown as MessageCompletedPayload
        upsertMessage(payload.message)
        currentRun.value.output_message_id = payload.message.id
        currentRun.value.status = 'completed'
        currentSession.value.last_message_preview = payload.message.content.slice(0, 180)
        upsertSessionSummary({
          id: currentSession.value.id,
          title: currentSession.value.title,
          created_at: currentSession.value.created_at,
          updated_at: new Date().toISOString(),
          status: currentSession.value.status,
          last_message_preview: currentSession.value.last_message_preview,
        })
        break
      }
      case 'report_ready': {
        const _payload = event.payload as unknown as ReportReadyPayload
        break
      }
      default:
        break
    }
  }

  function connectToRun(runId: string) {
    if (socket && currentRun.value?.id === runId && socket.readyState <= WebSocket.OPEN) {
      return
    }

    closeSocket()
    socketState.value = 'connecting'
    socket = new WebSocket(buildWebSocketUrl(`/chat/runs/${runId}/events/ws`))

    socket.addEventListener('open', () => {
      socketState.value = 'open'
    })

    socket.addEventListener('message', (messageEvent) => {
      const payload = JSON.parse(messageEvent.data) as
        | ChatRunEventRecord
        | { event_type: 'connection_ready'; payload: { run_id: string } }
      if (payload.event_type === 'connection_ready') {
        return
      }
      handleEvent(payload as ChatRunEventRecord)
    })

    socket.addEventListener('close', () => {
      socketState.value = 'closed'
    })

    socket.addEventListener('error', () => {
      socketState.value = 'closed'
    })
  }

  const currentMessages = computed(() => currentSession.value?.messages ?? [])
  const currentDocuments = computed(() => currentSession.value?.documents ?? [])
  const currentEvents = computed(() => currentRun.value?.events ?? [])

  onBeforeUnmount(() => {
    closeSocket()
  })

  return {
    sessions,
    currentSession,
    currentRun,
    currentMessages,
    currentDocuments,
    currentEvents,
    loading,
    sending,
    error,
    socketState,
    fetchSessions,
    loadSession,
    createSession,
    sendMessage,
    connectToRun,
    closeSocket,
  }
}
