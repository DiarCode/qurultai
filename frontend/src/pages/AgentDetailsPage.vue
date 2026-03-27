<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'

import AgentProfileHeader from '@/components/app/AgentProfileHeader.vue'
import AppIcon from '@/components/app/AppIcon.vue'
import DocumentLibraryPanel from '@/components/app/DocumentLibraryPanel.vue'
import EmptyStateCouncil from '@/components/app/EmptyStateCouncil.vue'
import SkillPickerPanel from '@/components/app/SkillPickerPanel.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { agents, availableSkills } from '@/data/council'

const route = useRoute()

const agent = computed(() => {
  return agents.find((item) => item.id === route.params.id)
})

const editor = reactive({
  role: '',
  description: '',
  systemPrompt: '',
})

const selectedSkills = reactive<string[]>([])

watch(
  agent,
  (value) => {
    if (!value) {
      return
    }

    editor.role = value.role
    editor.description = value.description
    editor.systemPrompt = value.systemPrompt
    selectedSkills.splice(0, selectedSkills.length, ...value.skills.map((skill) => skill.id))
  },
  { immediate: true },
)

const skillModels = computed(() => {
  return availableSkills.filter((skill) => selectedSkills.includes(skill.id))
})

function addSkill(skillId: string) {
  if (selectedSkills.includes(skillId)) {
    return
  }

  selectedSkills.push(skillId)
  const skill = availableSkills.find((item) => item.id === skillId)
  if (skill) {
    toast('Навык подключён', {
      description: skill.name,
    })
  }
}

function removeSkill(skillId: string) {
  const index = selectedSkills.indexOf(skillId)
  if (index >= 0) {
    selectedSkills.splice(index, 1)
  }
}

function saveAgent() {
  toast('Изменения сохранены в демонстрационном режиме', {
    description: agent.value?.name,
  })
}
</script>

<template>
  <section v-if="agent" class="space-y-10">
    <AgentProfileHeader :agent="agent" />

    <Tabs default-value="details">
      <TabsList class="w-full justify-start overflow-x-auto rounded-4xl p-2 md:w-auto">
        <TabsTrigger value="details" class="rounded-full px-5">
          Детали агента
        </TabsTrigger>
        <TabsTrigger value="documents" class="rounded-full px-5">
          Документы и RAG
        </TabsTrigger>
        <TabsTrigger value="skills" class="rounded-full px-5">
          Навыки агента
        </TabsTrigger>
      </TabsList>

      <TabsContent value="details">
        <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
          <!-- Main Form Card -->
          <article class="relative overflow-hidden rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl">
            <div
              class="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/50 via-transparent to-transparent opacity-50"
            />
            <div class="relative p-6 sm:p-8 space-y-6">
              <!-- Role & Status Row -->
              <div class="grid gap-6 md:grid-cols-2">
                <label class="space-y-3">
                  <span class="text-sm font-light tracking-tight text-slate-900">Роль</span>
                  <Input v-model="editor.role" class="rounded-2xl bg-white/90" />
                </label>
                <div class="space-y-3">
                  <span class="text-sm font-light tracking-tight text-slate-900">Статус</span>
                  <div
                    class="rounded-2xl border border-slate-100 bg-slate-50/50 px-5 py-3.5 text-sm font-light text-slate-700"
                  >
                    {{
                      agent.status === 'active'
                        ? 'Активен'
                        : agent.status === 'draft'
                          ? 'Черновик'
                          : 'На паузе'
                    }}
                  </div>
                </div>
              </div>

              <!-- Description -->
              <label class="space-y-3">
                <span class="text-sm font-light tracking-tight text-slate-900">Описание</span>
                <Textarea v-model="editor.description" class="min-h-32 bg-white/90" />
              </label>

              <!-- System Prompt -->
              <label class="space-y-3">
                <span class="text-sm font-light tracking-tight text-slate-900">Системный промпт</span>
                <Textarea v-model="editor.systemPrompt" class="min-h-44 bg-white/90" />
              </label>

              <Separator />

              <!-- Goals & Constraints -->
              <div class="grid gap-6 md:grid-cols-2">
                <div class="space-y-4">
                  <p class="section-kicker">Цели</p>
                  <ul class="space-y-3">
                    <li
                      v-for="goal in agent.goals"
                      :key="goal"
                      class="rounded-2xl border border-slate-100 bg-slate-50/50 px-5 py-4 text-sm font-light leading-7 text-slate-700"
                    >
                      {{ goal }}
                    </li>
                  </ul>
                </div>

                <div class="space-y-4">
                  <p class="section-kicker">Ограничения</p>
                  <ul class="space-y-3">
                    <li
                      v-for="constraint in agent.constraints"
                      :key="constraint"
                      class="rounded-2xl border border-slate-100 bg-slate-50/50 px-5 py-4 text-sm font-light leading-7 text-slate-700"
                    >
                      {{ constraint }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </article>

          <!-- Sidebar Card -->
          <article class="relative overflow-hidden rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl">
            <div
              class="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/50 via-transparent to-transparent opacity-50"
            />
            <div class="relative p-6 sm:p-8 space-y-6">
              <div class="space-y-4">
                <p class="section-kicker">Мета-данные</p>
                <div class="space-y-4">
                  <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5">
                    <p class="text-xs font-light tracking-tight text-slate-400">
                      ID агента
                    </p>
                    <p class="mt-2 text-sm font-light text-slate-700">{{ agent.id }}</p>
                  </div>
                  <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5">
                    <p class="text-xs font-light tracking-tight text-slate-400">Фокус</p>
                    <p class="mt-2 text-sm font-light text-slate-700">{{ agent.focus }}</p>
                  </div>
                  <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5">
                    <p class="text-xs font-light tracking-tight text-slate-400">
                      Подключённые навыки
                    </p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <Badge v-for="skill in skillModels" :key="skill.id" variant="outline">
                        {{ skill.name }}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>

              <Button class="w-full rounded-full" @click="saveAgent">
                <AppIcon name="check" :size="18" />
                Сохранить изменения
              </Button>
            </div>
          </article>
        </div>
      </TabsContent>

      <TabsContent value="documents">
        <DocumentLibraryPanel :documents="agent.documents" />
      </TabsContent>

      <TabsContent value="skills">
        <SkillPickerPanel
          :selected-skills="skillModels"
          :available-skills="availableSkills"
          @add="addSkill"
          @remove="removeSkill"
        />
      </TabsContent>
    </Tabs>
  </section>

  <section v-else class="py-20">
    <EmptyStateCouncil
      icon="agent"
      title="Агент не найден"
      description="Похоже, такого участника совета пока нет в реестре. Вернитесь в галерею агентов и выберите другого."
    />
  </section>
</template>