<script setup lang="ts">
import { ref } from 'vue'

import AgentCard from '@/components/app/AgentCard.vue'
import AppIcon from '@/components/app/AppIcon.vue'
import CreateAgentDialog from '@/components/app/CreateAgentDialog.vue'
import SectionHeading from '@/components/app/SectionHeading.vue'
import { Button } from '@/components/ui/button'
import { agents } from '@/data/council'

const dialogOpen = ref(false)
</script>

<template>
  <section class="space-y-10">
    <!-- Header -->
    <div class="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
      <SectionHeading
        eyebrow="Круг участников"
        title="Агенты совета"
        description="Каждый агент оформлен как отдельный участник Qurultai: со своей специализацией, документами, навыками и ролью в общем deliberation-контуре."
      />
      <Button class="rounded-full px-6" @click="dialogOpen = true">
        <AppIcon name="addCircle" :size="18" />
        Добавить агента
      </Button>
    </div>

    <!-- Agent Grid -->
    <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      <!-- Create Agent Card -->
      <button type="button" class="group text-left" @click="dialogOpen = true">
        <article
          class="relative h-full overflow-hidden rounded-4xl border border-dashed border-slate-200 bg-slate-50/50 backdrop-blur-sm transition-all duration-700 group-hover:-translate-y-1.5 group-hover:border-slate-300"
        >
          <div class="flex h-full flex-col items-center justify-center gap-5 py-12 text-center">
            <div class="ornament-ring flex size-16 items-center justify-center text-slate-400">
              <AppIcon name="addCircle" :size="26" />
            </div>
            <div class="space-y-3">
              <h2 class="text-lg font-light tracking-tight text-slate-900">
                Создать агента
              </h2>
              <p class="text-sm font-light leading-6 text-slate-500 max-w-xs">
                Добавьте нового участника совета с собственной ролью, целями и ограничениями.
              </p>
            </div>
          </div>
        </article>
      </button>

      <!-- Agent Cards -->
      <AgentCard v-for="agent in agents" :key="agent.id" :agent="agent" />
    </div>

    <CreateAgentDialog :open="dialogOpen" @update:open="dialogOpen = $event" />
  </section>
</template>