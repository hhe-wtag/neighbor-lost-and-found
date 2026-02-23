<template>
  <div>
    <h3 class="text-lg font-medium">Profile</h3>
    <p class="text-sm text-muted-foreground">Details of your account</p>
  </div>

  <Separator class="mt-8 mb-8" />

  <div v-if="loading" class="flex justify-center items-center flex-col">
    <p>Loading profile...</p>
    <div class="flex flex-col space-y-3">
      <Skeleton class="h-[125px] w-[250px] rounded-xl" />
      <div class="space-y-2">
        <Skeleton class="h-4 w-[250px]" />
        <Skeleton class="h-4 w-[200px]" />
      </div>
    </div>
  </div>

  <ScrollArea v-else-if="userStore.profile" class="grid gap-8 pr-4 max-h-[500px] overflow-auto">
    <div class="flex flex-col gap-8">
      <ProfileField icon="User" label="Full Name" :value="`${userStore.profile.name || ''}`" />

      <ProfileField icon="Mail" label="Email" :value="userStore.profile.email || 'N/A'" />
    </div>
  </ScrollArea>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { ref, onMounted } from 'vue'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { Separator } from '@/components/ui/separator'
import ProfileField from '@/components/shared/ProfileField.vue'
import { Skeleton } from '@/components/ui/skeleton'
import { ScrollArea } from '@/components/ui/scroll-area'

const { handleError } = useErrorHandler()
const userStore = useUserStore()
const loading = ref(true)

onMounted(async () => {
  try {
    // await userStore.fetchUserProfile()
  } catch (error) {
    console.error('Error occurred:', handleError(error))
  } finally {
    loading.value = false
  }
})
</script>
