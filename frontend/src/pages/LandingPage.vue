<script setup lang="ts">
import LandingMindMap from '@/components/app/LandingMindMap.vue'
import { landingNodes } from '@/data/council'
</script>

<template>
  <main class="relative min-h-screen overflow-hidden">
    <LandingMindMap :nodes="landingNodes" />
  </main>
</template>
