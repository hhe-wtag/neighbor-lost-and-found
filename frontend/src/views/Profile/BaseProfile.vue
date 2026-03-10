<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { computed } from 'vue'
import { User, Settings, ChevronRight, KeyRound } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const navItems = [
  { title: 'Overview', name: 'profile', icon: User },
  { title: 'Edit Profile', name: 'update-profile', icon: Settings },
  { title: 'Change Password', name: 'change-password', icon: KeyRound },
]
const initials = computed(
  () =>
    userStore.profile?.name?.slice(0, 2).toUpperCase() ??
    userStore.profile?.email?.slice(0, 2).toUpperCase() ??
    '?',
)
</script>

<template>
  <div class="min-h-screen bg-[#f5f2ee] font-[DM_Sans]">
    <div class="mx-auto max-w-5xl px-4 py-10 sm:px-8">
      <!-- Page header -->
      <div class="mb-8">
        <h1 class="font-['Playfair_Display'] text-3xl font-bold text-stone-900">Account</h1>
        <p class="mt-1 text-sm text-stone-400">Manage your profile and preferences</p>
      </div>

      <div class="flex flex-col gap-6 lg:flex-row lg:gap-10">
        <!-- Sidebar -->
        <aside class="lg:w-56 shrink-0">
          <div class="rounded-2xl border border-stone-200 bg-[#fffcf9] shadow-sm overflow-hidden">
            <!-- Avatar block -->
            <div class="flex flex-col items-center gap-2 border-b border-stone-100 px-6 py-6">
              <div
                class="flex h-14 w-14 items-center justify-center rounded-full bg-stone-200 text-stone-700 text-lg font-semibold"
              >
                {{ initials }}
              </div>
              <p class="text-sm font-medium text-stone-900 text-center leading-tight">
                {{ userStore.profile?.name || 'No name set' }}
              </p>
              <p class="text-[0.65rem] text-stone-400 text-center truncate max-w-full">
                {{ userStore.profile?.email }}
              </p>
              <span
                class="mt-1 rounded-full border border-stone-200 bg-stone-100 px-2.5 py-0.5 text-[0.6rem] uppercase tracking-widest text-stone-500"
              >
                {{ userStore.profile?.role }}
              </span>
            </div>

            <!-- Nav -->
            <nav class="p-2">
              <button
                v-for="item in navItems"
                :key="item.name"
                :class="[
                  'flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-sm transition-all',
                  route.name === item.name
                    ? 'bg-stone-900 text-stone-50'
                    : 'text-stone-500 hover:bg-stone-100 hover:text-stone-900',
                ]"
                @click="router.push({ name: item.name })"
              >
                <span class="flex items-center gap-2.5">
                  <component :is="item.icon" class="h-4 w-4" />
                  {{ item.title }}
                </span>
                <ChevronRight class="h-3.5 w-3.5 opacity-40" />
              </button>
            </nav>
          </div>
        </aside>

        <!-- Content -->
        <div class="flex-1 min-w-0">
          <div
            class="rounded-2xl border border-stone-200 bg-[#fffcf9] shadow-sm p-6 sm:p-8 animate-in fade-in slide-in-from-bottom-4 duration-500"
          >
            <router-view />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
