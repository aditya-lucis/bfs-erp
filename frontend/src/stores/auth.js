// src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api.js'
import { useMenuStore } from './menu.js'

export const useAuthStore = defineStore('auth', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  const user        = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const isLoading   = ref(false)
  const error       = ref(null)

  // ── Getters ────────────────────────────────────────────────────────────────
  const isLoggedIn  = computed(() => !!accessToken.value)
  const isSuperuser = computed(() => user.value?.is_superuser || false)
  const fullName    = computed(() => user.value?.full_name || user.value?.username || '')
  const employee    = computed(() => user.value?.employee || null)

  async function login(username, password) {
    isLoading.value = true
    error.value     = null
    try {
      const res = await api.post('/auth/login/', { username, password })
      accessToken.value = res.data.access
      localStorage.setItem('access_token',  res.data.access)
      localStorage.setItem('refresh_token', res.data.refresh)

      await fetchMe()

      // ← Wrap init() sendiri — jangan crash login kalau menu gagal
      try {
        const menuStore = useMenuStore()
        await menuStore.init()
      } catch (menuErr) {
        console.warn('Menu init gagal, lanjut tanpa menu:', menuErr)
      }

      return true   // ← tetap return true meskipun menu gagal
    } catch (err) {
      error.value = err.response?.data?.non_field_errors?.[0]
                || err.response?.data?.detail
                || 'Login gagal.'
      return false
    } finally {
      isLoading.value = false
    }
}

  async function fetchMe() {
    try {
      const res  = await api.get('/auth/whoami/')
      user.value = res.data
    } catch {
      logout()
    }
  }

  async function restoreSession() {
    if (accessToken.value && !user.value) {
      await fetchMe()
      try {
        const menuStore = useMenuStore()
        await menuStore.init()
      } catch (err) {
        console.warn('Menu restore gagal:', err)
      }
    }
  }

  async function logout() {
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) await api.post('/auth/logout/', { refresh })
    } catch { /* tetap logout */ } finally {
      try {
        const menuStore = useMenuStore()
        menuStore.reset()
      } catch { /* ignore */ }

      user.value        = null
      accessToken.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  return {
    user, accessToken, isLoading, error,
    isLoggedIn, isSuperuser, fullName, employee,
    login, logout, fetchMe, restoreSession,
  }
})