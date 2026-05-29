import axios from 'axios'
import { message } from 'ant-design-vue'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      message.error('登录已过期，请重新登录')
    } else {
      const msg = error.response?.data?.detail || error.message || '请求失败'
      message.error(msg)
    }
    return Promise.reject(error)
  },
)

export default request
