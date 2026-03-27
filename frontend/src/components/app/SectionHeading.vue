<script setup lang="ts">
import type { HTMLAttributes } from 'vue'

import { cn } from '@/lib/utils'

interface Props {
  eyebrow?: string
  title: string
  description?: string
  align?: 'start' | 'center'
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  align: 'start',
})
</script>

<template>
  <div
    :class="
      cn(
        'space-y-3',
        props.align === 'center' ? 'mx-auto max-w-2xl text-center' : 'max-w-2xl',
        props.class,
      )
    "
  >
    <p v-if="eyebrow" class="section-kicker">
      {{ eyebrow }}
    </p>
    <h2
      class="font-display text-[clamp(2rem,4vw,3.5rem)] leading-[0.98] tracking-[-0.03em] text-foreground"
    >
      {{ title }}
    </h2>
    <p v-if="description" class="max-w-xl text-sm leading-7 text-muted-foreground md:text-base">
      {{ description }}
    </p>
  </div>
</template>
