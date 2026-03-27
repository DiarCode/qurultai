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
  <div class="surface-panel flex flex-col items-center justify-center gap-4 px-6 py-10 text-center">
    <div class="ornament-ring flex size-16 items-center justify-center text-primary">
      <AppIcon :name="icon" :size="26" />
    </div>
    <div class="space-y-2">
      <h3 class="text-lg font-medium text-foreground">
        {{ title }}
      </h3>
      <p class="mx-auto max-w-md text-sm leading-6 text-muted-foreground">
        {{ description }}
      </p>
    </div>
    <Button
      v-if="actionLabel"
      variant="outline"
      class="rounded-full border-border/80 bg-background/90 px-5"
      @click="$emit('action')"
    >
      {{ actionLabel }}
    </Button>
  </div>
</template>
