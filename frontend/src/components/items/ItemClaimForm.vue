<template>
  <div class="space-y-4">
    <div class="flex flex-wrap gap-3">
      <Button
        :class="[
          'flex-1 transition-all active:scale-[0.98]',
          showForm
            ? 'bg-stone-100 text-stone-700 hover:bg-stone-200'
            : 'bg-stone-900 text-stone-50 hover:bg-stone-800',
        ]"
        @click="toggle"
      >
        <HandHeart class="mr-2 h-4 w-4" />
        {{ showForm ? 'Cancel Claim' : 'Claim Item' }}
      </Button>
      <Button
        variant="outline"
        class="border-stone-300 text-stone-500 hover:text-stone-900 hover:border-stone-400 transition-all"
      >
        <Share2 class="mr-2 h-4 w-4" /> Share
      </Button>
    </div>

    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="showForm" class="rounded-xl border border-stone-200 bg-stone-50/60 p-5 space-y-4">
        <div class="space-y-1">
          <h3 class="font-['Playfair_Display'] text-base font-bold text-stone-900">
            Submit a Claim
          </h3>
          <p class="text-xs text-stone-400 leading-relaxed">
            Describe why this item belongs to you. Unique markings, contents, or context help verify
            ownership.
          </p>
        </div>

        <div class="space-y-1.5">
          <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">
            Your message
          </Label>
          <Textarea
            v-model="message"
            placeholder="e.g. This is my blue backpack — it has a small tear on the left strap and contains my laptop charger…"
            class="min-h-[110px] resize-none border-stone-200 bg-white text-sm text-stone-800 placeholder:text-stone-300 focus-visible:ring-stone-300"
            :maxlength="500"
          />
          <div class="flex justify-end">
            <span class="text-[0.65rem] text-stone-300">{{ message.length }} / 500</span>
          </div>
        </div>

        <Alert v-if="claimStore.error" variant="destructive" class="py-2">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription class="text-xs">{{ claimStore.error }}</AlertDescription>
        </Alert>

        <Alert v-if="submitted" class="border-emerald-200 bg-emerald-50 py-2">
          <CheckCircle2 class="h-4 w-4 text-emerald-600" />
          <AlertDescription class="text-xs text-emerald-700">
            Your claim has been submitted! The owner will review it shortly.
          </AlertDescription>
        </Alert>

        <Button
          class="w-full bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
          :disabled="claimStore.loading || !message.trim() || submitted"
          @click="submit"
        >
          <Loader2 v-if="claimStore.loading" class="mr-2 h-4 w-4 animate-spin" />
          <Send v-else class="mr-2 h-4 w-4" />
          {{ claimStore.loading ? 'Submitting…' : 'Submit Claim' }}
        </Button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { HandHeart, Share2, Send, Loader2, AlertCircle, CheckCircle2 } from 'lucide-vue-next'
import { useClaimStore } from '@/stores/claim.ts'

const props = defineProps<{ itemId: number }>()

const claimStore = useClaimStore()
const showForm = ref(false)
const message = ref('')
const submitted = ref(false)

const toggle = () => {
  showForm.value = !showForm.value
  message.value = ''
  submitted.value = false
  claimStore.clearError()
}

const submit = async () => {
  if (!message.value.trim()) return
  const res = await claimStore.submitClaim(props.itemId, { opening_message: message.value.trim() })
  if (res.success) {
    submitted.value = true
    message.value = ''
  }
}
</script>
