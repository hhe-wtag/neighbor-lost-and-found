<template>
  <div class="space-y-3">
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
          <!-- Claimant info + status badge -->
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-2.5">
              <Avatar class="h-8 w-8">
                <AvatarFallback class="bg-stone-200 text-stone-600 text-xs font-medium">
                  {{ claim.claimant.name?.slice(0, 2).toUpperCase() ?? 'U' }}
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

          <!-- Message -->
          <p
            class="text-xs leading-relaxed text-stone-600 bg-white rounded-lg p-3 border border-stone-100"
          >
            {{ claim.message }}
          </p>

          <!-- Timestamp -->
          <div class="flex items-center gap-1.5 text-[0.65rem] text-stone-400">
            <Clock class="h-3 w-3" />
            {{ formatDate(claim.created_at) }}
          </div>

          <!-- Error for this specific claim -->
          <Alert
            v-if="itemStore.error && updatingId === claim.id"
            variant="destructive"
            class="py-2"
          >
            <AlertCircle class="h-4 w-4" />
            <AlertDescription class="text-xs">{{ itemStore.error }}</AlertDescription>
          </Alert>

          <!-- Owner actions — only for pending claims -->
          <div
            v-if="claim.status === 'pending' && itemStore.currentItem?.status !== 'claimed'"
            class="flex gap-2 pt-1"
          >
            <Button
              size="sm"
              class="flex-1 bg-emerald-600 text-white hover:bg-emerald-700 active:scale-[0.98] transition-all"
              :disabled="itemStore.loading && updatingId === claim.id"
              @click="updateStatus(claim.id, 'approved')"
            >
              <Loader2
                v-if="itemStore.loading && updatingId === claim.id && pendingStatus === 'approved'"
                class="mr-1.5 h-3.5 w-3.5 animate-spin"
              />
              <CheckCircle2 v-else class="mr-1.5 h-3.5 w-3.5" />
              Approve
            </Button>
            <Button
              size="sm"
              variant="outline"
              class="flex-1 border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 active:scale-[0.98] transition-all"
              :disabled="itemStore.loading && updatingId === claim.id"
              @click="updateStatus(claim.id, 'rejected')"
            >
              <Loader2
                v-if="itemStore.loading && updatingId === claim.id && pendingStatus === 'rejected'"
                class="mr-1.5 h-3.5 w-3.5 animate-spin"
              />
              <XCircle v-else class="mr-1.5 h-3.5 w-3.5" />
              Reject
            </Button>
          </div>

          <!-- Resolved actions — allow reverting to pending -->
          <div v-else class="flex justify-end">
            <Button
              size="sm"
              variant="ghost"
              class="h-7 text-[0.7rem] text-stone-400 hover:text-stone-700"
              :disabled="itemStore.loading && updatingId === claim.id"
              @click="updateStatus(claim.id, 'pending')"
            >
              <RotateCcw class="mr-1.5 h-3 w-3" />
              Revert to pending
            </Button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useItemStore } from '@/stores/item'
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
import type { ClaimListResponse } from '@/interfaces/item'
import { useRoute } from 'vue-router'

defineProps<{ claims: ClaimListResponse[] | null }>()
const emit = defineEmits<{ (e: 'updated'): void }>()

const route = useRoute()
const itemStore = useItemStore()
const expanded = ref(true)

// Track which claim row is in-flight and which status was requested
// so spinners render on the correct button only
const updatingId = ref<number | null>(null)
const pendingStatus = ref<string | null>(null)

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

const updateStatus = async (claimId: number, status: string) => {
  updatingId.value = claimId
  pendingStatus.value = status
  itemStore.clearError()

  const res = await itemStore.updateClaimStatus(claimId, { status })
  if (res.success) {
    fetchClaims()
  }

  updatingId.value = null
  pendingStatus.value = null
}
</script>
