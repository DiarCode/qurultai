<script setup lang="ts">
import type { SelectItemProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { SelectItem, SelectItemIndicator, SelectItemText, useForwardProps } from 'reka-ui'
import AppIcon from '@/components/app/AppIcon.vue'
import { cn } from '@/lib/utils'

const props = defineProps<SelectItemProps & { class?: HTMLAttributes['class'] }>()

const delegatedProps = reactiveOmit(props, 'class')

const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <SelectItem
    data-slot="select-item"
    v-bind="forwardedProps"
    :class="
      cn(
        'relative flex w-full cursor-default items-center gap-2.5 rounded-full px-4 py-3 text-sm font-light tracking-tight text-slate-700 outline-none select-none transition-all duration-500',
        'hover:bg-slate-50 hover:text-slate-900',
        'focus:bg-slate-50 focus:text-slate-900',
        'data-[highlighted]:bg-slate-50 data-[highlighted]:text-slate-900',
        'data-[disabled]:pointer-events-none data-[disabled]:opacity-40',
        '[&_svg:not([class*=\'text-\'])]:text-slate-400',
        '[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
        '*:[span]:last:flex *:[span]:last:items-center *:[span]:last:gap-2',
        props.class,
      )
    "
  >
    <span class="absolute right-3 flex size-4 items-center justify-center">
      <SelectItemIndicator>
        <slot name="indicator-icon">
          <AppIcon name="check" :size="16" />
        </slot>
      </SelectItemIndicator>
    </span>

    <SelectItemText>
      <slot />
    </SelectItemText>
  </SelectItem>
</template>