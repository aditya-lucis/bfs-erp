import { defineStore } from 'pinia'
import api from '../services/api.js'

export const usePurchaseOrderStore = defineStore('purchaseOrder', {
  state: () => ({
    pos: [],
    inboxPos: [],
    poDetails: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchPOs(params = {}) {
      this.loading = true
      try {
        const response = await api.get('/purchase/po/', { params })
        this.pos = response.data.results || response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal memuat daftar PO'
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchPODetails(id) {
      this.loading = true
      try {
        const response = await api.get(`/purchase/po/${id}/`)
        this.poDetails = response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal memuat detail PO'
        throw err
      } finally {
        this.loading = false
      }
    },

    async createPO(payload) {
      this.loading = true
      try {
        const response = await api.post('/purchase/po/', payload)
        return response.data
      } catch (err) {
        this.error = err.response?.data || 'Gagal membuat PO'
        throw err
      } finally {
        this.loading = false
      }
    },

    async patchPO(id, payload) {
      this.loading = true
      try {
        const response = await api.patch(`/purchase/po/${id}/`, payload)
        return response.data
      } catch (err) {
        this.error = err.response?.data || 'Gagal memperbarui PO parsial'
        throw err
      } finally {
        this.loading = false
      }
    },

    async updatePO(id, payload) {
      this.loading = true
      try {
        const response = await api.put(`/purchase/po/${id}/`, payload)
        return response.data
      } catch (err) {
        this.error = err.response?.data || 'Gagal memperbarui PO'
        throw err
      } finally {
        this.loading = false
      }
    },

    async deletePO(id) {
      this.loading = true
      try {
        await api.delete(`/purchase/po/${id}/`)
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal menghapus PO'
        throw err
      } finally {
        this.loading = false
      }
    },

    async submitPO(id) {
      this.loading = true
      try {
        const response = await api.post(`/purchase/po/${id}/submit/`)
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal submit PO'
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchPOInbox(params = {}) {
      this.loading = true
      try {
        const response = await api.get('/purchase/po-inbox/', { params })
        this.inboxPos = response.data.results || response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal memuat inbox PO'
        throw err
      } finally {
        this.loading = false
      }
    },

    async approvePO(id) {
      this.loading = true
      try {
        const response = await api.post(`/purchase/po-inbox/${id}/approve/`)
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal approve PO'
        throw err
      } finally {
        this.loading = false
      }
    },

    async rejectPO(id) {
      this.loading = true
      try {
        const response = await api.post(`/purchase/po-inbox/${id}/reject/`)
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal reject PO'
        throw err
      } finally {
        this.loading = false
      }
    }
  }
})
