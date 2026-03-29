<script setup lang="ts">
import { reactive, watch } from 'vue'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

import AppIcon from './AppIcon.vue'

const props = defineProps<{
  open: boolean
  saving?: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  submit: [
    payload: {
      name: string
      role: string
      description: string
      system_prompt: string
      goals: string[]
      constraints: string[]
      status: string
    },
  ]
}>()

const initialState = () => ({
  name: '',
  role: '',
  description: '',
  systemPrompt: '',
  goals: '',
  constraints: '',
  status: 'active',
})

const form = reactive(initialState())

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      Object.assign(form, initialState())
    }
  },
)

function submit() {
  emit('submit', {
    name: form.name.trim(),
    role: form.role.trim(),
    description: form.description.trim(),
    system_prompt: form.systemPrompt.trim(),
    goals: form.goals
      .split('\n')
      .map((item) => item.trim())
      .filter(Boolean),
    constraints: form.constraints
      .split('\n')
      .map((item) => item.trim())
      .filter(Boolean),
    status: form.status,
  })
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent
      class="max-h-[88vh] max-w-3xl overflow-y-auto rounded-4xl border-slate-100 bg-white/95 backdrop-blur-xl p-0"
    >
      <DialogHeader class="border-b border-slate-100 px-7 py-6">
        <DialogTitle class="font-display text-3xl tracking-tight text-slate-900">
          Добавить агента
        </DialogTitle>
        <DialogDescription class="text-sm font-light leading-7 text-slate-500">
          Настройте нового участника совета: роль, системный промпт, цели и ограничения для будущих
          обсуждений.
        </DialogDescription>
      </DialogHeader>

      <div class="grid gap-6 px-7 py-6">
        <div class="grid gap-6 md:grid-cols-2">
          <label class="space-y-3">
            <span class="text-sm font-light tracking-tight text-slate-900">Имя агента</span>
            <Input
              v-model="form.name"
              class="rounded-2xl bg-white/90"
              placeholder="Например, Синтез"
            />
          </label>
          <label class="space-y-3">
            <span class="text-sm font-light tracking-tight text-slate-900">Роль</span>
            <Input
              v-model="form.role"
              class="rounded-2xl bg-white/90"
              placeholder="Например, аналитик доверия"
            />
          </label>
        </div>

        <label class="space-y-3">
          <span class="text-sm font-light tracking-tight text-slate-900">Краткое описание</span>
          <Textarea v-model="form.description" class="min-h-28 bg-white/90" />
        </label>

        <label class="space-y-3">
          <span class="text-sm font-light tracking-tight text-slate-900">Системный промпт</span>
          <Textarea v-model="form.systemPrompt" class="min-h-40 bg-white/90" />
        </label>

        <div class="grid gap-6 md:grid-cols-2">
          <label class="space-y-3">
            <span class="text-sm font-light tracking-tight text-slate-900">Цели</span>
            <Textarea v-model="form.goals" class="min-h-32 bg-white/90" />
          </label>
          <label class="space-y-3">
            <span class="text-sm font-light tracking-tight text-slate-900">Ограничения</span>
            <Textarea v-model="form.constraints" class="min-h-32 bg-white/90" />
          </label>
        </div>

        <label class="space-y-3">
          <span class="text-sm font-light tracking-tight text-slate-900">Статус</span>
          <Select v-model="form.status">
            <SelectTrigger class="w-full rounded-2xl bg-white/90">
              <SelectValue placeholder="Выберите статус" />
            </SelectTrigger>
            <SelectContent class="rounded-2xl border-slate-100 bg-white/95 backdrop-blur-xl">
              <SelectItem value="active">Активен</SelectItem>
              <SelectItem value="draft">Черновик</SelectItem>
              <SelectItem value="paused">На паузе</SelectItem>
            </SelectContent>
          </Select>
        </label>
      </div>

      <DialogFooter class="border-t border-slate-100 px-7 py-6">
        <Button variant="outline" class="rounded-full" @click="emit('update:open', false)">
          Отмена
        </Button>
        <Button
          class="rounded-full px-6"
          :disabled="
            props.saving || !form.name.trim() || !form.role.trim() || !form.systemPrompt.trim()
          "
          @click="submit"
        >
          <AppIcon name="addCircle" :size="18" />
          {{ props.saving ? 'Сохраняем...' : 'Сохранить агента' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
