<template>
  <div class="relative min-h-screen overflow-hidden pb-28 pt-6 lg:pb-10 lg:pl-28">
    <div class="pointer-events-none absolute inset-0">
      <div
        class="absolute left-[-12rem] top-[-10rem] h-80 w-80 rounded-full bg-[radial-gradient(circle,rgba(230,162,95,0.16),transparent_70%)]"
      />
      <div
        class="absolute bottom-[-8rem] right-[-6rem] h-72 w-72 rounded-full bg-[radial-gradient(circle,rgba(191,126,63,0.1),transparent_70%)]"
      />
    </div>
    <slot />
  </div>
</template>
