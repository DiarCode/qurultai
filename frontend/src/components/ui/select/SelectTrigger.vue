<script setup lang="ts">
import type { SelectTriggerProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { SelectIcon, SelectTrigger, useForwardProps } from 'reka-ui'
import AppIcon from '@/components/app/AppIcon.vue'
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<SelectTriggerProps & { class?: HTMLAttributes['class']; size?: 'sm' | 'default' }>(),
  { size: 'default' },
)

const delegatedProps = reactiveOmit(props, 'class', 'size')
const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <SelectTrigger
    data-slot="select-trigger"
    :data-size="size"
    v-bind="forwardedProps"
    :class="
      cn(
        'flex w-fit items-center justify-between gap-2.5 rounded-full border border-slate-200 bg-white/90 px-5 py-3 text-sm font-light tracking-tight text-slate-900 whitespace-nowrap transition-all duration-500 outline-none',
        'hover:border-slate-300 hover:bg-white',
        'focus:border-slate-400 focus:shadow-[0_0_0_4px_rgba(15,23,42,0.04)]',
        'disabled:cursor-not-allowed disabled:opacity-50',
        'data-[placeholder]:text-slate-400',
        '[&_svg:not([class*=\'text-\'])]:text-slate-400',
        'data-[size=default]:h-12 data-[size=sm]:h-11',
        '*:data-[slot=select-value]:line-clamp-1 *:data-[slot=select-value]:flex *:data-[slot=select-value]:items-center *:data-[slot=select-value]:gap-2',
        '[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
        props.class,
      )
    "
  >
    <slot />
    <SelectIcon as-child>
      <AppIcon name="arrowDown" :size="16" class="opacity-50" />
    </SelectIcon>
  </SelectTrigger>
</template>