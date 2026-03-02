<template>
  <Card
    v-for="item in props.items"
    :key="item.id"
    class="relative overflow-hidden flex flex-col transition-all duration-200 hover:shadow-xl bg-card cursor-pointer"
    @click="router.push(`/items/${item.id}`)"
  >
    <div class="p-4 w-full h-[250px]">
      <div class="relative w-full h-full">
        <img
          :src="`${baseUrl + '/items/' + item.id + '/photo'}` || placeHolderImage"
          class="w-full h-full object-cover object-center rounded-lg border"
          alt=""
          @error="handleImageError"
        />
      </div>
    </div>

    <!-- Card Header -->
    <CardHeader>
      <CardTitle class="text-xl font-bold tracking-tight">
        {{ item.title }}
      </CardTitle>

      <!-- Badges -->
      <div class="flex flex-wrap gap-2">
        <div
          v-for="badge in getBadges(item)"
          :key="badge.text"
          class="w-fit px-3 py-1 rounded-full text-xs font-medium"
          :class="badge.style"
        >
          {{ badge.text }}
        </div>
      </div>

      <CardDescription class="line-clamp-2 mt-2">
        {{ item.description || 'No description provided.' }}
      </CardDescription>
    </CardHeader>

    <!-- Card Content -->
    <CardContent>
      <div class="space-y-2 text-sm">
        <div>
          <p class="text-xs text-muted-foreground">Category</p>
          <p class="font-medium capitalize">{{ item.category }}</p>
        </div>

        <div>
          <p class="text-xs text-muted-foreground">Location</p>
          <p class="font-medium">
            {{ item.location_name || 'Location not specified' }}
          </p>
        </div>

        <div>
          <p class="text-xs text-muted-foreground">Posted On</p>
          <p class="font-medium">
            {{ formatDate(item.created_at) }}
          </p>
        </div>
      </div>
    </CardContent>

    <!-- Card Footer -->
    <CardFooter class="flex" :class="isItemOwner(item) ? 'justify-between' : 'justify-end'">
      <!-- Edit Button -->
      <Tooltip v-if="isItemOwner(item)" :delay-duration="0">
        <TooltipTrigger>
          <Button variant="outline" size="sm" @click="handleEdit($event, item)">
            <Edit class="w-4 h-4 mr-1" />
            Edit
          </Button>
        </TooltipTrigger>
        <TooltipContent :side="'bottom'"> Update your listing </TooltipContent>
      </Tooltip>

      <Button
        variant="secondary"
        size="sm"
        class="hover:bg-primary hover:text-primary-foreground transition-colors"
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
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Edit } from 'lucide-vue-next'
import Tooltip from '../ui/tooltip/Tooltip.vue'
import TooltipTrigger from '../ui/tooltip/TooltipTrigger.vue'
import TooltipContent from '../ui/tooltip/TooltipContent.vue'
import { formatDate } from '@/utils/timeFunctions'
import placeHolderImage from '@/assets/product-placeholder.jpg'

const props = defineProps<{
  items: ItemListResponse[]
}>()

const router = useRouter()
const userStore = useUserStore()

const emit = defineEmits<{
  (e: 'openEditForm', item: ItemListResponse): void
}>()

const baseUrl = import.meta.env.VITE_API_URL

const isItemOwner = (item: ItemListResponse): boolean => {
  return item.user_id === userStore.profile?.id
}

const handleEdit = (event: MouseEvent, item: ItemListResponse): void => {
  event.stopPropagation()
  emit('openEditForm', item)
}

interface Badge {
  text: string
  style: string
}

const getBadges = (item: ItemListResponse): Badge[] => {
  const badges: Badge[] = []
  const now = new Date()
  const sevenDaysMs = 7 * 24 * 60 * 60 * 1000

  // Type badge
  badges.push({
    text: item.type === 'lost' ? 'Lost' : 'Found',
    style: item.type === 'lost' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800',
  })

  // Status badge
  if (item.status === 'resolved') {
    badges.push({
      text: 'Resolved',
      style: 'bg-gray-200 text-gray-800',
    })
  }

  // New badge
  if (new Date(item.created_at) > new Date(now.getTime() - sevenDaysMs)) {
    badges.push({
      text: 'New',
      style: 'bg-blue-100 text-blue-800',
    })
  }

  return badges
}

const handleImageError = (event: unknown) => {
  event.target.src = placeHolderImage
}
</script>
