<script setup lang="ts">
import { RouterView } from 'vue-router'

import AppShell from '@/components/app/AppShell.vue'
import FloatingSideNav from '@/components/app/FloatingSideNav.vue'
</script>

<template>
  <AppShell>
    <FloatingSideNav />
    <main class="page-shell relative z-10">
      <RouterView />
    </main>
  </AppShell>
</template>
