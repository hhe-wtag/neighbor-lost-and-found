<template>
  <div class="space-y-3">
    <!-- Section header -->
    <button
      class="flex w-full items-center justify-between text-left"
      @click="expanded = !expanded"
    >
      <div class="flex items-center gap-2">
        <span class="font-['Playfair_Display'] text-base font-bold text-stone-900">Claims</span>
        <Badge class="bg-stone-100 text-stone-600 border border-stone-200 text-xs">
          {{ claims.length }}
        </Badge>
      </div>
      <ChevronUp v-if="expanded" class="h-4 w-4 text-stone-400" />
      <ChevronDown v-else class="h-4 w-4 text-stone-400" />
    </button>

    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div v-if="expanded" class="space-y-3">
        <div
          v-if="claims.length === 0"
          class="flex flex-col items-center gap-2 py-6 text-stone-400"
        >
          <MessageSquare class="h-8 w-8 text-stone-200" />
          <p class="text-xs">No claims submitted yet.</p>
        </div>

        <div
          v-for="claim in claims"
          :key="claim.id"
          class="rounded-xl border border-stone-100 bg-stone-50/60 p-4 space-y-3"
        >
          <!-- Claimant info row -->
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-2.5">
              <Avatar class="h-8 w-8">
                <AvatarFallback class="bg-stone-200 text-stone-600 text-xs font-medium">
                  {{ claim.claimant.name.slice(0, 2).toUpperCase() }}
                </AvatarFallback>
              </Avatar>
              <div>
                <p class="text-sm font-medium text-stone-800">{{ claim.claimant.name }}</p>
                <p class="text-[0.65rem] text-stone-400">{{ claim.claimant.email }}</p>
              </div>
            </div>
            <Badge :class="['shrink-0 border text-[0.65rem]', statusConfig[claim.status].class]">
              {{ statusConfig[claim.status].label }}
            </Badge>
          </div>

          <!-- Last message preview -->
          <div
            v-if="claim.last_message"
            class="rounded-lg bg-white border border-stone-100 px-3 py-2.5 space-y-1"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="text-[0.65rem] font-medium text-stone-500">
                {{ claim.last_message.sender.name }}
              </span>
              <span class="text-[0.6rem] text-stone-300 shrink-0">
                {{ formatDate(claim.last_message.created_at) }}
              </span>
            </div>
            <p class="text-xs text-stone-600 line-clamp-2 leading-relaxed">
              {{ claim.last_message.body }}
            </p>
          </div>

          <!-- Submitted at -->
          <div class="flex items-center gap-1.5 text-[0.65rem] text-stone-400">
            <Clock class="h-3 w-3" />
            Submitted {{ formatDate(claim.created_at) }}
          </div>

          <!-- Error scoped to this row -->
          <Alert
            v-if="claimStore.error && updatingId === claim.id"
            variant="destructive"
            class="py-2"
          >
            <AlertCircle class="h-4 w-4" />
            <AlertDescription class="text-xs">{{ claimStore.error }}</AlertDescription>
          </Alert>

          <!-- Action row -->
          <div class="flex items-center gap-2 pt-1">
            <!-- Open chat -->
            <Button
              size="sm"
              variant="outline"
              class="flex-1 border-stone-200 text-stone-600 hover:border-stone-400 hover:text-stone-900 transition-all"
              @click="emit('openChat', claim)"
            >
              <MessageSquare class="mr-1.5 h-3.5 w-3.5" />
              View Messages
            </Button>

            <!-- Status actions -->
            <template v-if="claim.status === 'pending'">
              <Button
                size="sm"
                class="flex-1 bg-emerald-600 text-white hover:bg-emerald-700 active:scale-[0.98] transition-all"
                :disabled="claimStore.loading && updatingId === claim.id"
                @click="updateStatus(claim.id, claim.item_id, 'approved')"
              >
                <Loader2
                  v-if="
                    claimStore.loading && updatingId === claim.id && pendingStatus === 'approved'
                  "
                  class="mr-1.5 h-3.5 w-3.5 animate-spin"
                />
                <CheckCircle2 v-else class="mr-1.5 h-3.5 w-3.5" />
                Approve
              </Button>
              <Button
                size="sm"
                variant="outline"
                class="flex-1 border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 active:scale-[0.98] transition-all"
                :disabled="claimStore.loading && updatingId === claim.id"
                @click="updateStatus(claim.id, claim.item_id, 'rejected')"
              >
                <Loader2
                  v-if="
                    claimStore.loading && updatingId === claim.id && pendingStatus === 'rejected'
                  "
                  class="mr-1.5 h-3.5 w-3.5 animate-spin"
                />
                <XCircle v-else class="mr-1.5 h-3.5 w-3.5" />
                Reject
              </Button>
            </template>

            <Button
              v-else
              size="sm"
              variant="ghost"
              class="h-7 text-[0.7rem] text-stone-400 hover:text-stone-700"
              :disabled="claimStore.loading && updatingId === claim.id"
              @click="updateStatus(claim.id, claim.item_id, 'pending')"
            >
              <RotateCcw class="mr-1.5 h-3 w-3" />
              Revert
            </Button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useClaimStore } from '@/stores/claim'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Clock,
  ChevronUp,
  ChevronDown,
  MessageSquare,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Loader2,
  AlertCircle,
} from 'lucide-vue-next'
import type { ClaimListResponse, ClaimListItem, ClaimStatus } from '@/interfaces/claim'

defineProps<{ claims: ClaimListResponse }>()
const emit = defineEmits<{ (e: 'openChat', claim: ClaimListItem): void }>()

const claimStore = useClaimStore()
const expanded = ref(true)
const updatingId = ref<number | null>(null)
const pendingStatus = ref<ClaimStatus | null>(null)

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

const updateStatus = async (claimId: number, itemId: number, status: ClaimStatus) => {
  updatingId.value = claimId
  pendingStatus.value = status
  claimStore.clearError()
  await claimStore.updateClaimStatus(claimId, { status }, itemId)
  updatingId.value = null
  pendingStatus.value = null
}
</script>
