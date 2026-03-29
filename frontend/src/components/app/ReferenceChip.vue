<script setup lang="ts">
import type { CitationRecord } from '@/types/council'

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
  reference: CitationRecord
}>()
</script>

<template>
  <Dialog>
    <DialogTrigger as-child>
      <button
        class="inline-flex items-center gap-2.5 rounded-full border border-slate-100 bg-white/80 px-4 py-2 text-left text-xs font-light leading-5 text-slate-500 transition-all duration-500 hover:border-slate-200 hover:text-slate-900"
        type="button"
      >
        <AppIcon name="reference" :size="15" class="text-slate-400" />
        <span class="max-w-52 truncate">{{ reference.title }}</span>
        <span v-if="reference.location" class="text-slate-400">
          {{ reference.location }}
        </span>
      </button>
    </DialogTrigger>
    <DialogContent class="max-w-xl rounded-4xl border-slate-100 bg-white/95 backdrop-blur-xl p-0">
      <DialogHeader class="border-b border-slate-100 px-7 py-6">
        <div class="flex flex-wrap items-center gap-2">
          <Badge variant="secondary">Источник</Badge>
          <Badge v-if="reference.score !== null" variant="outline"
            >score {{ reference.score.toFixed(2) }}</Badge
          >
          <Badge v-if="reference.location" variant="outline">{{ reference.location }}</Badge>
        </div>
        <DialogTitle class="pt-3 text-left text-xl font-light tracking-tight text-slate-900">
          {{ reference.title }}
        </DialogTitle>
        <DialogDescription class="text-left text-sm font-light leading-7 text-slate-500">
          {{ reference.snippet || 'Полный документ доступен по ссылке ниже.' }}
        </DialogDescription>
      </DialogHeader>
      <div class="space-y-5 px-7 py-6">
        <div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/50 p-5">
          <p class="text-xs font-light tracking-tight text-slate-400">Источники и ссылки</p>
          <p class="mt-2 text-sm font-light leading-7 text-slate-700">
            {{ reference.snippet || 'Для этого доказательства доступен скачиваемый источник.' }}
          </p>
        </div>

        <Button class="rounded-full px-6" :as-child="Boolean(reference.download_url)">
          <a
            v-if="reference.download_url"
            :href="reference.download_url"
            target="_blank"
            rel="noreferrer"
          >
            <AppIcon name="link" :size="16" />
            Открыть источник
          </a>
          <span v-else class="inline-flex items-center gap-2">
            <AppIcon name="link" :size="16" />
            Источник недоступен
          </span>
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>
