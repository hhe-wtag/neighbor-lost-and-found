<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 translate-x-4"
    enter-to-class="opacity-100 translate-x-0"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 translate-x-0"
    leave-to-class="opacity-0 translate-x-4"
  >
    <div
      v-if="claim"
      class="fixed inset-y-0 right-0 z-50 flex w-full max-w-sm flex-col bg-[#fffcf9] shadow-2xl border-l border-stone-200"
    >
      <!-- Header -->
      <div class="flex items-center justify-between border-b border-stone-100 px-5 py-4">
        <div class="flex items-center gap-3">
          <Avatar class="h-9 w-9">
            <AvatarFallback class="bg-stone-200 text-stone-600 text-xs font-medium">
              {{ displayName.slice(0, 2).toUpperCase() }}
            </AvatarFallback>
          </Avatar>
          <div>
            <p class="text-sm font-medium text-stone-900">{{ displayName }}</p>
            <p class="text-[0.65rem] text-stone-400">{{ displaySub }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <Badge
            v-if="claimStatus"
            :class="['border text-[0.65rem]', statusConfig[claimStatus].class]"
          >
            {{ statusConfig[claimStatus].label }}
          </Badge>
          <Button
            variant="ghost"
            size="icon"
            class="h-7 w-7 text-stone-400 hover:text-stone-700"
            @click="claimStore.closeClaimThread()"
          >
            <X class="h-4 w-4" />
          </Button>
        </div>
      </div>

      <!-- Messages -->
      <div ref="messagesEl" class="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        <div v-if="claimStore.messagesLoading" class="flex justify-center py-8">
          <Loader2 class="h-6 w-6 animate-spin text-stone-300" />
        </div>

        <template v-else>
          <div
            v-if="claimStore.activeClaimMessages.length === 0"
            class="flex flex-col items-center gap-2 py-12 text-stone-300"
          >
            <MessageSquare class="h-8 w-8" />
            <p class="text-xs">No messages yet.</p>
          </div>

          <div
            v-for="msg in claimStore.activeClaimMessages"
            :key="msg.id"
            :class="['flex w-full', isMine(msg.sender_id) ? 'justify-end' : 'justify-start']"
          >
            <div
              :class="[
                'flex flex-col max-w-[75%]',
                isMine(msg.sender_id) ? 'items-end' : 'items-start',
              ]"
            >
              <div
                :class="[
                  'rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed',
                  isMine(msg.sender_id)
                    ? 'bg-stone-900 text-stone-50 rounded-br-sm'
                    : 'bg-stone-100 text-stone-800 rounded-bl-sm',
                ]"
              >
                {{ msg.body }}
              </div>
              <span class="mt-1 text-[0.6rem] text-stone-400 px-1">
                <template v-if="!isMine(msg.sender_id)">{{ msg.sender.name }} · </template>
                {{ formatDate(msg.created_at) }}
              </span>
            </div>
          </div>
        </template>
      </div>

      <!-- Input -->
      <div class="border-t border-stone-100 p-4 space-y-2">
        <Alert v-if="claimStore.error" variant="destructive" class="py-2">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription class="text-xs">{{ claimStore.error }}</AlertDescription>
        </Alert>
        <div class="flex gap-2">
          <Textarea
            v-model="newMessage"
            placeholder="Type a message…"
            class="min-h-[40px] max-h-[120px] resize-none border-stone-200 bg-white text-sm text-stone-800 placeholder:text-stone-300 focus-visible:ring-stone-300"
            @keydown.enter.exact.prevent="send"
          />
          <Button
            size="icon"
            class="h-10 w-10 shrink-0 bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
            :disabled="claimStore.loading || !newMessage.trim()"
            @click="send"
          >
            <Loader2 v-if="claimStore.loading" class="h-4 w-4 animate-spin" />
            <Send v-else class="h-4 w-4" />
          </Button>
        </div>
        <p class="text-[0.6rem] text-stone-300 text-center">Enter to send</p>
      </div>
    </div>
  </Transition>

  <!-- Backdrop -->
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-200"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="claim"
      class="fixed inset-0 z-40 bg-stone-900/20 backdrop-blur-sm"
      @click="claimStore.closeClaimThread()"
    />
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import { useClaimStore } from '@/stores/claim'
import { useUserStore } from '@/stores/user'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { X, Send, Loader2, MessageSquare, AlertCircle } from 'lucide-vue-next'
import type { ClaimListItem, MyClaimResponse, ClaimStatus } from '@/interfaces/claim'

const props = defineProps<{
  claim: ClaimListItem | MyClaimResponse | null
  itemId: number
}>()

const claimStore = useClaimStore()
const userStore = useUserStore()

// Force numeric comparison — API may return numbers, store id may be a string
const isMine = (senderId: number | string): boolean => {
  const profileId = userStore.profile?.id
  if (profileId === undefined || profileId === null) return false
  return Number(senderId) === Number(profileId)
}

const newMessage = ref('')
const messagesEl = ref<HTMLElement | null>(null)

const displayName = computed(() => {
  if (!props.claim) return ''
  if ('claimant' in props.claim) return props.claim.claimant.name
  return props.claim.item.title
})

const displaySub = computed(() => {
  if (!props.claim) return ''
  if ('claimant' in props.claim) return props.claim.claimant.email
  return 'Your claim'
})

const claimStatus = computed<ClaimStatus | null>(() => props.claim?.status ?? null)

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

watch(
  () => claimStore.activeClaimMessages.length,
  async () => {
    await nextTick()
    if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  },
)

const send = async () => {
  if (!newMessage.value.trim() || !props.claim) return
  const body = newMessage.value.trim()
  newMessage.value = ''
  await claimStore.postClaimMessage(props.claim.id, { body }, props.itemId)
}
</script>
