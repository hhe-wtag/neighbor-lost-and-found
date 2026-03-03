<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <span class="font-['Playfair_Display'] text-base font-bold text-stone-900">Your Claim</span>
      <Badge :class="['border text-[0.65rem]', statusConfig[claim.status].class]">
        {{ statusConfig[claim.status].label }}
      </Badge>
    </div>

    <div class="rounded-xl border border-stone-200 bg-stone-50/60 p-4 space-y-3">
      <div class="space-y-1.5">
        <p class="text-[0.68rem] uppercase tracking-widest text-stone-400">Your message</p>
        <p
          class="text-sm leading-relaxed text-stone-700 bg-white rounded-lg p-3 border border-stone-100"
        >
          {{ claim.message }}
        </p>
      </div>
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
import { Badge } from '@/components/ui/badge'
import { Clock } from 'lucide-vue-next'
import type { MyClaimResponse } from '@/interfaces/item'

defineProps<{ claim: MyClaimResponse }>()

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
