import { defineStore } from 'pinia'
import axiosInstance from '@/plugins/axios'
import { useErrorHandler } from '@/composables/useErrorHandler'
import type {
  ClaimResponse,
  ClaimCreate,
  ClaimMessageCreate,
  ClaimStatusUpdate,
  ClaimListResponse,
  ClaimListItem,
  MyClaimResponse,
  ClaimMessage,
} from '@/interfaces/claim'

const API_PATHS = {
  CREATE: (itemId: number) => `items/${itemId}/claim`,
  GET_FOR_ITEM: (itemId: number) => `items/${itemId}/claims`,
  GET_CLAIM_MESSAGES: (claimId: number) => `items/claims/${claimId}/messages`,
  POST_CLAIM_MESSAGE: (claimId: number) => `items/claims/${claimId}/messages`,
  UPDATE_STATUS: (claimId: number) => `items/claims/${claimId}/resolve`,
} as const

interface ClaimStoreState {
  currentItemClaims: ClaimListResponse | MyClaimResponse | null
  // Messages for the currently open claim thread
  activeClaimMessages: ClaimMessage[]
  activeClaimId: number | null
  loading: boolean
  messagesLoading: boolean
  error: string | null
}

export const useClaimStore = defineStore('claim', {
  state: (): ClaimStoreState => ({
    currentItemClaims: null,
    activeClaimMessages: [],
    activeClaimId: null,
    loading: false,
    messagesLoading: false,
    error: null,
  }),

  getters: {
    asOwnerClaims: (state): ClaimListResponse | null =>
      Array.isArray(state.currentItemClaims)
        ? (state.currentItemClaims as ClaimListResponse)
        : null,

    hasExistingClaim: (state): boolean => {
      return state.currentItemClaims !== null && !Array.isArray(state.currentItemClaims)
    },
    asMyClaim: (state): MyClaimResponse | null => {
      if (state.currentItemClaims === null || Array.isArray(state.currentItemClaims)) return null
      return state.currentItemClaims
    },
  },

  actions: {
    async handleApiCall<T>(
      apiCall: () => Promise<{ success: boolean; data: T; message: any }>,
      fallbackError = 'Something went wrong. Please try again.',
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

    async fetchClaims(itemId: number) {
      return this.handleApiCall<ClaimListResponse | MyClaimResponse>(async () => {
        const { data } = await axiosInstance.get(API_PATHS.GET_FOR_ITEM(itemId))
        return data
      }, 'Failed to fetch claims').then((res) => {
        if (res.success && res.data !== undefined) this.currentItemClaims = res.data
        return res
      })
    },

    async submitClaim(itemId: number, payload: ClaimCreate) {
      return this.handleApiCall<MyClaimResponse>(async () => {
        const { data } = await axiosInstance.post(API_PATHS.CREATE(itemId), payload)
        return data
      }, 'Failed to submit claim').then(async (res) => {
        if (res.success) await this.fetchClaims(itemId)
        return res
      })
    },

    /* ── Fetch full message thread for a specific claim ── */
    async fetchClaimMessages(claimId: number) {
      this.messagesLoading = true
      this.error = null
      try {
        const { data } = await axiosInstance.get(API_PATHS.GET_CLAIM_MESSAGES(claimId))
        if (data.success) {
          this.activeClaimMessages = data.data
          this.activeClaimId = claimId
        }
      } catch (err: unknown) {
        const { handleError } = useErrorHandler()
        this.error = handleError(err) || 'Failed to fetch messages'
      } finally {
        this.messagesLoading = false
      }
    },

    /* ── Post a message to a claim thread ── */
    async postClaimMessage(claimId: number, payload: ClaimMessageCreate, itemId: number) {
      return this.handleApiCall<ClaimMessage>(async () => {
        const { data } = await axiosInstance.post(API_PATHS.POST_CLAIM_MESSAGE(claimId), payload)
        return data
      }, 'Failed to send message').then(async (res) => {
        if (res.success) {
          // Append optimistically then refresh thread
          await this.fetchClaimMessages(claimId)
          await this.fetchClaims(itemId)
        }
        return res
      })
    },

    async updateClaimStatus(claimId: number, payload: ClaimStatusUpdate, itemId: number) {
      return this.handleApiCall<MyClaimResponse>(async () => {
        const { data } = await axiosInstance.patch(API_PATHS.UPDATE_STATUS(claimId), {
          status: payload.status,
        })
        return data
      }, 'Failed to update claim status').then(async (res) => {
        if (res.success) await this.fetchClaims(itemId)
        return res
      })
    },

    openClaimThread(claimId: number) {
      this.activeClaimId = claimId
      this.activeClaimMessages = []
      this.fetchClaimMessages(claimId)
    },

    closeClaimThread() {
      this.activeClaimId = null
      this.activeClaimMessages = []
    },

    clearError() {
      this.error = null
    },
    clearClaims() {
      this.currentItemClaims = null
    },
  },
})
