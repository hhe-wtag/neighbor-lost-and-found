<template>
  <div class="container mx-auto px-6 lg:px-12">
    <!-- Back Button -->
    <Button variant="ghost" class="my-4" @click="router.push('/items')">
      <ArrowLeft class="mr-2 h-4 w-4" />
      Back to Items
    </Button>

    <!-- Loading -->
    <div v-if="itemStore.loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>

    <!-- Error -->
    <Alert v-else-if="itemStore.error" variant="destructive" class="mb-6">
      <AlertDescription>{{ itemStore.error }}</AlertDescription>
    </Alert>

    <!-- Item Details -->
    <div v-else-if="itemStore.currentItem" class="flex flex-col lg:flex-row gap-6">
      <Card class="w-full lg:w-2/3">
        <CardHeader>
          <ItemImageCarousel :images="[photoUrl]" />

          <div class="flex justify-between items-start mt-4">
            <CardTitle class="text-2xl">
              {{ itemStore.currentItem.title }}
            </CardTitle>

            <!-- Type Badge -->
            <span
              :class="[
                'px-3 py-1 rounded-full text-sm font-medium',
                itemStore.currentItem.type === 'lost'
                  ? 'bg-red-100 text-red-600'
                  : 'bg-green-100 text-green-600',
              ]"
            >
              {{ itemStore.currentItem.type.toUpperCase() }}
            </span>
          </div>

          <CardDescription class="text-base mt-2">
            {{ itemStore.currentItem.description }}
          </CardDescription>
        </CardHeader>

        <CardContent class="space-y-4 mt-4">
          <!-- Category -->
          <div class="flex justify-between">
            <span class="text-muted-foreground">Category</span>
            <span class="font-medium capitalize">
              {{ itemStore.currentItem.category }}
            </span>
          </div>

          <!-- Location -->
          <div class="flex justify-between">
            <span class="text-muted-foreground">Location</span>
            <span class="font-medium">
              {{ itemStore.currentItem.location_name }}
            </span>
          </div>

          <!-- Coordinates -->
          <div class="flex justify-between">
            <span class="text-muted-foreground">Coordinates</span>
            <span class="font-medium">
              {{ itemStore.currentItem.lat }},
              {{ itemStore.currentItem.lng }}
            </span>
          </div>

          <!-- Status -->
          <div class="flex justify-between items-center">
            <span class="text-muted-foreground">Status</span>
            <span
              :class="[
                'px-3 py-1 rounded-full text-sm font-medium',
                itemStore.currentItem.status === 'open'
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-gray-200 text-gray-700',
              ]"
            >
              {{ itemStore.currentItem.status.toUpperCase() }}
            </span>
          </div>

          <!-- Created At -->
          <div class="flex justify-between">
            <span class="text-muted-foreground">Posted On</span>
            <span class="font-medium">
              {{ formattedDate }}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Not Found -->
    <Alert v-else variant="destructive" class="mb-6">
      <AlertDescription>Item not found</AlertDescription>
    </Alert>
  </div>
</template>
<script setup lang="ts">
import { computed, onBeforeMount, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { useItemStore } from '@/stores/item'
import type { ItemResponse } from '@/interfaces/item'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft } from 'lucide-vue-next'

import ItemImageCarousel from './ItemImageCarousel.vue'

const baseUrl = import.meta.env.VITE_API_URL

const router = useRouter()
const route = useRoute()
const itemStore = useItemStore()

// Fetch item on mount
onBeforeMount(async () => {
  const id = route.params.id as string
  console.log(id)
  if (id) {
    await itemStore.fetchItemById(Number(id))
  }
})

// Typed computed
const currentItem = computed<ItemResponse | null>(() => {
  return itemStore.currentItem
})

const photoUrl = computed<string>(() => baseUrl + '/items/' + currentItem.value?.id + '/photo')

// Format date
const formattedDate = computed<string>(() => {
  if (!currentItem.value?.created_at) return ''
  return new Date(currentItem.value.created_at).toLocaleString()
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
