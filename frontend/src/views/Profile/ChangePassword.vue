<template>
  <div class="space-y-6">
    <div>
      <h2 class="font-['Playfair_Display'] text-xl font-bold text-stone-900">Change Password</h2>
      <p class="mt-0.5 text-xs text-stone-400">
        Choose a strong password with at least 8 characters
      </p>
    </div>

    <div class="h-px bg-stone-100" />

    <div class="space-y-4">
      <!-- Current Password -->
      <div class="space-y-1.5">
        <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">
          Current Password <span class="text-red-400">*</span>
        </Label>
        <div class="relative">
          <Input
            v-model="form.currentPassword"
            :type="show.current ? 'text' : 'password'"
            placeholder="Enter your current password"
            class="border-stone-200 bg-white pr-10 text-sm text-stone-800 placeholder:text-stone-300 focus-visible:ring-stone-300"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-700 transition-colors"
            @click="show.current = !show.current"
          >
            <EyeOff v-if="show.current" class="h-4 w-4" />
            <Eye v-else class="h-4 w-4" />
          </button>
        </div>
      </div>

      <!-- New Password -->
      <div class="space-y-1.5">
        <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">
          New Password <span class="text-red-400">*</span>
        </Label>
        <div class="relative">
          <Input
            v-model="form.newPassword"
            :type="show.new ? 'text' : 'password'"
            placeholder="Enter your new password"
            class="border-stone-200 bg-white pr-10 text-sm text-stone-800 placeholder:text-stone-300 focus-visible:ring-stone-300"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-700 transition-colors"
            @click="show.new = !show.new"
          >
            <EyeOff v-if="show.new" class="h-4 w-4" />
            <Eye v-else class="h-4 w-4" />
          </button>
        </div>

        <!-- Password strength indicators -->
        <div v-if="form.newPassword" class="grid grid-cols-2 gap-1.5 pt-1">
          <div
            v-for="rule in passwordRules"
            :key="rule.label"
            :class="[
              'flex items-center gap-1.5 text-[0.65rem]',
              rule.passes ? 'text-emerald-600' : 'text-stone-400',
            ]"
          >
            <CheckCircle2 v-if="rule.passes" class="h-3 w-3 shrink-0" />
            <Circle v-else class="h-3 w-3 shrink-0" />
            {{ rule.label }}
          </div>
        </div>
      </div>

      <!-- Confirm Password -->
      <div class="space-y-1.5">
        <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">
          Confirm New Password <span class="text-red-400">*</span>
        </Label>
        <div class="relative">
          <Input
            v-model="form.confirmPassword"
            :type="show.confirm ? 'text' : 'password'"
            placeholder="Confirm your new password"
            class="border-stone-200 bg-white pr-10 text-sm text-stone-800 placeholder:text-stone-300 focus-visible:ring-stone-300"
            :class="{ 'border-red-300 focus-visible:ring-red-200': mismatch }"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-700 transition-colors"
            @click="show.confirm = !show.confirm"
          >
            <EyeOff v-if="show.confirm" class="h-4 w-4" />
            <Eye v-else class="h-4 w-4" />
          </button>
        </div>
        <p v-if="mismatch" class="text-[0.65rem] text-red-400">Passwords do not match</p>
      </div>

      <!-- Errors / Success -->
      <Alert v-if="errorMsg" variant="destructive" class="py-2">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription class="text-xs">{{ errorMsg }}</AlertDescription>
      </Alert>

      <Alert v-if="successMsg" class="border-emerald-200 bg-emerald-50 py-2">
        <CheckCircle2 class="h-4 w-4 text-emerald-600" />
        <AlertDescription class="text-xs text-emerald-700">{{ successMsg }}</AlertDescription>
      </Alert>

      <!-- Actions -->
      <div class="flex gap-2 pt-2">
        <Button
          class="bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all text-xs uppercase tracking-widest"
          size="sm"
          :disabled="loading || !canSubmit"
          @click="submit"
        >
          <Loader2 v-if="loading" class="mr-2 h-3.5 w-3.5 animate-spin" />
          <KeyRound v-else class="mr-2 h-3.5 w-3.5" />
          {{ loading ? 'Updating…' : 'Update Password' }}
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
import { reactive, computed, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Eye, EyeOff, KeyRound, AlertCircle, CheckCircle2, Circle } from 'lucide-vue-next'

const userStore = useUserStore()
const loading = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const form = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const show = reactive({ current: false, new: false, confirm: false })

const passwordRules = computed(() => [
  { label: 'At least 8 characters', passes: form.newPassword.length >= 8 },
  { label: 'One uppercase letter', passes: /[A-Z]/.test(form.newPassword) },
  { label: 'One lowercase letter', passes: /[a-z]/.test(form.newPassword) },
  { label: 'One number', passes: /[0-9]/.test(form.newPassword) },
])

const allRulesPassed = computed(() => passwordRules.value.every((r) => r.passes))
const mismatch = computed(() => !!form.confirmPassword && form.newPassword !== form.confirmPassword)
const canSubmit = computed(
  () =>
    form.currentPassword.trim() &&
    allRulesPassed.value &&
    form.newPassword === form.confirmPassword,
)

const reset = () => {
  form.currentPassword = ''
  form.newPassword = ''
  form.confirmPassword = ''
  successMsg.value = ''
  errorMsg.value = ''
}

const submit = async () => {
  if (!canSubmit.value) return
  loading.value = true
  successMsg.value = ''
  errorMsg.value = ''

  const res = await userStore.updatePassword(form.currentPassword, form.newPassword)

  loading.value = false
  if (res.success) {
    successMsg.value = 'Password updated successfully.'
    reset()
  } else {
    errorMsg.value = res.message
  }
}
</script>
