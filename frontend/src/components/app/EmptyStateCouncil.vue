<script setup lang="ts">
import type { AppIconName } from '@/lib/icon-registry'

import { Button } from '@/components/ui/button'

import AppIcon from './AppIcon.vue'

interface Props {
  title: string
  description: string
  icon: AppIconName
  actionLabel?: string
}

defineProps<Props>()
defineEmits<{ action: [] }>()
</script>

<template>
  <div class="elevated-glass flex flex-col items-center justify-center gap-6 px-8 py-14 text-center">
    <div class="ornament-ring flex size-18 items-center justify-center text-slate-900">
      <AppIcon :name="icon" :size="28" />
    </div>
    <div class="space-y-3">
      <h3 class="text-xl font-light tracking-tight text-slate-900">
        {{ title }}
      </h3>
      <p class="mx-auto max-w-md text-sm font-light leading-7 text-slate-500">
        {{ description }}
      </p>
    </div>
    <Button
      v-if="actionLabel"
      variant="outline"
      class="rounded-full px-6"
      @click="$emit('action')"
    >
      {{ actionLabel }}
    </Button>
  </div>
</template>