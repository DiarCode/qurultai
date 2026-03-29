<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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
import { useAgentsStore } from '@/stores/agents'

const route = useRoute()
const router = useRouter()
const agentsStore = useAgentsStore()

const editor = reactive({
  role: '',
  description: '',
  systemPrompt: '',
  goalsText: '',
  constraintsText: '',
  status: 'active',
})

const agent = computed(() => {
  return agentsStore.agents.find((item) => item.id === route.params.id) ?? null
})

watch(
  agent,
  (value) => {
    if (!value) {
      return
    }

    editor.role = value.role
    editor.description = value.description ?? ''
    editor.systemPrompt = value.system_prompt
    editor.goalsText = value.goals.join('\n')
    editor.constraintsText = value.constraints.join('\n')
    editor.status = value.status
  },
  { immediate: true },
)

agentsStore.ensureBootstrap().then(async () => {
  if (typeof route.params.id === 'string') {
    try {
      await agentsStore.fetchAgent(route.params.id)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Не удалось загрузить профиль агента.')
    }
  }
})

async function saveAgent() {
  if (!agent.value) {
    return
  }

  try {
    await agentsStore.updateAgent(agent.value.id, {
      role: editor.role,
      description: editor.description,
      system_prompt: editor.systemPrompt,
      goals: editor.goalsText
        .split('\n')
        .map((item) => item.trim())
        .filter(Boolean),
      constraints: editor.constraintsText
        .split('\n')
        .map((item) => item.trim())
        .filter(Boolean),
      status: editor.status,
    })
    toast.success('Профиль агента обновлён.')
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Не удалось сохранить изменения.')
  }
}

async function removeAgent() {
  if (!agent.value) {
    return
  }

  try {
    await agentsStore.deleteAgent(agent.value.id)
    toast.success('Агент удалён.')
    await router.push('/agents')
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Не удалось удалить агента.')
  }
}

async function handleDocumentUpload(file: File) {
  if (!agent.value) {
    return
  }

  try {
    await agentsStore.uploadAgentDocument(agent.value.id, file)
    toast.success('Документ загружен и привязан к агенту.')
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Не удалось загрузить документ.')
  }
}

async function handleDocumentRemove(documentId: string) {
  if (!agent.value) {
    return
  }

  try {
    await agentsStore.removeAgentDocument(agent.value.id, documentId)
    toast.success('Документ удалён.')
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Не удалось удалить документ.')
  }
}

async function addSkill(skillId: string) {
  if (!agent.value) {
    return
  }

  try {
    await agentsStore.addAgentSkill(agent.value.id, skillId)
    toast.success('Навык подключён.')
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Не удалось подключить навык.')
  }
}

async function removeSkill(skillId: string) {
  if (!agent.value) {
    return
  }

  try {
    await agentsStore.removeAgentSkill(agent.value.id, skillId)
    toast.success('Навык отключён.')
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Не удалось отключить навык.')
  }
}
</script>

<template>
  <section v-if="agent" class="space-y-10">
    <AgentProfileHeader :agent="agent" />

    <Tabs default-value="details">
      <TabsList class="w-full justify-start overflow-x-auto rounded-4xl p-2 md:w-auto">
        <TabsTrigger value="details" class="rounded-full px-5"> Детали агента </TabsTrigger>
        <TabsTrigger value="documents" class="rounded-full px-5"> Документы и RAG </TabsTrigger>
        <TabsTrigger value="skills" class="rounded-full px-5"> Навыки агента </TabsTrigger>
      </TabsList>

      <TabsContent value="details">
        <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
          <article
            class="relative overflow-hidden rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl"
          >
            <div class="relative p-6 sm:p-8 space-y-6">
              <div class="grid gap-6 md:grid-cols-2">
                <label class="space-y-3">
                  <span class="text-sm font-light tracking-tight text-slate-900">Роль</span>
                  <Input v-model="editor.role" class="rounded-2xl bg-white/90" />
                </label>
                <label class="space-y-3">
                  <span class="text-sm font-light tracking-tight text-slate-900">Статус</span>
                  <Input v-model="editor.status" class="rounded-2xl bg-white/90" />
                </label>
              </div>

              <label class="space-y-3">
                <span class="text-sm font-light tracking-tight text-slate-900">Описание</span>
                <Textarea v-model="editor.description" class="min-h-32 bg-white/90" />
              </label>

              <label class="space-y-3">
                <span class="text-sm font-light tracking-tight text-slate-900"
                  >Системный промпт</span
                >
                <Textarea v-model="editor.systemPrompt" class="min-h-44 bg-white/90" />
              </label>

              <Separator />

              <div class="grid gap-6 md:grid-cols-2">
                <label class="space-y-3">
                  <span class="text-sm font-light tracking-tight text-slate-900">Цели</span>
                  <Textarea v-model="editor.goalsText" class="min-h-32 bg-white/90" />
                </label>

                <label class="space-y-3">
                  <span class="text-sm font-light tracking-tight text-slate-900">Ограничения</span>
                  <Textarea v-model="editor.constraintsText" class="min-h-32 bg-white/90" />
                </label>
              </div>
            </div>
          </article>

          <article
            class="relative overflow-hidden rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl"
          >
            <div class="relative p-6 sm:p-8 space-y-6">
              <div class="space-y-4">
                <p class="section-kicker">Мета-данные</p>
                <div class="space-y-4">
                  <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5">
                    <p class="text-xs font-light tracking-tight text-slate-400">ID агента</p>
                    <p class="mt-2 text-sm font-light text-slate-700">{{ agent.id }}</p>
                  </div>
                  <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5">
                    <p class="text-xs font-light tracking-tight text-slate-400">Ключ</p>
                    <p class="mt-2 text-sm font-light text-slate-700">{{ agent.key }}</p>
                  </div>
                  <div class="rounded-2xl border border-slate-100 bg-slate-50/50 p-5">
                    <p class="text-xs font-light tracking-tight text-slate-400">
                      Подключённые навыки
                    </p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <Badge v-for="skill in agent.skills" :key="skill.id" variant="outline">
                        {{ skill.name }}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>

              <Button class="w-full rounded-full" :disabled="agentsStore.saving" @click="saveAgent">
                <AppIcon name="check" :size="18" />
                {{ agentsStore.saving ? 'Сохраняем...' : 'Сохранить изменения' }}
              </Button>
              <Button
                variant="outline"
                class="w-full rounded-full text-rose-600"
                :disabled="agentsStore.saving"
                @click="removeAgent"
              >
                <AppIcon name="cancel" :size="18" />
                Удалить агента
              </Button>
            </div>
          </article>
        </div>
      </TabsContent>

      <TabsContent value="documents">
        <DocumentLibraryPanel
          :documents="agent.documents"
          :uploading="agentsStore.saving"
          removable
          @upload="handleDocumentUpload"
          @remove="handleDocumentRemove"
        />
      </TabsContent>

      <TabsContent value="skills">
        <SkillPickerPanel
          :selected-skills="agent.skills"
          :available-skills="agentsStore.skills"
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
