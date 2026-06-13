/**
 * BFS ERP — Annual Budget Store
 * src/stores/annualBudget.js
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api.js'

export const useAnnualBudgetStore = defineStore('annualBudget', () => {
  // ── State ────────────────────────────────────────────────────────────────
  const headers = ref([])
  const currentHeader = ref(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)

  // ── Headers ──────────────────────────────────────────────────────────────
  async function fetchHeaders(params = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/annual-budget/headers/', { params })
      headers.value = res.data.results ?? res.data
      return headers.value
    } catch (e) {
      error.value = e?.response?.data?.detail || 'Gagal memuat data.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchHeader(id) {
    loading.value = true
    try {
      const res = await api.get(`/annual-budget/headers/${id}/`)
      currentHeader.value = res.data
      return res.data
    } finally {
      loading.value = false
    }
  }

  async function createHeader(payload) {
    saving.value = true
    try {
      const res = await api.post('/annual-budget/headers/', payload)
      headers.value.unshift(res.data)
      return res.data
    } finally {
      saving.value = false
    }
  }

  async function updateHeader(id, payload) {
    saving.value = true
    try {
      const res = await api.patch(`/annual-budget/headers/${id}/`, payload)
      const idx = headers.value.findIndex(h => h.id === id)
      if (idx !== -1) headers.value[idx] = res.data
      if (currentHeader.value?.id === id) currentHeader.value = res.data
      return res.data
    } finally {
      saving.value = false
    }
  }

  async function deleteHeader(id) {
    await api.delete(`/annual-budget/headers/${id}/`)
    headers.value = headers.value.filter(h => h.id !== id)
  }

  async function initLines(headerId) {
    saving.value = true
    try {
      const res = await api.post(`/annual-budget/headers/${headerId}/init-lines/`)
      return res.data
    } finally {
      saving.value = false
    }
  }

  // ── Lines ─────────────────────────────────────────────────────────────────
  async function fetchLines(headerId) {
    const res = await api.get('/annual-budget/lines/', { params: { header: headerId } })
    return res.data.results ?? res.data
  }

  async function createLine(payload) {
    const res = await api.post('/annual-budget/lines/', payload)
    return res.data
  }

  async function deleteLine(id) {
    await api.delete(`/annual-budget/lines/${id}/`)
  }

  async function bulkUpdateMonths(lineId, months, note = '') {
    saving.value = true
    try {
      const res = await api.patch(`/annual-budget/lines/${lineId}/bulk-update/`, {
        months,
        note,
      })
      return res.data
    } finally {
      saving.value = false
    }
  }

  async function updateMonth(lineId, month, budget, note = '') {
    const res = await api.patch(`/annual-budget/lines/${lineId}/update-month/`, {
      month, budget, note,
    })
    return res.data
  }

  async function fetchLineLogs(lineId) {
    const res = await api.get(`/annual-budget/lines/${lineId}/logs/`)
    return res.data.results ?? res.data
  }

  // ── Budget Component Picker ───────────────────────────────────────────────
  async function fetchBudgetComponents(departmentId, headerId = null) {
    const params = { department: departmentId }
    if (headerId) params.header = headerId
    const res = await api.get('/annual-budget/budget-components/', { params })
    return res.data
  }

  // ── Summary ───────────────────────────────────────────────────────────────
  async function fetchSummary(year) {
    const res = await api.get('/annual-budget/summary/', { params: { year } })
    return res.data
  }

  return {
    headers,
    currentHeader,
    loading,
    saving,
    error,
    fetchHeaders,
    fetchHeader,
    createHeader,
    updateHeader,
    deleteHeader,
    initLines,
    fetchLines,
    createLine,
    deleteLine,
    bulkUpdateMonths,
    updateMonth,
    fetchLineLogs,
    fetchBudgetComponents,
    fetchSummary,
  }
})
