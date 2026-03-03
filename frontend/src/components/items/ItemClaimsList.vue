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
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-2.5">
              <Avatar class="h-8 w-8">
                <AvatarFallback class="text-xs font-medium">
                  {{ claim.claimant.name?.slice(0, 2).toUpperCase() ?? 'U' }}
                </AvatarFallback>
              </Avatar>
              <div>
                <p class="text-sm font-medium text-stone-800">{{ claim.claimant_name }}</p>
                <p class="text-[0.65rem] text-stone-400">{{ claim.claimant_email }}</p>
              </div>
            </div>
            <Badge :class="['shrink-0 border text-[0.65rem]', statusConfig[claim.status].class]">
              {{ statusConfig[claim.status].label }}
            </Badge>
          </div>

          <p
            class="text-xs leading-relaxed text-stone-600 bg-white rounded-lg p-3 border border-stone-100"
          >
            {{ claim.message }}
          </p>

          <div class="flex items-center gap-1.5 text-[0.65rem] text-stone-400">
            <Clock class="h-3 w-3" />
            {{ formatDate(claim.created_at) }}
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Clock, ChevronUp, ChevronDown, MessageSquare } from 'lucide-vue-next'
import type { ClaimListResponse } from '@/interfaces/item'

defineProps<{ claims: ClaimListResponse[] }>()

const expanded = ref(true)

const statusConfig = {
  pending: { label: 'Pending', class: 'bg-amber-50 text-amber-700 border-amber-200' },
  approved: { label: 'Approved', class: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  rejected: { label: 'Rejected', class: 'bg-red-50 text-red-600 border-red-200' },
} as const

const formatDate = (date: string) =>
  new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
</script>
