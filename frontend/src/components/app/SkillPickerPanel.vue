<script setup lang="ts">
import { computed, ref } from 'vue'
import { toast } from 'vue-sonner'

import type { AgentSkill } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import AppIcon from './AppIcon.vue'
import EmptyStateCouncil from './EmptyStateCouncil.vue'

const props = defineProps<{
  selectedSkills: AgentSkill[]
  availableSkills: AgentSkill[]
}>()

const emit = defineEmits<{
  add: [skillId: string]
  remove: [skillId: string]
}>()

const selectedSkillId = ref<string>()

const missingSkills = computed(() => {
  const selectedIds = new Set(props.selectedSkills.map((skill) => skill.id))
  return props.availableSkills.filter((skill) => !selectedIds.has(skill.id))
})

function addSkill() {
  if (!selectedSkillId.value) {
    return
  }

  emit('add', selectedSkillId.value)
  selectedSkillId.value = undefined
}

function removeSkill(skill: AgentSkill) {
  emit('remove', skill.id)
  toast('Навык отключён от агента', {
    description: skill.name,
  })
}
</script>

<template>
  <div class="space-y-5">
    <div
      class="surface-panel flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between"
    >
      <div class="space-y-2">
        <p class="section-kicker">Навыки агента</p>
        <p class="text-sm leading-7 text-muted-foreground">
          Подключайте способности выборочно: аудит ссылок, сценарный анализ, сравнение норм и
          подготовку итоговых брифов.
        </p>
      </div>
      <div class="flex flex-col gap-3 sm:flex-row">
        <Select v-model="selectedSkillId">
          <SelectTrigger class="min-w-64 rounded-full bg-background/90">
            <SelectValue placeholder="Выберите навык" />
          </SelectTrigger>
          <SelectContent class="rounded-2xl border-border/80 bg-background/95">
            <SelectItem v-for="skill in missingSkills" :key="skill.id" :value="skill.id">
              {{ skill.name }}
            </SelectItem>
          </SelectContent>
        </Select>
        <Button class="rounded-full px-5" :disabled="!selectedSkillId" @click="addSkill">
          <AppIcon name="addCircle" :size="18" />
          Добавить навык
        </Button>
      </div>
    </div>

    <div v-if="selectedSkills.length" class="grid gap-4 md:grid-cols-2">
      <Card
        v-for="skill in selectedSkills"
        :key="skill.id"
        class="rounded-[2rem] border-border/80 bg-card/88"
      >
        <CardContent class="flex h-full flex-col gap-4 pt-6">
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-3">
              <div class="ornament-ring flex size-11 items-center justify-center text-primary">
                <AppIcon name="workflow" :size="18" />
              </div>
              <div>
                <h3 class="text-base font-medium text-foreground">
                  {{ skill.name }}
                </h3>
                <p class="mt-1 text-xs uppercase tracking-[0.2em] text-muted-foreground">
                  {{ skill.category }}
                </p>
              </div>
            </div>
            <Button variant="ghost" size="icon-sm" class="rounded-full" @click="removeSkill(skill)">
              <AppIcon name="cancel" :size="16" />
            </Button>
          </div>
          <p class="text-sm leading-7 text-muted-foreground">
            {{ skill.description }}
          </p>
          <div class="mt-auto flex items-center gap-2">
            <Badge variant="outline">Подключён</Badge>
          </div>
        </CardContent>
      </Card>
    </div>

    <EmptyStateCouncil
      v-else
      icon="sparkles"
      title="Навыки ещё не выбраны"
      description="Добавьте хотя бы один навык, чтобы агент получил специализированный способ анализа и участия в совете."
    />
  </div>
</template>
