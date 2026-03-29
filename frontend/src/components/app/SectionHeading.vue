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
        'space-y-4',
        props.align === 'center' ? 'mx-auto max-w-2xl text-center' : 'max-w-2xl',
        props.class,
      )
    "
  >
    <p v-if="eyebrow" class="section-kicker">
      {{ eyebrow }}
    </p>
    <h2
      class="font-display text-[clamp(2rem,4.5vw,3.75rem)] leading-[0.96] tracking-tight text-slate-900"
    >
      {{ title }}
    </h2>
    <p v-if="description" class="max-w-xl text-sm font-light leading-7 text-slate-500 sm:text-base">
      {{ description }}
    </p>
  </div>
</template>
