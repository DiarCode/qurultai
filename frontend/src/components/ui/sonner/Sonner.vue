<script lang="ts" setup>
import type { ToasterProps } from 'vue-sonner'
import { Toaster as Sonner } from 'vue-sonner'
import AppIcon from '@/components/app/AppIcon.vue'
import { cn } from '@/lib/utils'

const props = defineProps<ToasterProps>()
</script>

<template>
  <Sonner
    :class="cn('toaster group', props.class)"
    :style="{
      '--normal-bg': 'var(--popover)',
      '--normal-text': 'var(--popover-foreground)',
      '--normal-border': 'var(--border)',
      '--border-radius': 'var(--radius)',
    }"
    v-bind="props"
  >
    <template #success-icon>
      <AppIcon name="check" :size="16" />
    </template>
    <template #info-icon>
      <AppIcon name="info" :size="16" />
    </template>
    <template #warning-icon>
      <AppIcon name="alert" :size="16" />
    </template>
    <template #error-icon>
      <AppIcon name="cancel" :size="16" />
    </template>
    <template #loading-icon>
      <div>
        <AppIcon name="loading" :size="16" class="animate-spin" />
      </div>
    </template>
    <template #close-icon>
      <AppIcon name="cancel" :size="16" />
    </template>
  </Sonner>
</template>
