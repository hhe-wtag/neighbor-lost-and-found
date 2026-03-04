<template>
  <Card
    v-for="item in props.items"
    :key="item.id"
    class="group relative flex flex-col overflow-hidden border-0 bg-[#fffcf9] shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer active:scale-[0.98]"
    @click="router.push(`/items/${item.id}`)"
  >
    <!-- Image -->
    <div class="relative h-52 w-full overflow-hidden bg-stone-100">
      <img
        :src="getItemPhotoUrl(item)"
        class="h-full w-full object-cover object-center transition-transform duration-500 group-hover:scale-105"
        alt=""
        @error="handleImageError"
      />
      <!-- Badges overlaid on image -->
      <div class="absolute left-3 top-3 flex flex-wrap gap-1.5">
        <Badge
          :class="
            item.type === 'lost'
              ? 'bg-red-50/90 text-red-600 border border-red-200 backdrop-blur-sm'
              : 'bg-emerald-50/90 text-emerald-700 border border-emerald-200 backdrop-blur-sm'
          "
        >
          {{ item.type === 'lost' ? 'Lost' : 'Found' }}
        </Badge>
        <Badge
          v-if="item.status === 'resolved'"
          class="bg-stone-100/90 text-stone-500 border border-stone-200 backdrop-blur-sm"
        >
          Resolved
        </Badge>
        <Badge
          v-if="isNew(item)"
          class="bg-sky-50/90 text-sky-600 border border-sky-200 backdrop-blur-sm"
        >
          New
        </Badge>
      </div>

      <!-- Status: bottom-left of image -->
      <div class="absolute bottom-3 left-3">
        <Badge
          :class="
            item.status === 'open'
              ? 'bg-sky-50/90 text-sky-700 border border-sky-200 backdrop-blur-sm gap-1.5'
              : 'bg-stone-100/90 text-stone-500 border border-stone-200 backdrop-blur-sm gap-1.5'
          "
        >
          <span
            :class="[
              'inline-block h-1.5 w-1.5 rounded-full',
              item.status === 'open' ? 'bg-sky-500' : 'bg-stone-400',
            ]"
          />
          {{ item.status === 'open' ? 'Open' : 'Resolved' }}
        </Badge>
      </div>

      <!-- Edit button overlaid top-right (owner only) -->
      <div v-if="isItemOwner(item)" class="absolute right-3 top-3">
        <Tooltip :delay-duration="0">
          <TooltipTrigger as-child>
            <Button
              variant="secondary"
              size="icon"
              class="h-8 w-8 bg-white/80 backdrop-blur-sm border border-stone-200 text-stone-600 hover:bg-white hover:text-stone-900 shadow-sm transition-all"
              @click="handleEdit($event, item)"
            >
              <Pencil class="h-3.5 w-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom">Edit listing</TooltipContent>
        </Tooltip>
      </div>
    </div>

    <!-- Body -->
    <CardHeader class="pb-2 pt-4">
      <CardTitle
        class="font-['Playfair_Display'] text-base font-bold leading-snug text-stone-900 line-clamp-1"
      >
        {{ item.title }}
      </CardTitle>
      <CardDescription class="line-clamp-2 text-xs leading-relaxed text-stone-400">
        {{ item.description || 'No description provided.' }}
      </CardDescription>
    </CardHeader>

    <CardContent class="flex-1 pb-3">
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-[0.65rem] uppercase tracking-widest text-stone-400">Category</span>
          <span class="text-xs font-medium capitalize text-stone-700">{{ item.category }}</span>
        </div>
        <Separator class="bg-stone-100" />
        <div class="flex items-center justify-between">
          <span class="text-[0.65rem] uppercase tracking-widest text-stone-400">Location</span>
          <span class="text-xs font-medium text-stone-700 text-right max-w-[60%] truncate">
            {{ item.location_name || 'Not specified' }}
          </span>
        </div>
        <Separator class="bg-stone-100" />
        <div class="flex items-center justify-between">
          <span class="text-[0.65rem] uppercase tracking-widest text-stone-400">Posted</span>
          <span class="text-xs font-medium text-stone-700">{{ formatDate(item.created_at) }}</span>
        </div>
      </div>
    </CardContent>

    <!-- Footer -->
    <CardFooter class="pt-0 pb-4">
      <Button
        class="w-full bg-stone-900 text-stone-50 text-xs hover:bg-stone-800 active:scale-[0.98] transition-all"
        size="sm"
        @click.stop="router.push(`/items/${item.id}`)"
      >
        View Details
      </Button>
    </CardFooter>
  </Card>
</template>

<script setup lang="ts">
import type { ItemListResponse } from '@/interfaces/item'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Pencil } from 'lucide-vue-next'
import { formatDate } from '@/utils/timeFunctions'
import placeHolderImage from '@/assets/product-placeholder.jpg'

const props = defineProps<{ items: ItemListResponse[] }>()
const emit = defineEmits<{ (e: 'openEditForm', item: ItemListResponse): void }>()

const router = useRouter()
const userStore = useUserStore()

const isItemOwner = (item: ItemListResponse) => item.user_id === userStore.profile?.id

const isNew = (item: ItemListResponse) =>
  new Date(item.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)

const handleEdit = (event: MouseEvent, item: ItemListResponse) => {
  event.stopPropagation()
  emit('openEditForm', item)
}

const getItemPhotoUrl = (item: ItemListResponse) =>
  item.photo_url ? `${item.photo_url}?t=${Date.now()}` : placeHolderImage

const handleImageError = (event: Event) => {
  ;(event.target as HTMLImageElement).src = placeHolderImage
}
</script>
