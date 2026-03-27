<script setup lang="ts">
import type { HTMLAttributes } from 'vue'

import { HugeiconsIcon } from '@hugeicons/vue'

import { type AppIconName, iconRegistry } from '@/lib/icon-registry'
import { cn } from '@/lib/utils'

interface Props {
  name: AppIconName
  size?: number | string
  strokeWidth?: number
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  size: 20,
  strokeWidth: 1.7,
})
</script>

<template>
  <HugeiconsIcon
    :icon="iconRegistry[name]"
    :size="size"
    :stroke-width="strokeWidth"
    color="currentColor"
    :class="cn('shrink-0', props.class)"
  />
</template>
