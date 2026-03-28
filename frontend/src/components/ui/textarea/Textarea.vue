<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { useVModel } from '@vueuse/core'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
  defaultValue?: string | number
  modelValue?: string | number
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', payload: string | number): void
}>()

const modelValue = useVModel(props, 'modelValue', emits, {
  passive: true,
  defaultValue: props.defaultValue,
})
</script>

<template>
  <textarea
    v-model="modelValue"
    data-slot="textarea"
    :class="
      cn(
        'flex min-h-32 w-full rounded-2xl border border-slate-200 bg-white/90 px-5 py-4 text-sm font-light tracking-tight text-slate-900 placeholder:text-slate-400 transition-all duration-500 outline-none resize-none',
        'hover:border-slate-300',
        'focus:border-slate-400 focus:bg-white focus:shadow-[0_0_0_4px_rgba(15,23,42,0.04)]',
        'disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50',
        'aria-invalid:border-red-400 aria-invalid:focus:shadow-[0_0_0_4px_rgba(220,38,38,0.1)]',
        props.class,
      )
    "
  />
</template>