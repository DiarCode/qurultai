<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { toast } from 'vue-sonner'

import AgentCard from '@/components/app/AgentCard.vue'
import AppIcon from '@/components/app/AppIcon.vue'
import CreateAgentDialog from '@/components/app/CreateAgentDialog.vue'
import EmptyStateCouncil from '@/components/app/EmptyStateCouncil.vue'
import SectionHeading from '@/components/app/SectionHeading.vue'
import { Button } from '@/components/ui/button'
import { useAgentsStore } from '@/stores/agents'

const agentsStore = useAgentsStore()
const dialogOpen = ref(false)

onMounted(() => {
  agentsStore.ensureBootstrap().catch((error: unknown) => {
    toast.error(error instanceof Error ? error.message : 'Не удалось загрузить реестр агентов.')
  })
})

async function handleCreateAgent(payload: {
  name: string
  role: string
  description: string
  system_prompt: string
  goals: string[]
  constraints: string[]
  status: string
}) {
  try {
    await agentsStore.createAgent(payload)
    dialogOpen.value = false
    toast.success('Агент добавлен в реестр совета.')
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Не удалось создать агента.')
  }
}
</script>

<template>
  <section class="space-y-10">
    <div class="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
      <SectionHeading
        eyebrow="Круг участников"
        title="Агенты совета"
        description="Каждый агент теперь загружается из реестра backend: со своей ролью, документами, навыками и реальным статусом."
      />
      <Button class="rounded-full px-6" @click="dialogOpen = true">
        <AppIcon name="addCircle" :size="18" />
        Добавить агента
      </Button>
    </div>

    <div v-if="agentsStore.loading" class="surface-panel p-8 text-sm font-light text-slate-500">
      Загружаем реестр агентов...
    </div>

    <EmptyStateCouncil
      v-else-if="agentsStore.error"
      icon="alert"
      title="Не удалось загрузить агентов"
      :description="agentsStore.error"
      action-label="Повторить"
      @action="agentsStore.fetchAgents()"
    />

    <div v-else class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      <button type="button" class="group text-left" @click="dialogOpen = true">
        <article
          class="relative h-full overflow-hidden rounded-4xl border border-dashed border-slate-200 bg-slate-50/50 backdrop-blur-sm transition-all duration-700 group-hover:-translate-y-1.5 group-hover:border-slate-300"
        >
          <div class="flex h-full flex-col items-center justify-center gap-5 py-12 text-center">
            <div class="ornament-ring flex size-16 items-center justify-center text-slate-400">
              <AppIcon name="addCircle" :size="26" />
            </div>
            <div class="space-y-3">
              <h2 class="text-lg font-light tracking-tight text-slate-900">Создать агента</h2>
              <p class="text-sm font-light leading-6 text-slate-500 max-w-xs">
                Добавьте нового участника совета с собственной ролью, документами и навыками.
              </p>
            </div>
          </div>
        </article>
      </button>

      <AgentCard v-for="agent in agentsStore.agents" :key="agent.id" :agent="agent" />
    </div>

    <CreateAgentDialog
      :open="dialogOpen"
      :saving="agentsStore.saving"
      @update:open="dialogOpen = $event"
      @submit="handleCreateAgent"
    />
  </section>
</template>
