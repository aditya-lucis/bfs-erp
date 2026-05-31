import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api.js'

export const useRbacStore = defineStore('rbac', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  const groups      = ref([])
  const groupDetail = ref(null)
  const menuTree    = ref([])
  const myPerms     = ref({})
  const isLoading   = ref(false)
  const error       = ref(null)

  // Pagination
  const pagination = ref({ count: 0, next: null, previous: null, page: 1 })

  // ── Groups ─────────────────────────────────────────────────────────────────
  async function fetchGroups(params = {}) {
    isLoading.value = true
    error.value     = null
    try {
      const res    = await api.get('/rbac/groups/', { params })
      groups.value = res.data.results || res.data
      pagination.value = {
        count:    res.data.count    || groups.value.length,
        next:     res.data.next     || null,
        previous: res.data.previous || null,
        page:     params.page       || 1,
      }
    } catch (err) {
      error.value = 'Gagal memuat data groups.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchGroupDetail(id) {
    isLoading.value   = true
    groupDetail.value = null
    try {
      const res         = await api.get(`/rbac/groups/${id}/`)
      groupDetail.value = res.data
    } catch (err) {
      error.value = 'Gagal memuat detail group.'
    } finally {
      isLoading.value = false
    }
  }

  async function createGroup(payload) {
    const res = await api.post('/rbac/groups/', payload)
    return res.data
  }

  async function updateGroup(id, payload) {
    const res = await api.patch(`/rbac/groups/${id}/`, payload)
    return res.data
  }

  async function deleteGroup(id) {
    await api.delete(`/rbac/groups/${id}/`)
  }

  // ── Group Functions (Function Assignment) ──────────────────────────────────
  async function fetchGroupFunctions(groupId) {
    const res = await api.get(`/rbac/groups/${groupId}/functions/`)
    return res.data
  }

  async function assignFunctions(groupId, functions) {
    const res = await api.post(
      `/rbac/groups/${groupId}/functions/assign/`,
      { functions },
    )
    return res.data
  }

  // ── Modules + Functions (untuk checklist) ──────────────────────────────────
  async function fetchModules() {
    const res = await api.get('/rbac/modules/')
    return res.data.results || res.data
  }

  async function fetchFunctions(params = {}) {
    const res = await api.get('/rbac/functions/', { params })
    return res.data.results || res.data
  }

  // ── Menu tree & permissions (untuk sidebar) ────────────────────────────────
  async function fetchMenuTree() {
    const res    = await api.get('/rbac/menu-tree/')
    menuTree.value = res.data
  }

  async function fetchMyPermissions() {
    const res    = await api.get('/rbac/my-permissions/')
    myPerms.value = res.data
  }

  // ── Users in Group ─────────────────────────────────────────────────────────
  async function fetchGroupUsers(groupId) {
    const res = await api.get(`/rbac/groups/${groupId}/users/`)
    return res.data
  }

  async function assignUsersToGroup(groupId, userIds) {
    const res = await api.post(
      `/rbac/groups/${groupId}/users/assign/`,
      { user_ids: userIds },
    )
    return res.data
  }

  async function removeUserFromGroup(groupId, userId) {
    await api.delete(`/rbac/groups/${groupId}/users/${userId}/remove/`)
  }

  return {
    groups, groupDetail, menuTree, myPerms,
    isLoading, error, pagination,
    fetchGroups, fetchGroupDetail, createGroup, updateGroup, deleteGroup,
    fetchGroupFunctions, assignFunctions,
    fetchModules, fetchFunctions,
    fetchMenuTree, fetchMyPermissions,
    fetchGroupUsers, assignUsersToGroup, removeUserFromGroup,
  }
})