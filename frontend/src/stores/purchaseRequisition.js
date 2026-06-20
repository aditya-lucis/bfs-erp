import { defineStore } from 'pinia'
import api from '../services/api.js'

export const usePurchaseRequisitionStore = defineStore('purchaseRequisition', {
  state: () => ({
    prs: [],
    inboxPrs: [],
    prDetails: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchPRs(params = {}) {
      this.loading = true
      try {
        const response = await api.get('/purchase/pr/', { params })
        this.prs = response.data.results || response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal memuat daftar PR'
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchPRDetails(id) {
      this.loading = true
      try {
        const response = await api.get(`/purchase/pr/${id}/`)
        this.prDetails = response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal memuat detail PR'
        throw err
      } finally {
        this.loading = false
      }
    },

    async createPR(payload) {
      this.loading = true
      try {
        const response = await api.post('/purchase/pr/', payload)
        return response.data
      } catch (err) {
        this.error = err.response?.data || 'Gagal membuat PR'
        throw err
      } finally {
        this.loading = false
      }
    },

    async updatePR(id, payload) {
      this.loading = true
      try {
        const response = await api.put(`/purchase/pr/${id}/`, payload)
        return response.data
      } catch (err) {
        this.error = err.response?.data || 'Gagal memperbarui PR'
        throw err
      } finally {
        this.loading = false
      }
    },

    async deletePR(id) {
      this.loading = true
      try {
        await api.delete(`/purchase/pr/${id}/`)
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal menghapus PR'
        throw err
      } finally {
        this.loading = false
      }
    },

    async submitPR(id) {
      this.loading = true
      try {
        const response = await api.post(`/purchase/pr/${id}/submit/`)
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal submit PR'
        throw err
      } finally {
        this.loading = false
      }
    },

    // --- Inbox ---
    async fetchInboxPRs(params = {}) {
      this.loading = true
      try {
        const response = await api.get('/purchase/pr-inbox/', { params })
        this.inboxPrs = response.data.results || response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal memuat daftar PR Inbox'
        throw err
      } finally {
        this.loading = false
      }
    },

    async processInboxPR(id, action, remarks, details = []) {
      this.loading = true
      try {
        const response = await api.post(`/purchase/pr-inbox/${id}/approve/`, {
          action,
          remarks,
          details
        })
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal memproses PR'
        throw err
      } finally {
        this.loading = false
      }
    }
  }
})
