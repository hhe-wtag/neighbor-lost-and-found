<template>
  <div class="space-y-6">
    <div>
      <h2 class="font-['Playfair_Display'] text-xl font-bold text-stone-900">Edit Profile</h2>
      <p class="mt-0.5 text-xs text-stone-400">Update your name and email address</p>
    </div>

    <div class="h-px bg-stone-100" />

    <div class="space-y-4">
      <div class="space-y-1.5">
        <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400"> Full Name </Label>
        <Input
          v-model="form.name"
          placeholder="Your full name"
          class="border-stone-200 bg-white text-sm text-stone-800 placeholder:text-stone-300 focus-visible:ring-stone-300"
        />
      </div>

      <div class="space-y-1.5">
        <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">
          Email Address
        </Label>
        <Input
          v-model="form.email"
          type="email"
          placeholder="your@email.com"
          class="border-stone-200 bg-white text-sm text-stone-800 placeholder:text-stone-300 focus-visible:ring-stone-300"
        />
      </div>

      <Alert v-if="userStore.error" variant="destructive" class="py-2">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription class="text-xs">{{ userStore.error }}</AlertDescription>
      </Alert>

      <Alert v-if="successMsg" class="border-emerald-200 bg-emerald-50 py-2">
        <CheckCircle2 class="h-4 w-4 text-emerald-600" />
        <AlertDescription class="text-xs text-emerald-700">{{ successMsg }}</AlertDescription>
      </Alert>

      <div class="flex gap-2 pt-2">
        <Button
          class="bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all text-xs uppercase tracking-widest"
          size="sm"
          :disabled="userStore.loading || !isDirty"
          @click="save"
        >
          <Loader2 v-if="userStore.loading" class="mr-2 h-3.5 w-3.5 animate-spin" />
          <Save v-else class="mr-2 h-3.5 w-3.5" />
          {{ userStore.loading ? 'Saving…' : 'Save Changes' }}
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="border-stone-200 text-stone-500 hover:text-stone-900 text-xs uppercase tracking-widest"
          @click="reset"
        >
          Cancel
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Save, AlertCircle, CheckCircle2 } from 'lucide-vue-next'

const userStore = useUserStore()
const successMsg = ref('')

const form = reactive({ name: '', email: '' })

const loadForm = () => {
  form.name = userStore.profile?.name ?? ''
  form.email = userStore.profile?.email ?? ''
}

onMounted(async () => {
  if (!userStore.profile) await userStore.fetchUserProfile()
  loadForm()
})

const isDirty = computed(
  () =>
    form.name !== (userStore.profile?.name ?? '') ||
    form.email !== (userStore.profile?.email ?? ''),
)

const reset = () => {
  loadForm()
  successMsg.value = ''
}

const save = async () => {
  successMsg.value = ''
  const payload: { name?: string; email?: string } = {}
  if (form.name !== (userStore.profile?.name ?? '')) payload.name = form.name
  if (form.email !== (userStore.profile?.email ?? '')) payload.email = form.email

  const res = await userStore.updateUserInfo(payload)
  if (res.success) {
    successMsg.value = 'Profile updated successfully.'
    loadForm()
  }
}
</script>
