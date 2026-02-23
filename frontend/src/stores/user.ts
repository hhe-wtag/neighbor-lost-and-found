import { defineStore } from 'pinia'
import axiosInstance from '@/plugins/axios'
import { useErrorHandler } from '@/composables/useErrorHandler'
import type { UserProfile } from '@/interfaces/user'

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null as UserProfile | null,
    error: null as string | null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.profile,
  },
  actions: {
    async login(email: string, password: string) {
      const { handleError } = useErrorHandler()
      try {
        await axiosInstance.post('/auth/login', { email, password })
        await this.fetchUserProfile() // populate profile after login
        return { success: true, message: 'Login successful' }
      } catch (error) {
        this.error = handleError(error) || 'Login failed'
        return { success: false, message: this.error }
      }
    },

    async register(userData: { name: string; email: string; password: string }) {
      const { handleError } = useErrorHandler()
      try {
        await axiosInstance.post('/auth/register', userData)
        return { success: true, message: 'Registration successful' }
      } catch (error) {
        this.error = handleError(error) || 'Registration failed'
        return { success: false, message: this.error }
      }
    },

    async fetchUserProfile() {
      const { handleError } = useErrorHandler()
      try {
        const response = await axiosInstance.get('/auth/me')
        this.profile = response.data
        this.error = null
        return { success: true, message: 'Profile fetched successfully' }
      } catch (error) {
        this.profile = null
        this.error = handleError(error) || 'Failed to fetch profile'
        return { success: false, message: this.error }
      }
    },

    async updatePassword(currentPassword: string, newPassword: string) {
      const { handleError } = useErrorHandler()
      try {
        await axiosInstance.put('/user/profile/password-change', { currentPassword, newPassword })
        return { success: true, message: 'Password updated successfully' }
      } catch (error) {
        this.error = handleError(error) || 'Failed to update password'
        return { success: false, message: this.error }
      }
    },

    async logout() {
      const { handleError } = useErrorHandler()
      try {
        await axiosInstance.post('/auth/logout')
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.profile = null
        this.error = null
      }
    },
  },
})
