<script setup lang="ts">
import { computed, ref } from 'vue'
import { toast } from 'vue-sonner'

import type { SkillRecord } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
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
  selectedSkills: SkillRecord[]
  availableSkills: SkillRecord[]
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

function removeSkill(skill: SkillRecord) {
  emit('remove', skill.id)
  toast('Навык отключён от агента', {
    description: skill.name,
  })
}
</script>

<template>
  <div class="space-y-6">
    <div
      class="surface-panel flex flex-col gap-5 p-6 md:flex-row md:items-center md:justify-between"
    >
      <div class="space-y-3">
        <p class="section-kicker">Навыки агента</p>
        <p class="text-sm font-light leading-7 text-slate-500">
          Подключайте способности выборочно: аудит ссылок, сценарный анализ, сравнение норм и
          подготовку итоговых брифов.
        </p>
      </div>
      <div class="flex flex-col gap-3 sm:flex-row">
        <Select v-model="selectedSkillId">
          <SelectTrigger class="min-w-64 rounded-full bg-white/90">
            <SelectValue placeholder="Выберите навык" />
          </SelectTrigger>
          <SelectContent class="rounded-2xl border-slate-100 bg-white/95 backdrop-blur-xl">
            <SelectItem v-for="skill in missingSkills" :key="skill.id" :value="skill.id">
              {{ skill.name }}
            </SelectItem>
          </SelectContent>
        </Select>
        <Button class="rounded-full px-6" :disabled="!selectedSkillId" @click="addSkill">
          <AppIcon name="addCircle" :size="18" />
          Добавить навык
        </Button>
      </div>
    </div>

    <div v-if="selectedSkills.length" class="grid gap-5 md:grid-cols-2">
      <article
        v-for="skill in selectedSkills"
        :key="skill.id"
        class="relative overflow-hidden rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl"
      >
        <div
          class="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/50 via-transparent to-transparent opacity-50"
        />
        <div class="relative flex h-full flex-col gap-5 p-6">
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-4">
              <div class="ornament-ring flex size-12 items-center justify-center text-slate-900">
                <AppIcon name="workflow" :size="18" />
              </div>
              <div>
                <h3 class="text-base font-light tracking-tight text-slate-900">
                  {{ skill.name }}
                </h3>
                <p class="mt-1 text-xs font-light tracking-tight text-slate-400">
                  {{ skill.key }}
                </p>
              </div>
            </div>
            <Button variant="ghost" size="icon-sm" class="rounded-full" @click="removeSkill(skill)">
              <AppIcon name="cancel" :size="16" />
            </Button>
          </div>
          <p class="text-sm font-light leading-7 text-slate-500">
            {{ skill.description }}
          </p>
          <div class="mt-auto flex items-center gap-2">
            <Badge variant="outline">Подключён</Badge>
          </div>
        </div>
      </article>
    </div>

    <EmptyStateCouncil
      v-else
      icon="sparkles"
      title="Навыки ещё не выбраны"
      description="Добавьте хотя бы один навык, чтобы агент получил специализированный способ анализа и участия в совете."
    />
  </div>
</template>
