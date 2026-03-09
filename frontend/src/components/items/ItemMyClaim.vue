<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <span class="font-['Playfair_Display'] text-base font-bold text-stone-900">{{
        sectionLabel
      }}</span>
      <div class="flex items-center gap-2">
        <Badge :class="['border text-[0.65rem]', statusConfig[claim.status].class]">
          {{ statusConfig[claim.status].label }}
        </Badge>
      </div>
    </div>

    <div class="rounded-xl border border-stone-200 bg-stone-50/60 p-4 space-y-3">
      <!-- Read mode: last message preview -->
      <template v-if="!editing">
        <p class="text-[0.68rem] uppercase tracking-widest text-stone-400">Last Message</p>
        <div v-if="lastMessage" class="bg-white rounded-lg p-3 border border-stone-100 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-medium text-stone-700">{{ lastMessage.sender.name }}</span>
            <span class="text-[0.6rem] text-stone-300">{{
              formatDate(lastMessage.created_at)
            }}</span>
          </div>
          <p class="text-sm leading-relaxed text-stone-600 line-clamp-2">{{ lastMessage.body }}</p>
        </div>
        <p v-else class="text-xs text-stone-400">No messages yet.</p>
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

        <Alert v-if="claimStore.error" variant="destructive" class="py-2">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription class="text-xs">{{ claimStore.error }}</AlertDescription>
        </Alert>

        <Button
          class="w-full bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
          size="sm"
          :disabled="
            claimStore.loading || !editedMessage.trim() || editedMessage === originalMessage
          "
          @click="saveEdit"
        >
          <Loader2 v-if="claimStore.loading" class="mr-2 h-3.5 w-3.5 animate-spin" />
          <Save v-else class="mr-2 h-3.5 w-3.5" />
          {{ claimStore.loading ? 'Saving…' : 'Save Changes' }}
        </Button>
      </template>

      <div class="flex items-center gap-1.5 text-[0.65rem] text-stone-400">
        <Clock class="h-3 w-3" />
        Submitted {{ formatDate(claim.created_at) }}
      </div>
    </div>

    <!-- Chat + status message -->
    <Button
      class="w-full border-stone-200 text-stone-600 hover:border-stone-400 hover:text-stone-900 transition-all"
      variant="outline"
      @click="claimStore.openClaimThread(claim.id)"
    >
      <MessageSquare class="mr-2 h-4 w-4" />
      View Conversation
    </Button>

    <p class="text-[0.7rem] text-stone-400 text-center leading-relaxed">
      The owner will review your claim and get back to you.
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useClaimStore } from '@/stores/claim'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Clock, Pencil, X, Save, Loader2, AlertCircle, MessageSquare } from 'lucide-vue-next'
import type { MyClaimResponse } from '@/interfaces/claim'

const props = defineProps<{
  claim: MyClaimResponse
  itemType: 'lost' | 'found'
}>()

const sectionLabel = computed(() =>
  props.itemType === 'lost' ? 'Your Sighting Report' : 'Your Claim',
)

const claimStore = useClaimStore()
const editing = ref(false)

const lastMessage = computed(() => props.claim.messages?.at(-1) ?? null)
const originalMessage = computed(() => lastMessage.value?.body ?? '')
const editedMessage = ref(originalMessage.value)

const statusConfig = {
  pending: { label: 'Pending', class: 'bg-amber-50 text-amber-700 border-amber-200' },
  approved: { label: 'Approved', class: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  rejected: { label: 'Rejected', class: 'bg-red-50 text-red-600 border-red-200' },
} as const

const formatDate = (date: string) =>
  new Date(date).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

const toggleEdit = () => {
  editing.value = !editing.value
  editedMessage.value = originalMessage.value
  claimStore.clearError()
}

const saveEdit = async () => {
  if (!editedMessage.value.trim() || editedMessage.value === originalMessage.value) return
  await claimStore.updateClaimMessage(
    props.claim.id,
    { message: editedMessage.value.trim() },
    props.claim.item_id,
  )
  editing.value = false
}
</script>
