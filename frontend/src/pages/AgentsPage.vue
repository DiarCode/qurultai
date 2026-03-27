<script setup lang="ts">
import { ref } from 'vue'

import AgentCard from '@/components/app/AgentCard.vue'
import AppIcon from '@/components/app/AppIcon.vue'
import CreateAgentDialog from '@/components/app/CreateAgentDialog.vue'
import SectionHeading from '@/components/app/SectionHeading.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { agents } from '@/data/council'

const dialogOpen = ref(false)
</script>

<template>
  <section class="space-y-8">
    <div class="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
      <SectionHeading
        eyebrow="Круг участников"
        title="Агенты совета"
        description="Каждый агент оформлен как отдельный участник Qurultai: со своей специализацией, документами, навыками и ролью в общем deliberation-контуре."
      />
      <Button class="rounded-full px-5" @click="dialogOpen = true">
        <AppIcon name="addCircle" :size="18" />
        Добавить агента
      </Button>
    </div>

    <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      <button type="button" class="group text-left" @click="dialogOpen = true">
        <Card
          class="h-full border-dashed transition-all duration-300 group-hover:-translate-y-1 group-hover:border-primary/35"
        >
          <CardContent
            class="flex h-full flex-col items-center justify-center gap-4 py-12 text-center"
          >
            <div class="ornament-ring flex size-16 items-center justify-center text-primary">
              <AppIcon name="addCircle" :size="26" />
            </div>
            <div class="space-y-2">
              <h2 class="text-lg font-medium text-foreground">Создать агента</h2>
              <p class="text-sm leading-7 text-muted-foreground">
                Добавьте нового участника совета с собственной ролью, целями и ограничениями.
              </p>
            </div>
          </CardContent>
        </Card>
      </button>

      <AgentCard v-for="agent in agents" :key="agent.id" :agent="agent" />
    </div>

    <CreateAgentDialog :open="dialogOpen" @update:open="dialogOpen = $event" />
  </section>
</template>
