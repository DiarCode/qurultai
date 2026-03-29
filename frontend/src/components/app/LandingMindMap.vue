<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import type { LandingNode } from '@/types/council'

import { Button } from '@/components/ui/button'

import AppIcon from './AppIcon.vue'
import HeroCouncilIllustration from './HeroCouncilIllustration.vue'

const props = defineProps<{
  nodes: LandingNode[]
}>()

const leftColumnIndices = [0, 2, 4] as const
const rightColumnIndices = [1, 3, 5, 6] as const

const leftColumnNodes = computed(() =>
  leftColumnIndices.map((i) => props.nodes[i]).filter((n): n is LandingNode => !!n),
)

const rightColumnNodes = computed(() =>
  rightColumnIndices.map((i) => props.nodes[i]).filter((n): n is LandingNode => !!n),
)
</script>

<template>
  <div
    class="relative mx-auto flex min-h-screen max-w-[1440px] items-center justify-center px-5 py-10 sm:px-8 lg:px-12 lg:py-12"
  >
    <!-- Subtle grid overlay -->
    <div class="ornament-grid rounded-4xl" />

    <!-- Glassmorphic radial gradient overlay -->
    <div
      class="pointer-events-none absolute inset-0 rounded-4xl bg-gradient-to-br from-white/50 via-transparent to-slate-50/30"
    />

    <!-- Decorative circles -->
    <div
      class="pointer-events-none absolute left-1/2 top-1/2 hidden aspect-square w-[52rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-slate-200/40 lg:block"
    />
    <div
      class="pointer-events-none absolute left-1/2 top-1/2 hidden aspect-square w-[40rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-dashed border-slate-200/50 lg:block"
    />

    <!-- Top badge -->
    <div class="absolute inset-x-0 top-8 flex justify-center">
      <div
        class="rounded-full border border-slate-200/60 bg-white/70 backdrop-blur-md px-5 py-2.5 text-sm font-light tracking-tight text-slate-500"
      >
        Цифровой совет решений
      </div>
    </div>

    <!-- Desktop Layout -->
    <div
      class="relative z-10 hidden w-full items-center gap-8 lg:grid lg:grid-cols-[0.88fr_minmax(0,1.18fr)_0.88fr]"
    >
      <!-- Left Column -->
      <div class="space-y-5">
        <div
          v-for="node in leftColumnNodes"
          :key="node.id"
          class="group surface-panel flex gap-5 p-5 transition-all duration-700 hover:-translate-y-1.5 hover:shadow-lg"
        >
          <div class="ornament-ring flex size-14 items-center justify-center text-slate-900">
            <AppIcon :name="node.icon" :size="22" />
          </div>
          <div class="space-y-1.5">
            <p class="text-sm font-light tracking-tight text-slate-900">
              {{ node.label }}
            </p>
            <p class="text-sm font-light leading-6 text-slate-500">
              {{ node.description }}
            </p>
          </div>
        </div>
      </div>

      <!-- Center Column -->
      <div class="relative">
        <div class="space-y-8 text-center">
          <div class="space-y-5">
            <!-- Kicker -->
            <p class="section-kicker justify-center">Qurultai</p>

            <!-- Main heading - editorial serif -->
            <h1
              class="mx-auto max-w-[12ch] font-display text-[clamp(3.5rem,5.5vw,5.5rem)] leading-[0.92] tracking-tight text-slate-900"
            >
              Совет, в котором аргументы слышны.
            </h1>

            <!-- Description -->
            <p class="mx-auto max-w-2xl text-base font-light leading-7 text-slate-500">
              Мультиагентная платформа, где ИИ-участники собирают документы, спорят между собой,
              проверяют источники и выдают итоговое заключение в понятной, проверяемой форме.
            </p>
          </div>

          <!-- Hero illustration container -->
          <div class="elevated-glass mx-auto max-w-[36rem] p-6">
            <div
              class="absolute inset-x-12 top-20 -z-10 h-52 rounded-full bg-gradient-to-br from-slate-100/80 to-transparent blur-2xl"
            />
            <HeroCouncilIllustration class="relative mx-auto max-w-[30rem]" />
          </div>

          <!-- CTA -->
          <div class="flex items-center justify-center gap-6">
            <Button as-child size="lg" class="rounded-full px-8 text-base font-light">
              <RouterLink to="/chat">Созвать совет</RouterLink>
            </Button>
            <p class="max-w-xs text-left text-sm font-light leading-6 text-slate-500">
              Центральный чат для пользователя.
              <br />
              Дебаты агентов открываются отдельно.
            </p>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="space-y-5">
        <div
          v-for="node in rightColumnNodes"
          :key="node.id"
          class="group surface-panel flex gap-5 p-5 transition-all duration-700 hover:-translate-y-1.5 hover:shadow-lg"
        >
          <div class="ornament-ring flex size-14 items-center justify-center text-slate-900">
            <AppIcon :name="node.icon" :size="22" />
          </div>
          <div class="space-y-1.5">
            <p class="text-sm font-light tracking-tight text-slate-900">
              {{ node.label }}
            </p>
            <p class="text-sm font-light leading-6 text-slate-500">
              {{ node.description }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Layout -->
    <div class="relative z-10 flex w-full max-w-xl flex-col gap-10 lg:hidden">
      <div class="space-y-5 text-center">
        <p class="section-kicker justify-center">Qurultai</p>
        <h1
          class="font-display text-[clamp(2.5rem,14vw,4.5rem)] leading-[0.92] tracking-tight text-slate-900"
        >
          Совет, в котором аргументы слышны.
        </h1>
        <p class="text-sm font-light leading-7 text-slate-500">
          Мультиагентная платформа для обсуждений, проверки документов и выпуска итогового
          заключения с видимыми основаниями.
        </p>
      </div>

      <div class="elevated-glass p-6">
        <HeroCouncilIllustration />
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div v-for="node in nodes" :key="node.id" class="surface-panel flex gap-4 p-5">
          <div class="ornament-ring flex size-12 items-center justify-center text-slate-900">
            <AppIcon :name="node.icon" :size="18" />
          </div>
          <div>
            <p class="text-sm font-light tracking-tight text-slate-900">
              {{ node.label }}
            </p>
            <p class="text-xs font-light leading-5 text-slate-500">
              {{ node.description }}
            </p>
          </div>
        </div>
      </div>

      <Button as-child size="lg" class="rounded-full text-base font-light">
        <RouterLink to="/chat">Созвать совет</RouterLink>
      </Button>
    </div>
  </div>
</template>
