<script setup lang="ts">
import { reactive, watch } from 'vue'
import { toast } from 'vue-sonner'

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
}>()

const emit = defineEmits<{ 'update:open': [value: boolean] }>()

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
  toast('Новый агент добавлен в демонстрационный реестр', {
    description: `${form.name || 'Новый агент'}: ${form.role || 'роль будет уточнена'}`,
  })
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent
      class="max-h-[88vh] max-w-3xl overflow-y-auto rounded-[2rem] border-border/80 bg-background/95 p-0"
    >
      <DialogHeader class="border-b border-border/70 px-6 py-5">
        <DialogTitle class="font-display text-3xl tracking-[-0.03em]">
          Добавить агента
        </DialogTitle>
        <DialogDescription class="text-sm leading-7 text-muted-foreground">
          Настройте нового участника совета: роль, системный промпт, цели и ограничения для будущих
          обсуждений.
        </DialogDescription>
      </DialogHeader>

      <div class="grid gap-5 px-6 py-5">
        <div class="grid gap-5 md:grid-cols-2">
          <label class="space-y-2">
            <span class="text-sm font-medium text-foreground">Имя агента</span>
            <Input
              v-model="form.name"
              class="rounded-2xl bg-background/90"
              placeholder="Например, Синтез"
            />
          </label>
          <label class="space-y-2">
            <span class="text-sm font-medium text-foreground">Роль</span>
            <Input
              v-model="form.role"
              class="rounded-2xl bg-background/90"
              placeholder="Например, аналитик доверия"
            />
          </label>
        </div>

        <label class="space-y-2">
          <span class="text-sm font-medium text-foreground">Краткое описание</span>
          <Textarea v-model="form.description" class="min-h-24 bg-background/90" />
        </label>

        <label class="space-y-2">
          <span class="text-sm font-medium text-foreground">Системный промпт</span>
          <Textarea v-model="form.systemPrompt" class="min-h-36 bg-background/90" />
        </label>

        <div class="grid gap-5 md:grid-cols-2">
          <label class="space-y-2">
            <span class="text-sm font-medium text-foreground">Цели</span>
            <Textarea v-model="form.goals" class="min-h-28 bg-background/90" />
          </label>
          <label class="space-y-2">
            <span class="text-sm font-medium text-foreground">Ограничения</span>
            <Textarea v-model="form.constraints" class="min-h-28 bg-background/90" />
          </label>
        </div>

        <label class="space-y-2">
          <span class="text-sm font-medium text-foreground">Статус</span>
          <Select v-model="form.status">
            <SelectTrigger class="w-full rounded-2xl bg-background/90">
              <SelectValue placeholder="Выберите статус" />
            </SelectTrigger>
            <SelectContent class="rounded-2xl border-border/80 bg-background/95">
              <SelectItem value="active">Активен</SelectItem>
              <SelectItem value="draft">Черновик</SelectItem>
              <SelectItem value="paused">На паузе</SelectItem>
            </SelectContent>
          </Select>
        </label>
      </div>

      <DialogFooter class="border-t border-border/70 px-6 py-5">
        <Button variant="outline" class="rounded-full" @click="emit('update:open', false)">
          Отмена
        </Button>
        <Button class="rounded-full px-5" @click="submit">
          <AppIcon name="addCircle" :size="18" />
          Сохранить агента
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
