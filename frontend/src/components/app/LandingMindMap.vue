<script setup lang="ts">
import { RouterLink } from 'vue-router'

import type { LandingNode } from '@/types/council'

import { Button } from '@/components/ui/button'

import AppIcon from './AppIcon.vue'
import HeroCouncilIllustration from './HeroCouncilIllustration.vue'

defineProps<{
  nodes: LandingNode[]
}>()

const leftColumnNodes = [0, 2, 4] as const
const rightColumnNodes = [1, 3, 5, 6] as const
</script>

<template>
  <div
    class="relative mx-auto flex min-h-screen max-w-[1360px] items-center justify-center px-4 py-8 sm:px-8 lg:px-10 lg:py-10"
  >
    <div class="ornament-grid absolute inset-0 rounded-[2.8rem]" />
    <div
      class="pointer-events-none absolute inset-0 rounded-[2.8rem] bg-[radial-gradient(circle_at_center,rgba(233,165,98,0.12),transparent_42%)]"
    />
    <div
      class="pointer-events-none absolute left-1/2 top-1/2 hidden aspect-square w-[48rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[color:var(--ornament)]/40 lg:block"
    />
    <div
      class="pointer-events-none absolute left-1/2 top-1/2 hidden aspect-square w-[38rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-dashed border-[color:var(--ornament)]/35 lg:block"
    />

    <div class="absolute inset-x-0 top-6 flex justify-center">
      <div
        class="rounded-full border border-border/70 bg-background/70 px-4 py-2 text-xs uppercase tracking-[0.28em] text-muted-foreground backdrop-blur-sm"
      >
        Цифровой совет решений
      </div>
    </div>

    <div
      class="relative z-10 hidden w-full items-center gap-6 lg:grid lg:grid-cols-[0.92fr_minmax(0,1.14fr)_0.92fr]"
    >
      <div class="space-y-4">
        <div
          v-for="index in leftColumnNodes"
          :key="nodes[index].id"
          class="surface-panel flex gap-4 p-4 transition-transform duration-300 hover:-translate-y-1"
        >
          <div class="ornament-ring flex size-12 items-center justify-center text-primary">
            <AppIcon :name="nodes[index].icon" :size="20" />
          </div>
          <div class="space-y-1">
            <p class="text-sm font-medium text-foreground">
              {{ nodes[index].label }}
            </p>
            <p class="text-xs leading-5 text-muted-foreground">
              {{ nodes[index].description }}
            </p>
          </div>
        </div>
      </div>

      <div class="relative">
        <div class="space-y-6 text-center">
          <div class="space-y-3">
            <p class="section-kicker justify-center">Qurultai</p>
            <h1
              class="mx-auto max-w-[11ch] font-display text-[clamp(3.5rem,5vw,5.25rem)] leading-[0.92] tracking-[-0.045em] text-foreground"
            >
              Совет, в котором аргументы слышны.
            </h1>
            <p class="mx-auto max-w-2xl text-[0.95rem] leading-8 text-muted-foreground">
              Мультиагентная платформа, где ИИ-участники собирают документы, спорят между собой,
              проверяют источники и выдают итоговое заключение в понятной, проверяемой форме.
            </p>
          </div>

          <div class="surface-panel mx-auto max-w-[34rem] p-5">
            <div
              class="absolute inset-x-10 top-18 -z-10 h-44 rounded-full bg-[radial-gradient(circle,rgba(233,165,98,0.22),transparent_70%)] blur-2xl"
            />
            <HeroCouncilIllustration class="relative mx-auto max-w-[28rem]" />
          </div>

          <div class="flex items-center justify-center gap-4">
            <Button as-child size="lg" class="rounded-full px-8 text-base">
              <RouterLink to="/chat">Созвать совет</RouterLink>
            </Button>
            <p class="max-w-xs text-left text-sm leading-6 text-muted-foreground">
              Центральный чат для пользователя.
              <br />
              Дебаты агентов открываются отдельно.
            </p>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div
          v-for="index in rightColumnNodes"
          :key="nodes[index].id"
          class="surface-panel flex gap-4 p-4 transition-transform duration-300 hover:-translate-y-1"
        >
          <div class="ornament-ring flex size-12 items-center justify-center text-primary">
            <AppIcon :name="nodes[index].icon" :size="20" />
          </div>
          <div class="space-y-1">
            <p class="text-sm font-medium text-foreground">
              {{ nodes[index].label }}
            </p>
            <p class="text-xs leading-5 text-muted-foreground">
              {{ nodes[index].description }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="relative z-10 flex w-full max-w-xl flex-col gap-8 lg:hidden">
      <div class="space-y-4 text-center">
        <p class="section-kicker justify-center">Qurultai</p>
        <h1
          class="font-display text-[clamp(3rem,14vw,4.4rem)] leading-[0.92] tracking-[-0.05em] text-foreground"
        >
          Совет, в котором аргументы слышны.
        </h1>
        <p class="text-sm leading-7 text-muted-foreground">
          Мультиагентная платформа для обсуждений, проверки документов и выпуска итогового
          заключения с видимыми основаниями.
        </p>
      </div>

      <div class="surface-panel p-5">
        <HeroCouncilIllustration />
      </div>

      <div class="grid gap-3 sm:grid-cols-2">
        <div v-for="node in nodes" :key="node.id" class="surface-panel flex gap-3 p-4">
          <div class="ornament-ring flex size-11 items-center justify-center text-primary">
            <AppIcon :name="node.icon" :size="18" />
          </div>
          <div>
            <p class="text-sm font-medium text-foreground">
              {{ node.label }}
            </p>
            <p class="text-xs leading-5 text-muted-foreground">
              {{ node.description }}
            </p>
          </div>
        </div>
      </div>

      <Button as-child size="lg" class="rounded-full text-base">
        <RouterLink to="/chat">Созвать совет</RouterLink>
      </Button>
    </div>
  </div>
</template>
