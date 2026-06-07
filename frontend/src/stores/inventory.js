import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api.js'

export const useInventoryStore = defineStore('inventory', () => {

  // ── State ──────────────────────────────────────────────────────────────────
  const units      = ref([])
  const categories = ref([])
  const items      = ref([])
  const choices    = ref(null)
  const isLoading  = ref(false)
  const error      = ref(null)

  // ── Unit Measurement ───────────────────────────────────────────────────────

  async function fetchUnits(params = {}) {
    isLoading.value = true
    try {
      const res   = await api.get('/inventory/units/', { params })
      units.value = res.data
    } catch (err) {
      console.error('Gagal memuat unit measurement', err)
    } finally {
      isLoading.value = false
    }
  }

  async function createUnit(payload) {
    const res = await api.post('/inventory/units/', payload)
    return res.data
  }

  async function updateUnit(id, payload) {
    const res = await api.patch(`/inventory/units/${id}/`, payload)
    return res.data
  }

  async function deleteUnit(id) {
    await api.delete(`/inventory/units/${id}/`)
  }

  // ── Item Category ──────────────────────────────────────────────────────────

  async function fetchCategories(params = {}) {
    isLoading.value = true
    try {
      const res      = await api.get('/inventory/categories/', { params })
      categories.value = res.data
    } catch (err) {
      console.error('Gagal memuat item category', err)
    } finally {
      isLoading.value = false
    }
  }

  async function createCategory(payload) {
    const res = await api.post('/inventory/categories/', payload)
    return res.data
  }

  async function updateCategory(id, payload) {
    const res = await api.patch(`/inventory/categories/${id}/`, payload)
    return res.data
  }

  async function deleteCategory(id) {
    await api.delete(`/inventory/categories/${id}/`)
  }

  // ── Items ──────────────────────────────────────────────────────────────────

  async function fetchItems(params = {}) {
    isLoading.value = true
    error.value     = null
    try {
      const res   = await api.get('/inventory/items/', { params })
      items.value = res.data.results ?? res.data
    } catch (err) {
      error.value = 'Gagal memuat data item.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchItem(id) {
    const res = await api.get(`/inventory/items/${id}/`)
    return res.data
  }

  async function createItem(formData) {
    const res = await api.post('/inventory/items/', formData, {
      headers: formData instanceof FormData
        ? { 'Content-Type': 'multipart/form-data' }
        : { 'Content-Type': 'application/json' },
    })
    return res.data
  }

  async function updateItem(id, formData) {
    const res = await api.patch(`/inventory/items/${id}/`, formData, {
      headers: formData instanceof FormData
        ? { 'Content-Type': 'multipart/form-data' }
        : { 'Content-Type': 'application/json' },
    })
    return res.data
  }

  async function deleteItem(id) {
    await api.delete(`/inventory/items/${id}/`)
  }

  async function uploadItemImage(id, file) {
    const fd = new FormData()
    fd.append('image', file)
    const res = await api.post(`/inventory/items/${id}/upload-image/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  }

  // ── Account Links ──────────────────────────────────────────────────────────

  async function fetchAccountLinks(itemId) {
    const res = await api.get(`/inventory/items/${itemId}/accounts/`)
    return res.data
  }

  async function createAccountLink(itemId, payload) {
    const res = await api.post(`/inventory/items/${itemId}/accounts/`, payload)
    return res.data
  }

  async function deleteAccountLink(itemId, linkId) {
    await api.delete(`/inventory/items/${itemId}/accounts/${linkId}/`)
  }

  // ── Choices ────────────────────────────────────────────────────────────────

  async function fetchChoices() {
    if (choices.value) return
    try {
      const res  = await api.get('/inventory/choices/')
      choices.value = res.data
    } catch (err) {
      console.error('Gagal memuat choices inventory', err)
    }
  }

  return {
    units, categories, items, choices, isLoading, error,
    fetchUnits, createUnit, updateUnit, deleteUnit,
    fetchCategories, createCategory, updateCategory, deleteCategory,
    fetchItems, fetchItem, createItem, updateItem, deleteItem, uploadItemImage,
    fetchAccountLinks, createAccountLink, deleteAccountLink,
    fetchChoices,
  }
})