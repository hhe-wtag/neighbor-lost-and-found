<template>
  <div class="mx-auto max-w-7xl px-4 py-8 sm:px-8 font-[DM_Sans]">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
      <div>
        <h1 class="font-['Playfair_Display'] text-3xl font-bold text-stone-900">Items</h1>
        <p class="mt-1 text-sm text-stone-400">Browse lost & found reports</p>
      </div>

      <div class="flex items-center gap-3">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-stone-400" />
          <Input
            v-model="searchQuery"
            placeholder="Search items..."
            class="pl-9 w-56 bg-white/70 border-stone-200 placeholder:text-stone-400 focus-visible:ring-stone-300"
          />
        </div>
        <Button
          class="bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
          @click="openCreateForm"
        >
          <Plus class="mr-2 h-4 w-4" /> Add Item
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <Card class="mb-8 border-0 bg-white/60 shadow-sm backdrop-blur-sm">
      <CardContent class="flex flex-col gap-4 p-5 sm:flex-row sm:items-end">
        <div class="flex-1 space-y-1.5">
          <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">Type</Label>
          <Select :model-value="filters.type" @update:model-value="(v) => (filters.type = v)">
            <SelectTrigger class="border-stone-200 bg-white">
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="lost">Lost</SelectItem>
              <SelectItem value="found">Found</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div class="flex-1 space-y-1.5">
          <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">Category</Label>
          <Select
            :model-value="filters.category"
            @update:model-value="(v) => (filters.category = v)"
          >
            <SelectTrigger class="border-stone-200 bg-white">
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

        <div class="flex-1 space-y-1.5">
          <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">Status</Label>
          <Select :model-value="filters.status" @update:model-value="(v) => (filters.status = v)">
            <SelectTrigger class="border-stone-200 bg-white">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="open">Open</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div class="flex gap-2 sm:w-48">
          <Button
            class="flex-1 bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
            @click="applyFilters"
          >
            Apply
          </Button>
          <Button
            variant="outline"
            class="flex-1 border-stone-200 text-stone-500 hover:text-stone-900 hover:border-stone-400 transition-all"
            @click="clearFilters"
          >
            Clear
          </Button>
        </div>
      </CardContent>
    </Card>

    <!-- Loading -->
    <div v-if="itemStore.loading" class="flex flex-col items-center gap-3 py-24">
      <Loader2 class="h-8 w-8 animate-spin text-amber-700/60" />
      <p class="text-sm text-stone-400">Loading items…</p>
    </div>

    <!-- Error -->
    <Alert v-else-if="itemStore.error" variant="destructive" class="mb-6">
      <AlertCircle class="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>{{ itemStore.error }}</AlertDescription>
    </Alert>

    <!-- Empty State -->
    <div
      v-else-if="itemStore.items.length === 0"
      class="flex flex-col items-center gap-3 py-24 text-stone-400"
    >
      <PackageSearch class="h-12 w-12 text-stone-300" />
      <p class="text-sm">{{ searchQuery ? 'No items match your search' : 'No items available' }}</p>
    </div>

    <!-- Grid -->
    <div
      v-else
      class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 animate-in fade-in duration-500"
    >
      <ItemCard :items="itemStore.items" @openEditForm="(item) => openEditForm(item)" />
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-10 flex justify-center">
      <Pagination :current-page="currentPage" :total-pages="totalPages">
        <div class="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            class="h-8 w-8 text-stone-400 hover:text-stone-900"
            :disabled="currentPage === 1"
            @click="goToPage(1)"
          >
            <ChevronsLeft class="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            class="h-8 w-8 text-stone-400 hover:text-stone-900"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            <ChevronLeft class="h-4 w-4" />
          </Button>

          <template v-for="n in visiblePages" :key="n">
            <Button
              :variant="n === currentPage ? 'default' : 'ghost'"
              size="icon"
              :class="[
                'h-8 w-8 text-sm transition-all',
                n === currentPage
                  ? 'bg-stone-900 text-stone-50 hover:bg-stone-800'
                  : 'text-stone-500 hover:text-stone-900',
              ]"
              @click="goToPage(n)"
            >
              {{ n }}
            </Button>
          </template>

          <Button
            variant="ghost"
            size="icon"
            class="h-8 w-8 text-stone-400 hover:text-stone-900"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            <ChevronRight class="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            class="h-8 w-8 text-stone-400 hover:text-stone-900"
            :disabled="currentPage === totalPages"
            @click="goToPage(totalPages)"
          >
            <ChevronsRight class="h-4 w-4" />
          </Button>
        </div>
      </Pagination>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog :open="showForm" @update:open="(value) => !value && closeForm()">
      <DialogContent class="max-w-[425px] sm:max-w-[600px] bg-[#fffcf9]">
        <DialogHeader>
          <DialogTitle class="font-['Playfair_Display'] text-xl font-bold text-stone-900">
            {{ selectedItem ? 'Edit Item' : 'Create New Item' }}
          </DialogTitle>
          <DialogDescription class="text-stone-400">
            {{ selectedItem ? 'Update the item details below.' : 'Enter the item details below.' }}
          </DialogDescription>
        </DialogHeader>
        <ItemForm :item="selectedItem" @submit="handleFormSubmit" @cancel="closeForm" />
      </DialogContent>
    </Dialog>

    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { Ref } from 'vue'

import { useItemStore } from '@/stores/item'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Pagination } from '@/components/ui/pagination'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import {
  Search,
  Plus,
  Loader2,
  AlertCircle,
  PackageSearch,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  MapPin,
} from 'lucide-vue-next'

import ItemForm from '@/components/items/ItemForm.vue'
import ItemCard from '@/components/items/ItemCard.vue'
import type {
  CreateItemData,
  Item,
  ItemCreate,
  ItemStatus,
  UpdateItemData,
} from '@/interfaces/item'
import { useRouter } from 'vue-router'

const itemStore = useItemStore()
const searchQuery = ref('')
const showForm = ref(false)
const selectedItem: Ref<Item | null> = ref(null)
const currentPage = ref(1)
const pageSize = ref(12)
const searchDebounce = ref<ReturnType<typeof setTimeout> | null>(null)
const filters = ref<{ type?: string; category?: string; status?: string }>({})

const totalPages = computed(() => itemStore.totalPages)
const visiblePages = computed(() => {
  const pages: number[] = []
  for (let n = 1; n <= totalPages.value; n++) {
    if (Math.abs(n - currentPage.value) <= 2 || n === 1 || n === totalPages.value) {
      pages.push(n)
    }
  }
  return pages
})

onMounted(async () => {
  if (itemStore.itemCategories.length === 0) await itemStore.fetchItemCategories()

  await fetchItems()
})

function goToPage(page: number) {
  currentPage.value = Math.min(Math.max(page, 1), totalPages.value)
}

const fetchItems = async () => {
  await itemStore.fetchAllItems({
    ...filters.value,
    keyword: searchQuery.value.trim() || undefined,
    offset: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value,
  })
  currentPage.value = itemStore.currentPage
}

// Debounce keyword search — fires 400ms after user stops typing
watch(searchQuery, () => {
  if (searchDebounce.value) clearTimeout(searchDebounce.value)
  searchDebounce.value = setTimeout(() => {
    currentPage.value = 1
    fetchItems()
  }, 400)
})

const applyFilters = async () => {
  currentPage.value = 1
  await fetchItems()
}
const clearFilters = async () => {
  filters.value = {}
  currentPage.value = 1
  await fetchItems()
}

const openCreateForm = () => {
  selectedItem.value = null
  showForm.value = true
}
const openEditForm = (item: Item) => {
  selectedItem.value = item
  showForm.value = true
}
const closeForm = () => {
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
    const res = await itemStore.createItem(formData as CreateItemData)
    if (res.success && file && res.data?.id) await itemStore.uploadItemPhoto(res.data.id, file)
  } else {
    const res = await itemStore.updateItem(selectedItem.value.id, formData as UpdateItemData)
    if (res.success && res.data?.id) {
      if (removedPhoto) await itemStore.deleteItemPhoto(res.data.id)
      if (file) await itemStore.uploadItemPhoto(res.data.id, file)
    }
  }
  closeForm()
  await fetchItems()
}

watch(currentPage, fetchItems)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');
</style>
