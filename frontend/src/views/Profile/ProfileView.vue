<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="font-['Playfair_Display'] text-xl font-bold text-stone-900">Overview</h2>
      <p class="mt-0.5 text-xs text-stone-400">Your account details</p>
    </div>

    <div class="h-px bg-stone-100" />

    <div v-if="userStore.loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="h-14 animate-pulse rounded-xl bg-stone-100" />
    </div>

    <div v-else-if="userStore.profile" class="space-y-3">
      <div
        v-for="field in fields"
        :key="field.label"
        class="flex items-center justify-between rounded-xl border border-stone-100 bg-stone-50/60 px-4 py-3.5"
      >
        <div class="flex items-center gap-3">
          <component :is="field.icon" class="h-4 w-4 text-stone-400 shrink-0" />
          <div>
            <p class="text-[0.65rem] uppercase tracking-widest text-stone-400">{{ field.label }}</p>
            <p class="text-sm font-medium text-stone-800 mt-0.5">{{ field.value }}</p>
          </div>
        </div>
      </div>

      <div class="pt-2">
        <Button
          class="bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all text-xs uppercase tracking-widest"
          size="sm"
          @click="router.push({ name: 'update-profile' })"
        >
          <Pencil class="mr-2 h-3.5 w-3.5" /> Edit Profile
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Button } from '@/components/ui/button'
import { User, Mail, Shield, Calendar, Pencil } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()

onMounted(async () => {
  if (!userStore.profile) await userStore.fetchUserProfile()
})

const fields = computed(() => [
  {
    label: 'Full Name',
    value: userStore.profile?.name || '—',
    icon: User,
  },
  {
    label: 'Email Address',
    value: userStore.profile?.email ?? '—',
    icon: Mail,
  },
  {
    label: 'Role',
    value: userStore.profile?.role ?? '—',
    icon: Shield,
  },
  {
    label: 'Member Since',
    value: userStore.profile?.created_at
      ? new Date(userStore.profile.created_at).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        })
      : '—',
    icon: Calendar,
  },
])
</script>
