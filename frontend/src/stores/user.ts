import { defineStore } from 'pinia'
import axiosInstance from '@/plugins/axios'
import { useErrorHandler } from '@/composables/useErrorHandler'

export interface UserProfile {
  id: number
  name: string | null
  email: string
  role: 'ADMIN' | 'USER'
  created_at: string
  updated_at: string | null
}

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null as UserProfile | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.profile,
  },

  actions: {
    async handleApiCall<T>(
      apiCall: () => Promise<T>,
      fallback = 'Something went wrong.',
    ): Promise<{ success: boolean; message: string; data?: T }> {
      const { handleError } = useErrorHandler()
      this.loading = true
      this.error = null
      try {
        const data = await apiCall()
        return { success: true, message: 'OK', data }
      } catch (err) {
        const msg = handleError(err) || fallback
        this.error = msg
        return { success: false, message: msg }
      } finally {
        this.loading = false
      }
    },

    async register(userData: { name?: string; email: string; password: string }) {
      return this.handleApiCall(async () => {
        await axiosInstance.post('/auth/register', userData)
      }, 'Registration failed')
    },

    async login(email: string, password: string) {
      return this.handleApiCall(async () => {
        await axiosInstance.post('/auth/login', { email, password })
        await this.fetchUserProfile()
      }, 'Login failed')
    },

    async fetchUserProfile() {
      return this.handleApiCall(async () => {
        const { data } = await axiosInstance.get('/auth/me')
        this.profile = data.data as UserProfile
        return this.profile
      }, 'Failed to fetch profile')
    },

    async updateUserInfo(payload: { name?: string; email?: string }) {
      if (!this.profile) return { success: false, message: 'Not authenticated' }
      return this.handleApiCall(async () => {
        const { data } = await axiosInstance.patch(`/users/${this.profile!.id}`, payload)
        this.profile = data.data as UserProfile
        return this.profile
      }, 'Failed to update profile')
    },

    async logout() {
      try {
        await axiosInstance.post('/auth/logout')
      } catch (e) {
        console.error('Logout error:', e)
      } finally {
        this.profile = null
        this.error = null
      }
    },
  },
})
