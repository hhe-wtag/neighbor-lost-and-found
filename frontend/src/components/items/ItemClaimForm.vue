<template>
  <div class="space-y-3">
    <!-- Toggle button -->
    <Button
      :class="[
        'w-full transition-all active:scale-[0.98]',
        isOpen
          ? 'border-stone-200 text-stone-600 hover:border-stone-400'
          : itemType === 'found'
            ? 'bg-stone-900 text-stone-50 hover:bg-stone-800'
            : 'bg-amber-700 text-amber-50 hover:bg-amber-800',
      ]"
      :variant="isOpen ? 'outline' : 'default'"
      @click="toggle"
    >
      <template v-if="!isOpen">
        <Binoculars v-if="itemType === 'lost'" class="mr-2 h-4 w-4" />
        <HandHelping v-else class="mr-2 h-4 w-4" />
        {{ copy.button }}
      </template>
      <template v-else>
        <X class="mr-2 h-4 w-4" />
        {{ copy.cancel }}
      </template>
    </Button>

    <!-- Expanding form -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="isOpen" class="rounded-xl border border-stone-200 bg-stone-50/60 p-4 space-y-3">
        <div class="space-y-1.5">
          <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">
            {{ copy.label }}
          </Label>
          <Textarea
            v-model="message"
            :placeholder="copy.placeholder"
            class="min-h-[120px] resize-none border-stone-200 bg-white text-sm text-stone-800 placeholder:text-stone-300 focus-visible:ring-stone-300"
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

        <Button
          class="w-full active:scale-[0.98] transition-all"
          :class="
            itemType === 'lost'
              ? 'bg-amber-700 text-amber-50 hover:bg-amber-800'
              : 'bg-stone-900 text-stone-50 hover:bg-stone-800'
          "
          :disabled="claimStore.loading || !message.trim()"
          @click="submit"
        >
          <Loader2 v-if="claimStore.loading" class="mr-2 h-3.5 w-3.5 animate-spin" />
          <Binoculars v-else-if="itemType === 'lost'" class="mr-2 h-3.5 w-3.5" />
          <HandHelping v-else class="mr-2 h-3.5 w-3.5" />
          {{ claimStore.loading ? 'Submitting…' : copy.button }}
        </Button>

        <p class="text-[0.7rem] text-stone-400 text-center leading-relaxed">
          {{ copy.hint }}
        </p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { HandHeart, Share2, Send, Loader2, AlertCircle, CheckCircle2 } from 'lucide-vue-next'
import { useClaimStore } from '@/stores/claim.ts'
import { X, Binoculars, HandHelping } from 'lucide-vue-next'

const props = defineProps<{
  itemId: number
  itemType: 'lost' | 'found'
}>()

// Derived copy based on item type
const copy = computed(() => {
  if (props.itemType === 'found') {
    return {
      button: 'Claim This Item',
      cancel: 'Cancel Claim',
      placeholder:
        'Explain why this item belongs to you — include any identifying details, purchase info, or anything that proves ownership…',
      label: 'Your Message',
      hint: 'The finder will review your claim and reach out if it matches.',
      icon: 'claim',
    }
  }
  return {
    button: 'Report a Sighting',
    cancel: 'Cancel Report',
    placeholder:
      'Describe where and when you saw this item, its condition, and any other details that might help the owner…',
    label: 'Your Sighting Report',
    hint: 'The owner will review your report and reach out to follow up.',
    icon: 'sighting',
  }
})

const claimStore = useClaimStore()
const isOpen = ref(false)

const message = ref('')
const submitted = ref(false)
const toggle = () => {
  isOpen.value = !isOpen.value
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
