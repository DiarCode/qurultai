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
import { Card, CardContent } from '@/components/ui/card'
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
  <section v-if="agent" class="space-y-8">
    <AgentProfileHeader :agent="agent" />

    <Tabs default-value="details">
      <TabsList class="w-full justify-start overflow-x-auto rounded-[2rem] p-2 md:w-auto">
        <TabsTrigger value="details" class="rounded-full px-4"> Детали агента </TabsTrigger>
        <TabsTrigger value="documents" class="rounded-full px-4"> Документы и RAG </TabsTrigger>
        <TabsTrigger value="skills" class="rounded-full px-4"> Навыки агента </TabsTrigger>
      </TabsList>

      <TabsContent value="details">
        <div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
          <Card class="rounded-[2rem] border-border/80 bg-card/88">
            <CardContent class="grid gap-5 pt-6">
              <div class="grid gap-5 md:grid-cols-2">
                <label class="space-y-2">
                  <span class="text-sm font-medium text-foreground">Роль</span>
                  <Input v-model="editor.role" class="rounded-2xl bg-background/90" />
                </label>
                <div class="space-y-2">
                  <span class="text-sm font-medium text-foreground">Статус</span>
                  <div
                    class="rounded-2xl border border-border/70 bg-[color:var(--surface-muted)] px-4 py-3 text-sm text-foreground"
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

              <label class="space-y-2">
                <span class="text-sm font-medium text-foreground">Описание</span>
                <Textarea v-model="editor.description" class="min-h-28 bg-background/90" />
              </label>

              <label class="space-y-2">
                <span class="text-sm font-medium text-foreground">Системный промпт</span>
                <Textarea v-model="editor.systemPrompt" class="min-h-40 bg-background/90" />
              </label>

              <Separator />

              <div class="grid gap-5 md:grid-cols-2">
                <div class="space-y-3">
                  <p class="section-kicker">Цели</p>
                  <ul class="space-y-2">
                    <li
                      v-for="goal in agent.goals"
                      :key="goal"
                      class="rounded-[1.25rem] border border-border/70 bg-[color:var(--surface-muted)] px-4 py-3 text-sm leading-7 text-foreground"
                    >
                      {{ goal }}
                    </li>
                  </ul>
                </div>

                <div class="space-y-3">
                  <p class="section-kicker">Ограничения</p>
                  <ul class="space-y-2">
                    <li
                      v-for="constraint in agent.constraints"
                      :key="constraint"
                      class="rounded-[1.25rem] border border-border/70 bg-[color:var(--surface-muted)] px-4 py-3 text-sm leading-7 text-foreground"
                    >
                      {{ constraint }}
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card class="rounded-[2rem] border-border/80 bg-card/88">
            <CardContent class="space-y-5 pt-6">
              <div class="space-y-3">
                <p class="section-kicker">Мета-данные</p>
                <div class="space-y-3">
                  <div
                    class="rounded-[1.5rem] border border-border/70 bg-[color:var(--surface-muted)] p-4"
                  >
                    <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                      ID агента
                    </p>
                    <p class="mt-2 text-sm text-foreground">{{ agent.id }}</p>
                  </div>
                  <div
                    class="rounded-[1.5rem] border border-border/70 bg-[color:var(--surface-muted)] p-4"
                  >
                    <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Фокус</p>
                    <p class="mt-2 text-sm text-foreground">{{ agent.focus }}</p>
                  </div>
                  <div
                    class="rounded-[1.5rem] border border-border/70 bg-[color:var(--surface-muted)] p-4"
                  >
                    <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">
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
            </CardContent>
          </Card>
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

  <section v-else class="py-16">
    <EmptyStateCouncil
      icon="agent"
      title="Агент не найден"
      description="Похоже, такого участника совета пока нет в реестре. Вернитесь в галерею агентов и выберите другого."
    />
  </section>
</template>
