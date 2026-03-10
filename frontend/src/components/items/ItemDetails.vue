<template>
  <div class="min-h-screen bg-[#f5f2ee] font-[DM_Sans]">
    <div class="relative z-10 mx-auto max-w-5xl px-4 py-6 sm:px-8">
      <Button
        variant="ghost"
        class="mb-6 gap-2 text-xs font-medium uppercase tracking-widest text-stone-500 hover:text-stone-900 transition-all hover:gap-3"
        @click="router.push('/items')"
      >
        <ArrowLeft class="h-4 w-4" />
        Back to Items
      </Button>

      <!-- Loading -->
      <div v-if="itemStore.loading" class="flex flex-col items-center gap-3 py-24">
        <Loader2 class="h-8 w-8 animate-spin text-amber-700/60" />
        <p class="text-sm text-stone-400">Fetching item details…</p>
      </div>

      <!-- Error -->
      <Alert v-else-if="itemStore.error" variant="destructive" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>{{ itemStore.error }}</AlertDescription>
      </Alert>

      <!-- Item Details -->
      <div
        v-else-if="itemStore.currentItem"
        class="flex animate-in fade-in slide-in-from-bottom-4 duration-500 flex-col gap-6 lg:flex-row lg:items-start"
      >
        <!-- LEFT: Image + Map -->
        <div class="flex flex-col gap-4 lg:w-[44%]">
          <Card class="overflow-hidden border-0 bg-stone-100 shadow-md">
            <div class="relative">
              <ItemImageCarousel
                :images="[getItemPhotoUrl(itemStore.currentItem) || '']"
                :key="(itemStore.currentItem?.photo_url ?? '') + Date.now()"
              />
              <Badge
                :class="[
                  'absolute left-3 top-3 backdrop-blur-sm border',
                  itemStore.currentItem.type === 'lost'
                    ? 'bg-red-50/80 text-red-600 border-red-200'
                    : 'bg-emerald-50/80 text-emerald-700 border-emerald-200',
                ]"
              >
                {{ itemStore.currentItem.type.toUpperCase() }}
              </Badge>
            </div>
          </Card>

          <Card
            v-if="itemStore.currentItem.lat && itemStore.currentItem.lng"
            class="overflow-hidden border-0 bg-stone-100 shadow-sm"
          >
            <CardHeader class="pb-2 pt-4 px-4">
              <p class="text-[0.68rem] font-medium uppercase tracking-widest text-stone-400">
                Location on Map
              </p>
            </CardHeader>
            <CardContent class="p-0">
              <ItemMap
                :lat="itemStore.currentItem.lat"
                :lng="itemStore.currentItem.lng"
                :location-name="itemStore.currentItem.location_name"
                :description="itemStore.currentItem.description"
              />
            </CardContent>
          </Card>
        </div>

        <!-- RIGHT: Info Panel -->
        <Card class="flex-1 border-0 bg-[#fffcf9] shadow-lg">
          <CardHeader class="pb-2">
            <div class="flex items-start justify-between gap-4">
              <CardTitle
                class="font-['Playfair_Display'] text-2xl font-bold leading-snug text-stone-900 sm:text-3xl"
              >
                {{ itemStore.currentItem.title }}
              </CardTitle>
              <Badge
                :class="[
                  'mt-1 shrink-0 gap-1.5',
                  itemStore.currentItem.status === 'open'
                    ? 'bg-sky-50 text-sky-700 border border-sky-200'
                    : 'bg-stone-100 text-stone-500 border border-stone-200',
                ]"
              >
                <span
                  :class="[
                    'inline-block h-1.5 w-1.5 rounded-full',
                    itemStore.currentItem.status === 'open' ? 'bg-sky-500' : 'bg-stone-400',
                  ]"
                />
                {{ itemStore.currentItem.status.toUpperCase() }}
              </Badge>
            </div>
            <CardDescription class="mt-3 text-sm leading-relaxed text-stone-500">
              {{ itemStore.currentItem.description }}
            </CardDescription>
          </CardHeader>

          <CardContent class="space-y-6">
            <Separator class="bg-gradient-to-r from-stone-200 to-transparent" />

            <!-- Meta Grid -->
            <div class="grid grid-cols-2 gap-x-6 gap-y-5">
              <div class="flex flex-col gap-1">
                <span class="text-[0.68rem] font-medium uppercase tracking-widest text-stone-400">
                  Category
                </span>
                <span class="text-sm capitalize text-stone-800">{{
                  itemStore.currentItem.category
                }}</span>
              </div>

              <div class="flex flex-col gap-1">
                <span class="text-[0.68rem] font-medium uppercase tracking-widest text-stone-400">
                  Location
                </span>
                <span class="text-sm text-stone-800">{{
                  itemStore.currentItem.location_name
                }}</span>
              </div>

              <div class="flex flex-col gap-1">
                <span class="text-[0.68rem] font-medium uppercase tracking-widest text-stone-400">
                  Coordinates
                </span>
                <span class="font-mono text-xs text-stone-500">
                  {{ itemStore.currentItem.lat }}, {{ itemStore.currentItem.lng }}
                </span>
              </div>

              <div class="flex flex-col gap-1">
                <span class="text-[0.68rem] font-medium uppercase tracking-widest text-stone-400">
                  Posted On
                </span>
                <span class="text-sm text-stone-800">{{ formattedDate }}</span>
              </div>

              <!-- Post Owner -->
              <div class="flex flex-col gap-1">
                <span class="text-[0.68rem] font-medium uppercase tracking-widest text-stone-400">
                  Posted By
                </span>
                <span class="text-sm text-stone-800">{{
                  itemStore.currentItem.user?.name || 'Unknown'
                }}</span>
              </div>
              <div class="flex flex-col gap-1">
                <span class="text-[0.68rem] font-medium uppercase tracking-widest text-stone-400">
                  Email
                </span>
                <span class="text-sm text-stone-800">{{
                  itemStore.currentItem.user?.email || 'Unknown'
                }}</span>
              </div>
            </div>

            <Separator class="bg-gradient-to-r from-stone-200 to-transparent" />

            <!-- Owner: edit + claims list -->
            <template v-if="isOwner">
              <div class="flex flex-wrap gap-3">
                <Button
                  class="flex-1 bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
                  @click="openEditForm(itemStore.currentItem)"
                >
                  <Pencil class="mr-2 h-4 w-4" /> Edit Item
                </Button>
              </div>

              <Separator class="bg-gradient-to-r from-stone-200 to-transparent" />
              <ItemClaimsList
                v-if="ownerClaims !== null"
                :claims="ownerClaims"
                @open-chat="openChat"
              />
            </template>

            <!-- Non-owner + resolved -->
            <template v-else-if="itemStore.currentItem.status !== 'open'">
              <Button disabled class="w-full bg-stone-100 text-stone-400 cursor-not-allowed">
                <CheckCircle2 class="mr-2 h-4 w-4" /> Item Resolved
              </Button>
            </template>

            <!-- Non-owner + open: claim flow -->
            <template v-else>
              <ItemMyClaim
                v-if="claimStore.hasExistingClaim && claimStore.asMyClaim"
                :claim="claimStore.asMyClaim"
                :item-type="itemStore.currentItem.type"
              />
              <!-- No claim yet → show the form -->
              <ItemClaimForm
                v-else
                :item-id="itemStore.currentItem.id"
                :item-type="itemStore.currentItem.type"
              />
            </template>
          </CardContent>
        </Card>
      </div>

      <!-- Not Found -->
      <Alert v-else variant="destructive" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>Item not found.</AlertDescription>
      </Alert>
    </div>
  </div>
  <ItemClaimChat :claim="activeChatClaim" :item-id="itemStore.currentItem?.id ?? 0" />
  <Dialog :open="showForm" @update:open="(value) => !value && closeForm()">
    <DialogContent class="max-w-[425px] sm:max-w-[600px] bg-[#fffcf9]">
      <DialogHeader>
        <DialogTitle class="font-['Playfair_Display'] text-xl font-bold text-stone-900">
          Edit Item
        </DialogTitle>
        <DialogDescription class="text-stone-400">
          Update the item details below.
        </DialogDescription>
      </DialogHeader>
      <ItemForm :item="selectedItem" @submit="handleFormSubmit" @cancel="closeForm" />
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, onBeforeMount, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useItemStore } from '@/stores/item'
import { useUserStore } from '@/stores/user'
import type { ItemCreate, ItemListResponse, ItemResponse, ItemStatus } from '@/interfaces/item'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, AlertCircle, Loader2, Pencil, Share2, CheckCircle2 } from 'lucide-vue-next'

import ItemImageCarousel from './ItemImageCarousel.vue'
import ItemMap from './ItemMap.vue'
import ItemClaimForm from './ItemClaimForm.vue'
import ItemMyClaim from './ItemMyClaim.vue'
import ItemClaimsList from './ItemClaimsList.vue'
import { useClaimStore } from '@/stores/claim'
import ItemClaimChat from './ItemClaimChat.vue'
import type { ClaimListItem } from '@/interfaces/claim'
import Dialog from '../ui/dialog/Dialog.vue'
import DialogContent from '../ui/dialog/DialogContent.vue'
import DialogHeader from '../ui/dialog/DialogHeader.vue'
import DialogTitle from '../ui/dialog/DialogTitle.vue'
import DialogDescription from '../ui/dialog/DialogDescription.vue'
import ItemForm from './ItemForm.vue'
import placeHolderImage from '@/assets/product-placeholder.jpg'

interface ItemFormSubmit {
  formData: ItemCreate | (ItemCreate & { status?: ItemStatus })
  file: File | null
  removedPhoto: boolean
}

const router = useRouter()
const route = useRoute()
const itemStore = useItemStore()
const userStore = useUserStore()

const emit = defineEmits<{ (e: 'openEditForm', item: ItemListResponse): void }>()

const showForm = ref(false)
const selectedItem = ref<ItemResponse | null>(null)

onBeforeMount(async () => {
  const id = route.params.id as string
  if (!id) return
  await itemStore.fetchItemById(Number(id))
  await claimStore.fetchClaims(Number(id))
})

const openEditForm = (item: ItemResponse) => {
  selectedItem.value = item
  showForm.value = true
}

const closeForm = () => {
  selectedItem.value = null
  showForm.value = false
}

const currentItem = computed<ItemResponse | null>(() => itemStore.currentItem)

const isOwner = computed(
  () => !!userStore.profile && currentItem.value?.user_id === userStore.profile.id,
)

const claimStore = useClaimStore()

// Use store getters directly — no manual narrowing needed in the component
const ownerClaims = computed(() => (isOwner.value ? claimStore.asOwnerClaims : null))
const myClaim = computed(() => (!isOwner.value ? claimStore.asMyClaim : null))

const formattedDate = computed<string>(() => {
  if (!currentItem.value?.created_at) return ''
  return new Date(currentItem.value.created_at).toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
})

const activeChatClaim = computed(() => {
  if (claimStore.activeClaimId === null) return null
  // Owner: find in claims list
  const fromList = claimStore.asOwnerClaims?.find((c) => c.id === claimStore.activeClaimId)
  if (fromList) return fromList
  // Claimant: use their own claim object
  if (claimStore.asMyClaim?.id === claimStore.activeClaimId) return claimStore.asMyClaim
  return null
})

const openChat = (claim: ClaimListItem) => {
  claimStore.openClaimThread(claim.id)
}

const getItemPhotoUrl = (item: ItemResponse) =>
  item.photo_url ? `${item.photo_url}?t=${Date.now()}` : placeHolderImage

const handleImageError = (event: Event) => {
  ;(event.target as HTMLImageElement).src = placeHolderImage
}

const handleFormSubmit = async ({ formData, file, removedPhoto }: ItemFormSubmit) => {
  if (!selectedItem.value) {
    return
  }
  const res = await itemStore.updateItem(selectedItem.value?.id, formData as UpdateItemData)
  if (res.success && res.data?.id) {
    if (removedPhoto) await itemStore.deleteItemPhoto(res.data.id)
    if (file) await itemStore.uploadItemPhoto(res.data.id, file)
  }

  closeForm()
  await itemStore.fetchItemById(Number(route.params.id as string))
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');
</style>
