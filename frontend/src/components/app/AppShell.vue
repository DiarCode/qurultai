<template>
  <div class="relative min-h-screen overflow-hidden pb-20 pt-8 lg:pb-12 lg:pl-24">
    <!-- Glassmorphic ambient background -->
    <div class="pointer-events-none absolute inset-0">
      <!-- Primary radial gradient - top left -->
      <div
        class="absolute -left-32 -top-32 aspect-square w-[500px] rounded-full bg-gradient-to-br from-slate-100/60 to-transparent blur-3xl"
      />
      <!-- Secondary radial gradient - bottom right -->
      <div
        class="absolute -bottom-24 -right-24 aspect-square w-[400px] rounded-full bg-gradient-to-tl from-slate-200/40 to-transparent blur-3xl"
      />
      <!-- Accent highlight -->
      <div
        class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 aspect-square w-[800px] rounded-full bg-gradient-radial from-white/30 via-slate-50/20 to-transparent"
      />
      <!-- Subtle grid pattern -->
      <div
        class="absolute inset-0 opacity-[0.03]"
        style="
          background-image:
            linear-gradient(to right, rgb(15 23 42) 1px, transparent 1px),
            linear-gradient(to bottom, rgb(15 23 42) 1px, transparent 1px);
          background-size: 48px 48px;
        "
      />
    </div>
    <slot />
  </div>
</template>