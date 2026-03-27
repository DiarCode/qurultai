<script setup lang="ts">
import { toast } from 'vue-sonner'

import type { SourceReference } from '@/types/council'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

import AppIcon from './AppIcon.vue'

defineProps<{
  reference: SourceReference
}>()

function notifyOpen(title: string) {
  toast('Источник откроется после подключения хранилища', {
    description: title,
  })
}
</script>

<template>
  <Dialog>
    <DialogTrigger as-child>
      <button
        class="inline-flex items-center gap-2 rounded-full border border-border/70 bg-background/80 px-3 py-1.5 text-left text-xs leading-5 text-muted-foreground transition-colors hover:border-primary/30 hover:text-foreground"
        type="button"
      >
        <AppIcon name="reference" :size="15" class="text-primary" />
        <span class="max-w-52 truncate">{{ reference.title }}</span>
        <span v-if="reference.location" class="text-[color:var(--ornament-strong)]">
          {{ reference.location }}
        </span>
      </button>
    </DialogTrigger>
    <DialogContent class="max-w-xl rounded-[2rem] border-border/80 bg-background/95 p-0">
      <DialogHeader class="border-b border-border/70 px-6 py-5">
        <div class="flex flex-wrap items-center gap-2">
          <Badge variant="secondary">{{ reference.type }}</Badge>
          <Badge v-if="reference.location" variant="outline">{{ reference.location }}</Badge>
        </div>
        <DialogTitle class="pt-2 text-left text-xl">
          {{ reference.title }}
        </DialogTitle>
        <DialogDescription class="text-left text-sm leading-7 text-muted-foreground">
          {{ reference.summary }}
        </DialogDescription>
      </DialogHeader>
      <div class="space-y-4 px-6 py-5">
        <div
          class="rounded-[1.5rem] border border-dashed border-border/80 bg-[color:var(--surface-muted)] p-4"
        >
          <p class="text-xs uppercase tracking-[0.22em] text-muted-foreground">
            Источники и ссылки
          </p>
          <p class="mt-2 text-sm leading-7 text-foreground">
            В итоговой интеграции здесь будет открываться просмотр документа, страницы и выделенного
            фрагмента, на который ссылается тезис.
          </p>
        </div>

        <Button class="rounded-full px-5" @click="notifyOpen(reference.title)">
          <AppIcon name="link" :size="16" />
          Открыть источник
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>
