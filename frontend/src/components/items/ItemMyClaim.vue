<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <span class="font-['Playfair_Display'] text-base font-bold text-stone-900">Your Claim</span>
      <div class="flex items-center gap-2">
        <Badge :class="['border text-[0.65rem]', statusConfig[claim.status].class]">
          {{ statusConfig[claim.status].label }}
        </Badge>
        <!-- Only allow editing if still pending -->
        <Button
          v-if="claim.status === 'pending'"
          variant="ghost"
          size="icon"
          class="h-6 w-6 text-stone-400 hover:text-stone-700"
          @click="toggleEdit"
        >
          <Pencil v-if="!editing" class="h-3.5 w-3.5" />
          <X v-else class="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>

    <div class="rounded-xl border border-stone-200 bg-stone-50/60 p-4 space-y-3">
      <!-- Read mode -->
      <template v-if="!editing">
        <div class="space-y-1.5">
          <p class="text-[0.68rem] uppercase tracking-widest text-stone-400">Your message</p>
          <p
            class="text-sm leading-relaxed text-stone-700 bg-white rounded-lg p-3 border border-stone-100"
          >
            {{ claim.message }}
          </p>
        </div>
      </template>

      <!-- Edit mode -->
      <template v-else>
        <div class="space-y-1.5">
          <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">
            Edit your message
          </Label>
          <Textarea
            v-model="editedMessage"
            class="min-h-[110px] resize-none border-stone-200 bg-white text-sm text-stone-800 placeholder:text-stone-300 focus-visible:ring-stone-300"
            :maxlength="500"
          />
          <div class="flex justify-end">
            <span class="text-[0.65rem] text-stone-300">{{ editedMessage.length }} / 500</span>
          </div>
        </div>

        <Alert v-if="itemStore.error" variant="destructive" class="py-2">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription class="text-xs">{{ itemStore.error }}</AlertDescription>
        </Alert>

        <Button
          class="w-full bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
          size="sm"
          :disabled="itemStore.loading || !editedMessage.trim() || editedMessage === claim.message"
          @click="saveEdit"
        >
          <Loader2 v-if="itemStore.loading" class="mr-2 h-3.5 w-3.5 animate-spin" />
          <Save v-else class="mr-2 h-3.5 w-3.5" />
          {{ itemStore.loading ? 'Saving…' : 'Save Changes' }}
        </Button>
      </template>

      <div class="flex items-center gap-1.5 text-[0.65rem] text-stone-400">
        <Clock class="h-3 w-3" />
        Submitted {{ formatDate(claim.created_at) }}
      </div>
    </div>

    <p class="text-[0.7rem] text-stone-400 text-center leading-relaxed">
      The owner will review your claim and get back to you.
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useItemStore } from '@/stores/item'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Clock, Pencil, X, Save, Loader2, AlertCircle } from 'lucide-vue-next'
import type { MyClaimResponse } from '@/interfaces/item'
import { useRoute } from 'vue-router'

const props = defineProps<{ claim: MyClaimResponse }>()
const emit = defineEmits<{ (e: 'updated'): void }>()

const route = useRoute()

const itemStore = useItemStore()
const editing = ref(false)
const editedMessage = ref(props.claim.message)

const statusConfig = {
  pending: { label: 'Pending', class: 'bg-amber-50 text-amber-700 border-amber-200' },
  approved: { label: 'Approved', class: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  rejected: { label: 'Rejected', class: 'bg-red-50 text-red-600 border-red-200' },
} as const

const fetchClaims = async () => {
  const id = route.params.id as string
  if (!id) {
    return
  }

  await itemStore.fetchClaims(Number(id))
}

const formatDate = (date: string) =>
  new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

const toggleEdit = () => {
  editing.value = !editing.value
  editedMessage.value = props.claim.message
  itemStore.clearError()
}

const saveEdit = async () => {
  if (!editedMessage.value.trim() || editedMessage.value === props.claim.message) return
  const res = await itemStore.updateClaimMessage(props.claim.id, {
    message: editedMessage.value.trim(),
  })
  if (res.success) {
    editing.value = false
    if (res.success) {
      fetchClaims()
    }
  }
}
</script>
