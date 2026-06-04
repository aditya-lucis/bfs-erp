// src/stores/menu.js — tulis ulang dari scratch
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api.js'

export const useMenuStore = defineStore('menu', () => {
  const tree      = ref([])    // array, bukan undefined
  const myPerms   = ref({})
  const isReady   = ref(false)
  const isLoading = ref(false)

  async function init() {
    isLoading.value = true
    try {
      const [treeRes, permsRes] = await Promise.all([
        api.get('/rbac/menu-tree/'),
        api.get('/rbac/my-permissions/'),
      ])
      tree.value    = Array.isArray(treeRes.data) ? treeRes.data : []
      myPerms.value = permsRes.data || {}
      isReady.value = true
    } catch (err) {
      console.error('Menu init error:', err)
      tree.value    = []
      myPerms.value = {}
    } finally {
      isLoading.value = false
    }
  }

  function can(functionCode, action = 'can_read') {
    return myPerms.value?.[functionCode]?.[action] ?? false
  }

  function reset() {
    tree.value      = []
    myPerms.value   = {}
    isReady.value   = false
    isLoading.value = false
  }

  return {
    tree,
    myPerms,
    isReady,
    isLoading,
    init,
    can,
    reset,
  }
})