<template>
  <div class="container space-y-6 py-6">
    <!-- Header and Search -->
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold">Items</h1>
      <div class="flex gap-4">
        <div class="relative w-64">
          <Input v-model="searchQuery" placeholder="Search items..." class="pl-8" type="search" />
          <Search class="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
        </div>
        <Button @click="openCreateForm">Add Item</Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 bg-muted/40 p-4 rounded-xl">
      <!-- Type Filter -->
      <div class="space-y-2">
        <Label>Type</Label>
        <Select :model-value="filters.type" @update:model-value="(v) => (filters.type = v)">
          <SelectTrigger>
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="lost">Lost</SelectItem>
            <SelectItem value="found">Found</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <!-- Category Filter -->
      <div class="space-y-2">
        <Label>Category</Label>
        <Select :model-value="filters.category" @update:model-value="(v) => (filters.category = v)">
          <SelectTrigger>
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem
              v-for="category in itemStore.itemCategories"
              :key="category"
              :value="category"
            >
              {{ category }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <!-- Status Filter -->
      <div class="space-y-2">
        <Label>Status</Label>
        <Select :model-value="filters.status" @update:model-value="(v) => (filters.status = v)">
          <SelectTrigger>
            <SelectValue placeholder="All Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <!-- Actions -->
      <div class="flex items-end gap-2">
        <Button class="w-full" @click="applyFilters"> Apply </Button>
        <Button variant="outline" class="w-full" @click="clearFilters"> Clear </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="itemStore.loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>

    <!-- Error State -->
    <Alert v-if="itemStore.error" variant="destructive">
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>{{ itemStore.error }}</AlertDescription>
    </Alert>

    <!-- Empty State -->
    <div v-else-if="itemStore.items.length === 0" class="text-center py-8 text-muted-foreground">
      {{ searchQuery ? 'No items match your search' : 'No items available' }}
    </div>

    <!-- Grid Layout -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <ItemCard :items="itemStore.items" @openEditForm="(item) => openEditForm(item)" />
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog :open="showForm" @update:open="(value) => !value && closeForm()">
      <DialogContent class="max-w-[425px] sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{{ selectedItem ? 'Edit Item' : 'Create New Item' }}</DialogTitle>
          <DialogDescription>
            {{ selectedItem ? 'Update the item details below' : 'Enter the item details below' }}
          </DialogDescription>
        </DialogHeader>
        <ItemForm :item="selectedItem" @submit="handleFormSubmit" @cancel="closeForm" />
      </DialogContent>
    </Dialog>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center pt-6">
      <Pagination :current-page="currentPage" :total-pages="totalPages">
        <PaginationFirst @click="goToPage(1)" />
        <PaginationPrev @click="goToPage(currentPage - 1)" />

        <PaginationEllipsis v-if="currentPage > 3" />

        <button
          v-for="n in visiblePages"
          :key="n"
          :class="{
            'bg-blue-500 text-white': n === currentPage,
            'bg-gray-100 text-gray-700': n !== currentPage,
          }"
          class="px-3 py-1 rounded mx-1"
          @click="goToPage(n)"
        >
          {{ n }}
        </button>

        <PaginationEllipsis v-if="currentPage < totalPages - 2" />

        <PaginationNext @click="goToPage(currentPage + 1)" />
        <PaginationLast @click="goToPage(totalPages)" />
      </Pagination>
    </div>

    <router-view />
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { Ref } from 'vue'

import { useItemStore } from '@/stores/item'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import {
  Pagination,
  PaginationPrev,
  PaginationNext,
  PaginationFirst,
  PaginationLast,
  PaginationEllipsis,
} from '@/components/ui/pagination'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-vue-next'
import ItemForm from '@/components/items/ItemForm.vue'
import type {
  CreateItemData,
  Item,
  ItemCreate,
  ItemStatus,
  UpdateItemData,
} from '@/interfaces/item'
import ItemCard from '@/components/items/ItemCard.vue'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import { Label } from '@/components/ui/label'

const itemStore = useItemStore()
const searchQuery = ref('')
const showForm = ref(false)
const selectedItem: Ref<Item | null> = ref(null)

const currentPage = ref(1)
const pageSize = ref(12)

const totalPages = computed(() => itemStore.totalPages)

const visiblePages = computed(() => {
  const pages = []
  for (let n = 1; n <= totalPages.value; n++) {
    if (Math.abs(n - currentPage.value) <= 2 || n === 1 || n === totalPages.value) {
      pages.push(n)
    }
  }
  return pages
})

function goToPage(page: number) {
  if (page < 1) page = 1
  if (page > totalPages.value) page = totalPages.value
  currentPage.value = page
}

const fetchItems = async () => {
  await itemStore.fetchAllItems({
    ...filters.value,
    offset: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value,
  })
  // sync component page with store
  currentPage.value = itemStore.currentPage
}
onMounted(async () => {
  if (itemStore.itemCategories.length === 0) {
    await itemStore.fetchItemCategories()
  }

  await fetchItems()
})

const filters = ref<{
  type?: string
  category?: string
  status?: string
}>({})

const applyFilters = async () => {
  currentPage.value = 1
  await fetchItems()
}

const clearFilters = async () => {
  filters.value = {}
  currentPage.value = 1
  await fetchItems()
}
const openCreateForm = (): void => {
  selectedItem.value = null
  showForm.value = true
}

const openEditForm = (item: Item): void => {
  selectedItem.value = item
  showForm.value = true
}

const closeForm = (): void => {
  selectedItem.value = null
  showForm.value = false
}

interface ItemFormSubmit {
  formData: ItemCreate | (ItemCreate & { status?: ItemStatus })
  file: File | null
  removedPhoto: boolean
}

const handleFormSubmit = async ({ formData, file, removedPhoto }: ItemFormSubmit) => {
  if (!selectedItem.value) {
    // CREATE
    const res = await itemStore.createItem(formData as CreateItemData)
    if (res.success && file && res.data?.id) {
      await itemStore.uploadItemPhoto(res.data.id, file)
    }
  } else {
    // UPDATE
    const res = await itemStore.updateItem(selectedItem.value.id, formData as UpdateItemData)
    if (res.success && res.data?.id) {
      if (removedPhoto) await itemStore.deleteItemPhoto(res.data.id)
      if (file) await itemStore.uploadItemPhoto(res.data.id, file)
    }
  }

  closeForm()
  await fetchItems()
}

watch(currentPage, async () => {
  await fetchItems()
})
</script>
