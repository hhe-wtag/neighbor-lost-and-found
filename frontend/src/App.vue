<script setup lang="ts">
import Toaster from '@/components/ui/toast/Toaster.vue'
import Navbar from './components/shared/Navbar.vue'
import TooltipProvider from './components/ui/tooltip/TooltipProvider.vue'
</script>

<template>
  <TooltipProvider>
    <div class="flex min-h-screen flex-col">
      <Navbar class="flex-none" />
      <main class="flex-1">
        <!-- Ambient background blobs -->
        <div class="pointer-events-none fixed inset-0 z-0 overflow-hidden">
          <div
            class="absolute -right-32 -top-32 h-[500px] w-[500px] rounded-full bg-amber-200/15 blur-3xl"
          />
          <div
            class="absolute -bottom-32 -left-32 h-[400px] w-[400px] rounded-full bg-emerald-200/10 blur-3xl"
          />
        </div>

        <router-view />
      </main>
      <Toaster />
    </div>
  </TooltipProvider>
</template>

<style>
:root {
  --navbar-height: 3.6rem;
}

.min-h-screen-minus-nav {
  min-height: calc(100vh - var(--navbar-height));
}
</style>
