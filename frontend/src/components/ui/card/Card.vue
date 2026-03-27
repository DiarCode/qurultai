<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div
    data-slot="card"
    :class="
      cn(
        'relative flex flex-col gap-6 rounded-4xl border border-slate-100 bg-white/80 backdrop-blur-xl py-6 text-slate-900 overflow-hidden',
        'before:absolute before:inset-0 before:bg-gradient-to-br before:from-white/50 before:via-transparent before:to-transparent before:pointer-events-none',
        'shadow-[0_1px_3px_rgba(15,23,42,0.02),0_4px_16px_rgba(15,23,42,0.04)]',
        props.class,
      )
    "
  >
    <slot />
  </div>
</template>
