import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '../types'
import { getMe } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)

  const isLoggedIn = () => !!token.value

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function clearToken() {
    token.value = ''
    localStorage.removeItem('token')
    user.value = null
  }

  async function fetchUser() {
    try {
      const res: any = await getMe()
      user.value = res
    } catch {
      clearToken()
    }
  }

  return { token, user, isLoggedIn, setToken, clearToken, fetchUser }
})
