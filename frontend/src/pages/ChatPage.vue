<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

import ChatWorkspace from '@/components/app/ChatWorkspace.vue'
import DebatePanel from '@/components/app/DebatePanel.vue'
import { useChatWorkspace } from '@/composables/useChatWorkspace'
import type { ChatModePreference } from '@/types/chat'

const route = useRoute()
const router = useRouter()
const {
  sessions,
  currentSession,
  currentRun,
  sending,
  socketState,
  error,
  fetchSessions,
  loadSession,
  createSession,
  sendMessage,
} = useChatWorkspace()

onMounted(async () => {
  try {
    const sessionList = await fetchSessions()
    const requestedSessionId = typeof route.query.session === 'string' ? route.query.session : null
    const nextSessionId = requestedSessionId || sessionList[0]?.id || null
    if (nextSessionId) {
      await loadSession(nextSessionId)
    }
  } catch (cause) {
    toast.error(cause instanceof Error ? cause.message : 'Failed to initialize the chat workspace.')
  }
})

watch(
  () => currentSession.value?.id,
  (sessionId) => {
    router.replace({
      query: {
        ...route.query,
        session: sessionId,
      },
    })
  },
)

async function handleCreateSession() {
  try {
    const session = await createSession()
    await loadSession(session.id)
    toast.success('New chat ready.')
  } catch (cause) {
    toast.error(cause instanceof Error ? cause.message : 'Failed to create a new chat.')
  }
}

async function handleSelectSession(sessionId: string) {
  try {
    await loadSession(sessionId)
  } catch (cause) {
    toast.error(cause instanceof Error ? cause.message : 'Failed to open the selected chat.')
  }
}

async function handleSubmit(payload: {
  content: string
  files: File[]
  modePreference: ChatModePreference
}) {
  try {
    await sendMessage(payload.content, payload.files, payload.modePreference)
  } catch (cause) {
    toast.error(cause instanceof Error ? cause.message : 'Failed to send the message.')
  }
}
</script>

<template>
  <section class="grid gap-6 xl:grid-cols-[minmax(0,1.34fr)_minmax(22rem,0.8fr)]">
    <div class="min-w-0">
      <ChatWorkspace
        :sessions="sessions"
        :current-session="currentSession"
        :current-run="currentRun"
        :sending="sending"
        :socket-state="socketState"
        :error="error"
        @create-session="handleCreateSession"
        @select-session="handleSelectSession"
        @submit="handleSubmit"
      />
    </div>

    <DebatePanel :current-session="currentSession" :current-run="currentRun" :socket-state="socketState" />
  </section>
</template>
