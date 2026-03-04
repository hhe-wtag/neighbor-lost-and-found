import { defineStore } from 'pinia'
import type {
  ItemResponse,
  ItemListResponse,
  ItemCreate,
  ItemUpdate,
  ItemType,
  ItemStatus,
  ClaimCreate,
} from '@/interfaces/item'
import axiosInstance from '@/plugins/axios'
import { useErrorHandler } from '@/composables/useErrorHandler'

/* =========================
   API PATHS (FastAPI Spec)
========================= */
const API_PATHS = {
  ALL: 'items/',
  SINGLE: (id: number) => `items/${id}`,
  CREATE: 'items/',
  UPDATE: (id: number) => `items/${id}`,
  DELETE: (id: number) => `items/${id}`,
  MY_ITEMS: 'items/me',

  ITEM_CATEGORIES: 'items/categories',

  ITEM_PHOTO: (id: number) => `items/${id}/photo`,

  CREATE_CLAIM: (id: number) => `items/${id}/claim`,
  GET_CLAIMS: (id: number) => `items/${id}/claims`,
  UPDATE_CLAIM_MESSAGE: (id: number) => `items/claims/${id}`,
  UPDATE_CLAIM_STATUS: (id: number) => `items/claims/${id}/resolve`,
} as const

/* =========================
   STORE STATE TYPE
========================= */
interface ItemStoreState {
  items: ItemListResponse[]
  total: number
  offset: number
  limit: number
  itemCategories: string[]
  currentItem: ItemResponse | null
  currentItemClaims: any
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
    currentItemClaims: null,
    itemCategories: [],
    loading: false,
    error: null,
  }),

  /* =========================
     GETTERS
  ========================= */
  getters: {
    getItemById:
      (state) =>
      (id: number): ItemListResponse | undefined =>
        state.items.find((item: ItemListResponse) => item.id === id),

    openItems: (state): ItemListResponse[] =>
      state.items.filter((item: ItemListResponse) => item.status === 'open'),

    lostItems: (state): ItemListResponse[] =>
      state.items.filter((item: ItemListResponse) => item.type === 'lost'),

    foundItems: (state): ItemListResponse[] =>
      state.items.filter((item: ItemListResponse) => item.type === 'found'),

    hasError: (state): boolean => state.error !== null,

    totalPages: (state): number => Math.ceil(state.total / state.limit),
  },

  /* =========================
     ACTIONS
  ========================= */
  actions: {
    /* Generic API handler for APIResponse<T> */
    async handleApiCall<T>(
      apiCall: () => Promise<{ success: boolean; data: T; message: any }>,
      fallbackError: string = 'Something Went Wrong, Please Try Again.',
    ): Promise<{
      success: boolean
      message: string
      data?: T
    }> {
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
                  .map(
                    ([field, errs]) => `${field}: ${Array.isArray(errs) ? errs.join('. ') : errs}`,
                  )
                  .join('. \n'),
          data: result.data,
        }
      } catch (err: unknown) {
        const msg = handleError(err) || fallbackError
        this.error = msg
        console.error(`API Error: ${fallbackError}`, err)

        return {
          success: false,
          message: msg,
        }
      } finally {
        this.loading = false
      }
    },

    /* =========================
       Fetch All Items
    ========================= */
    async fetchAllItems(params?: {
      type?: ItemType
      category?: string[]
      status?: ItemStatus
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
          // Map API response to your state
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

    /* =========================
       Fetch My Items
    ========================= */
    async fetchMyItems() {
      return this.handleApiCall<ItemListResponse[]>(async () => {
        const { data } = await axiosInstance.get(API_PATHS.MY_ITEMS)
        return data
      }, 'Failed to fetch my items').then((res) => {
        if (res.success && res.data) this.items = res.data
        return res
      })
    },

    /* =========================
       Fetch Single Item
    ========================= */
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

    /* =========================
       Fetch Item Categories
    ========================= */
    async fetchItemCategories() {
      return this.handleApiCall<string[]>(async () => {
        const { data } = await axiosInstance.get(API_PATHS.ITEM_CATEGORIES)
        return data
      }, 'Failed to fetch categories').then((res) => {
        if (res.success && res.data) this.itemCategories = res.data
        return res
      })
    },

    /* =========================
       Create Item
    ========================= */
    async createItem(payload: ItemCreate) {
      return this.handleApiCall<ItemResponse>(async () => {
        const { data } = await axiosInstance.post(API_PATHS.CREATE, payload)
        return data
      }, 'Failed to create item').then((res) => {
        if (res.success && res.data) this.items.unshift(res.data)
        return res
      })
    },

    /* =========================
       Update Item
    ========================= */
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

    /* =========================
       Delete Item
    ========================= */
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

    /* =========================
       Upload Item Photo
    ========================= */
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

    /* =========================
       Delete Item Photo
    ========================= */
    async deleteItemPhoto(itemId: number) {
      return this.handleApiCall(async () => {
        const { data } = await axiosInstance.delete(API_PATHS.ITEM_PHOTO(itemId))
        return data
      }, 'Failed to delete item photo')
    },

    /* =========================
       Create Claim for An Item
    ========================= */
    async submitClaim(itemId: number, payload: ClaimCreate) {
      return this.handleApiCall<ItemResponse>(async () => {
        const { data } = await axiosInstance.post(API_PATHS.CREATE_CLAIM(itemId), payload)
        return data
      })
    },

    /* =========================
       Get All Claims for Item
    ========================= */
    async fetchClaims(itemId: number) {
      return this.handleApiCall<ItemResponse>(async () => {
        const { data } = await axiosInstance.get(API_PATHS.GET_CLAIMS(itemId))

        return data
      }, 'Failed to fetch claims').then((res) => {
        if (res.success && res.data !== undefined) {
          this.currentItemClaims = res.data
        }
        return res
      })
    },

    /* =========================
       Get All Claims for Item
    ========================= */
    async updateClaimMessage(claimId: number, payload: { message: string }) {
      return this.handleApiCall<ItemResponse>(async () => {
        const { data } = await axiosInstance.patch(API_PATHS.UPDATE_CLAIM_MESSAGE(claimId), payload)

        return data
      })
    },

    /* =========================
       Get All Claims for Item
    ========================= */
    async updateClaimStatus(claimId: number, payload: { status: string }) {
      return this.handleApiCall<ItemResponse>(async () => {
        const { data } = await axiosInstance.patch(API_PATHS.UPDATE_CLAIM_STATUS(claimId), payload)

        return data
      })
    },

    /* Utilities */
    clearCurrentItem() {
      this.currentItem = null
    },

    clearError() {
      this.error = null
    },
  },
})
