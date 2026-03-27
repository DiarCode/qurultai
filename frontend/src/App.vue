<script setup lang="ts">
import 'vue-sonner/style.css'

import { RouterView } from 'vue-router'

import { Toaster } from '@/components/ui/sonner'
</script>

<template>
  <RouterView />
  <Toaster position="top-right" rich-colors close-button />
</template>
