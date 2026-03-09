import { defineStore } from 'pinia'
import axiosInstance from '@/plugins/axios'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { toast } from '@/components/ui/toast' // <-- shadcn toast
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

    hasExistingClaim: (state): boolean =>
      state.currentItemClaims !== null && !Array.isArray(state.currentItemClaims),

    asMyClaim: (state): MyClaimResponse | null =>
      state.currentItemClaims && !Array.isArray(state.currentItemClaims)
        ? state.currentItemClaims
        : null,
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

        if (result.success) {
          // toast({
          //   title: 'Success',
          //   description: result.message,
          // })
        } else {
          toast({
            title: 'Error',
            description: result.message || fallbackError,
          })
        }

        return {
          success: result.success,
          message: result.message,
          data: result.data,
        }
      } catch (err: unknown) {
        const msg = handleError(err) || fallbackError
        this.error = msg
        toast({
          title: 'Error',
          description: msg,
        })
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

    async fetchClaimMessages(claimId: number) {
      this.messagesLoading = true
      this.error = null
      try {
        const { data } = await axiosInstance.get(API_PATHS.GET_CLAIM_MESSAGES(claimId))
        if (data.success) {
          this.activeClaimMessages = data.data
          this.activeClaimId = claimId
        } else {
          toast({
            title: 'Error',
            description: data.message,
          })
        }
      } catch (err: unknown) {
        const { handleError } = useErrorHandler()
        const msg = handleError(err) || 'Failed to fetch messages'
        this.error = msg
        toast({
          title: 'Error',
          description: msg,
        })
      } finally {
        this.messagesLoading = false
      }
    },

    async postClaimMessage(claimId: number, payload: ClaimMessageCreate, itemId: number) {
      return this.handleApiCall<ClaimMessage>(async () => {
        const { data } = await axiosInstance.post(API_PATHS.POST_CLAIM_MESSAGE(claimId), payload)
        return data
      }, 'Failed to send message').then(async (res) => {
        if (res.success) {
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
