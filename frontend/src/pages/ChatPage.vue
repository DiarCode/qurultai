<script setup lang="ts">
import ChatWorkspace from '@/components/app/ChatWorkspace.vue'
import DebatePanel from '@/components/app/DebatePanel.vue'
import { agents, chatMessages, debateMessages, exportOptions, finalSummary } from '@/data/council'

function focusDebatePanel() {
  document.getElementById('debate-panel')?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}
</script>

<template>
  <section
    class="grid gap-6 xl:grid-cols-[minmax(0,1.22fr)_minmax(24rem,0.92fr)] 2xl:grid-cols-[minmax(0,1.3fr)_minmax(28rem,0.9fr)]"
  >
    <div class="min-w-0">
      <ChatWorkspace
        :messages="chatMessages"
        :exports="exportOptions"
        :summary="finalSummary"
        @open-debate="focusDebatePanel"
      />
    </div>

    <DebatePanel :agents="agents" :messages="debateMessages" :request="chatMessages[0]!" />
  </section>
</template>
