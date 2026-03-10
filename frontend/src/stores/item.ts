import { defineStore } from 'pinia'
import type {
  ItemResponse,
  ItemListResponse,
  ItemCreate,
  ItemUpdate,
  ItemType,
  ItemStatus,
} from '@/interfaces/item'
import axiosInstance from '@/plugins/axios'
import { useErrorHandler } from '@/composables/useErrorHandler'

const API_PATHS = {
  ALL: 'items/',
  SINGLE: (id: number) => `items/${id}`,
  CREATE: 'items/',
  UPDATE: (id: number) => `items/${id}`,
  DELETE: (id: number) => `items/${id}`,
  MY_ITEMS: 'items/me',
  ITEM_CATEGORIES: 'items/categories',
  ITEM_PHOTO: (id: number) => `items/${id}/photo`,
} as const

interface ItemStoreState {
  items: ItemListResponse[]
  myItems: ItemListResponse[]
  total: number
  offset: number
  limit: number
  itemCategories: string[]
  currentItem: ItemResponse | null
  loading: boolean
  error: string | null
  currentPage: number
  hasNext: boolean
  hasPrev: boolean
}

export const useItemStore = defineStore('item', {
  state: (): ItemStoreState => ({
    items: [],
    total: 0,
    offset: 0,
    limit: 12,
    currentPage: 1,
    hasNext: false,
    hasPrev: false,
    currentItem: null,
    itemCategories: [],
    loading: false,
    error: null,
  }),

  getters: {
    getItemById:
      (state) =>
      (id: number): ItemListResponse | undefined =>
        state.items.find((item) => item.id === id),

    openItems: (state): ItemListResponse[] => state.items.filter((i) => i.status === 'open'),
    lostItems: (state): ItemListResponse[] => state.items.filter((i) => i.type === 'lost'),
    foundItems: (state): ItemListResponse[] => state.items.filter((i) => i.type === 'found'),
    hasError: (state): boolean => state.error !== null,
    totalPages: (state): number => Math.ceil(state.total / state.limit),
  },

  actions: {
    async handleApiCall<T>(
      apiCall: () => Promise<{ success: boolean; data: T; message: any }>,
      fallbackError = 'Something Went Wrong, Please Try Again.',
    ): Promise<{ success: boolean; message: string; data?: T }> {
      const { handleError } = useErrorHandler()
      this.loading = true
      this.error = null

      try {
        const result = await apiCall()
        return {
          success: true,
          message:
            typeof result.message === 'string'
              ? result.message
              : Object.entries(result.message)
                  .map(([f, e]) => `${f}: ${Array.isArray(e) ? e.join('. ') : e}`)
                  .join('.\n'),
          data: result.data,
        }
      } catch (err: unknown) {
        const msg = handleError(err) || fallbackError
        this.error = msg
        return { success: false, message: msg }
      } finally {
        this.loading = false
      }
    },

    async fetchAllItems(params?: {
      type?: ItemType
      category?: string[]
      status?: ItemStatus
      keyword?: string
      lat?: number
      lng?: number
      radius?: number
      offset?: number
      limit?: number
    }) {
      return this.handleApiCall<{
        items: ItemListResponse[]
        total: number
        page: number
        total_pages: number
        offset: number
        limit: number
        has_next: boolean
        has_prev: boolean
      }>(async () => {
        const { data } = await axiosInstance.get(API_PATHS.ALL, { params })
        return data
      }, 'Failed to fetch items').then((res) => {
        if (res.success && res.data) {
          this.items = res.data.items
          this.total = res.data.total
          this.offset = res.data.offset
          this.limit = res.data.limit
          this.currentPage = res.data.page
          this.hasNext = res.data.has_next
          this.hasPrev = res.data.has_prev
        }
        return res
      })
    },

    async fetchMyItems() {
      return this.handleApiCall<ItemListResponse[]>(async () => {
        const { data } = await axiosInstance.get(API_PATHS.MY_ITEMS)
        return data
      }, 'Failed to fetch my items').then((res) => {
        if (res.success && res.data) this.items = res.data
        return res
      })
    },

    async fetchItemById(id: number) {
      return this.handleApiCall<ItemResponse>(async () => {
        const { data } = await axiosInstance.get(API_PATHS.SINGLE(id))
        return data
      }, 'Failed to fetch item').then((res) => {
        if (res.success && res.data) {
          this.currentItem = res.data
          const index = this.items.findIndex((item) => item.id === id)
          if (index !== -1) this.items[index] = { ...this.items[index], ...res.data }
        }
        return res
      })
    },

    async fetchItemCategories() {
      return this.handleApiCall<string[]>(async () => {
        const { data } = await axiosInstance.get(API_PATHS.ITEM_CATEGORIES)
        return data
      }, 'Failed to fetch categories').then((res) => {
        if (res.success && res.data) this.itemCategories = res.data
        return res
      })
    },

    async createItem(payload: ItemCreate) {
      return this.handleApiCall<ItemResponse>(async () => {
        const { data } = await axiosInstance.post(API_PATHS.CREATE, payload)
        return data
      }, 'Failed to create item').then((res) => {
        if (res.success && res.data) this.items.unshift(res.data)
        return res
      })
    },

    async updateItem(id: number, payload: ItemUpdate) {
      return this.handleApiCall<ItemResponse>(async () => {
        const { data } = await axiosInstance.patch(API_PATHS.UPDATE(id), payload)
        return data
      }, 'Failed to update item').then((res) => {
        if (res.success && res.data) {
          const index = this.items.findIndex((item) => item.id === id)
          if (index !== -1) this.items[index] = { ...this.items[index], ...res.data }
          if (this.currentItem?.id === id) this.currentItem = res.data
        }
        return res
      })
    },

    async deleteItem(id: number) {
      return this.handleApiCall<void>(async () => {
        await axiosInstance.delete(API_PATHS.DELETE(id))
      }, 'Failed to delete item').then((res) => {
        if (res.success) {
          this.items = this.items.filter((item) => item.id !== id)
          if (this.currentItem?.id === id) this.clearCurrentItem()
        }
        return res
      })
    },

    async uploadItemPhoto(itemId: number, file: File) {
      return this.handleApiCall(async () => {
        const formData = new FormData()
        formData.append('file', file)
        const { data } = await axiosInstance.put(API_PATHS.ITEM_PHOTO(itemId), formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        return data
      }, 'Failed to upload item photo')
    },

    async deleteItemPhoto(itemId: number) {
      return this.handleApiCall(async () => {
        const { data } = await axiosInstance.delete(API_PATHS.ITEM_PHOTO(itemId))
        return data
      }, 'Failed to delete item photo')
    },

    clearCurrentItem() {
      this.currentItem = null
    },

    clearError() {
      this.error = null
    },
  },
})
