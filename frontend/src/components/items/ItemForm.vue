<template>
  <form @submit.prevent="handleSubmit" class="space-y-2">
    <!-- Title -->
    <div class="space-y-2">
      <Label>Title</Label>
      <Input v-model="formData.title" placeholder="Enter item title" required />
      <p v-if="errors.title" class="text-red-500 text-sm">{{ errors.title }}</p>
    </div>

    <!-- Description -->
    <div class="space-y-2">
      <Label>Description</Label>
      <Textarea v-model="formData.description" placeholder="Describe the item" />
      <p v-if="errors.description" class="text-red-500 text-sm">
        {{ errors.description }}
      </p>
    </div>

    <!-- Type + Category -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Type -->
      <div class="space-y-2">
        <Label>Type</Label>
        <Select
          :model-value="formData.type"
          @update:model-value="(v) => (formData.type = v as ItemType)"
        >
          <SelectTrigger>
            <SelectValue placeholder="Select type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="lost">Lost</SelectItem>
            <SelectItem value="found">Found</SelectItem>
          </SelectContent>
        </Select>
        <p v-if="errors.type" class="text-red-500 text-sm">
          {{ errors.type }}
        </p>
      </div>

      <!-- Category -->
      <div class="space-y-2">
        <Label>Category</Label>
        <Select
          :model-value="formData.category"
          @update:model-value="(v: string) => (formData.category = v)"
        >
          <SelectTrigger class="capitalize">
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem
              v-for="category in categoryOptions"
              :key="category"
              :value="category"
              class="capitalize"
            >
              {{ category }}
            </SelectItem>
          </SelectContent>
        </Select>

        <p v-if="errors.category" class="text-red-500 text-sm">
          {{ errors.category }}
        </p>
      </div>
    </div>

    <!-- Location Name -->
    <div class="space-y-2">
      <Label>Location Name</Label>
      <Input v-model="formData.location_name" placeholder="e.g. Dhanmondi Lake, Dhaka" />
      <p v-if="errors.location_name" class="text-red-500 text-sm">
        {{ errors.location_name }}
      </p>
    </div>

    <!-- Latitude + Longitude -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Latitude -->
      <div class="space-y-2">
        <Label>Latitude</Label>
        <Input v-model.number="formData.lat" type="number" step="any" required />
        <p v-if="errors.lat" class="text-red-500 text-sm">
          {{ errors.lat }}
        </p>
      </div>

      <!-- Longitude -->
      <div class="space-y-2">
        <Label>Longitude</Label>
        <Input v-model.number="formData.lng" type="number" step="any" required />
        <p v-if="errors.lng" class="text-red-500 text-sm">
          {{ errors.lng }}
        </p>
      </div>
    </div>

    <!-- Status (Edit Mode Only) -->
    <div v-if="canUpdateStatus" class="space-y-2">
      <Label>Status</Label>
      <Select
        :model-value="props.item?.status"
        @update:model-value="
          (v) =>
            emit('submit', {
              ...formData,
              status: v as ItemStatus,
            } as ItemUpdate)
        "
      >
        <SelectTrigger>
          <SelectValue placeholder="Select status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem v-for="status in statusOptions" :key="status.value" :value="status.value">
            {{ status.label }}
          </SelectItem>
        </SelectContent>
      </Select>
    </div>

    <!-- Footer -->
    <DialogFooter>
      <Button type="button" variant="outline" @click="emit('cancel')"> Cancel </Button>

      <Button type="submit" :disabled="loading">
        {{ props.item ? 'Update' : 'Create' }}
      </Button>
    </DialogFooter>
  </form>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { ItemResponse, ItemCreate, ItemUpdate, ItemType, ItemStatus } from '@/interfaces/item'
import { z } from 'zod'
import itemValidationSchema from '@/utils/itemValidationSchema'
import { useItemStore } from '@/stores/item'

interface ItemFormProps {
  item?: ItemResponse | null
}

const itemStore = useItemStore()

const props = defineProps<ItemFormProps>()

const emit = defineEmits<{
  (e: 'submit', data: ItemCreate | ItemUpdate): void
  (e: 'cancel'): void
}>()

const loading = ref(false)
const errors = ref<Record<string, string>>({})

const categoryOptions = computed<string[]>(() => {
  return itemStore.itemCategories
})

/**
 * Default Create Shape
 */
const formData = ref<ItemCreate>({
  type: 'lost',
  title: '',
  description: '',
  category: 'other',
  lat: 0,
  lng: 0,
  location_name: '',
})

/**
 * Populate when editing
 */
onMounted(async () => {
  if (props.item) {
    formData.value = {
      type: props.item.type,
      title: props.item.title,
      description: props.item.description ?? '',
      category: props.item.category,
      lat: props.item.lat,
      lng: props.item.lng,
      location_name: props.item.location_name ?? '',
    }
  }
})

/**
 * Status Handling (Only for edit mode)
 */
const statusOptions: { value: ItemStatus; label: string }[] = [
  { value: 'open', label: 'Open' },
  { value: 'resolved', label: 'Resolved' },
]

const canUpdateStatus = computed<boolean>(() => {
  return !!props.item
})

/**
 * Submit
 */
const handleSubmit = async (): Promise<void> => {
  loading.value = true
  errors.value = {}

  try {
    const result = itemValidationSchema.parse(formData.value)
    emit('submit', result)
  } catch (e) {
    if (e instanceof z.ZodError) {
      e.errors.forEach((error) => {
        if (error.path.length > 0) {
          errors.value[String(error.path[0])] = error.message
        }
      })
    }
  } finally {
    loading.value = false
  }
}
</script>
