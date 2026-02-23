import axios from 'axios'
import router from '@/router'
import { useUserStore } from '@/stores/user'

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8080/api/v1',
  withCredentials: true, // sends cookies automatically with every request
})

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      router.push('/login')
    }
    return Promise.reject(error)
  },
)

export default axiosInstance
