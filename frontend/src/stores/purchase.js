import { defineStore } from 'pinia'
import api from '../services/api.js'

export const usePurchaseStore = defineStore('purchase', {
  state: () => ({
    vendors:        [],
    currentVendor:  null,
    categories:     [],
    groups:         [],
    loading:        false,
    error:          null,
  }),

  actions: {

    // ── Vendor list ──────────────────────────────────────────
    async fetchVendors(params = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/purchase/vendors/', { params })
        this.vendors = res.data.results ?? res.data
      } catch (e) {
        this.error = e
        this.vendors = []
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchVendor(id) {
      this.loading = true
      try {
        const res = await api.get(`/purchase/vendors/${id}/`)
        this.currentVendor = res.data
      } catch (e) {
        this.error = e
      } finally {
        this.loading = false
      }
    },

    async createVendor(payload) {
      const res = await api.post('/purchase/vendors/create/', payload)
      return res.data
    },

    async updateVendor(id, payload) {
      const res = await api.patch(`/purchase/vendors/${id}/update/`, payload)
      return res.data
    },

    async deleteVendor(id) {
      const res = await api.delete(`/purchase/vendors/${id}/delete/`)
      return res.data
    },

    // ── Linked Accounts ────────────────────────────────────────
    async saveLinkedAccounts(vendorId, payload) {
      const res = await api.post(
        `/purchase/vendors/${vendorId}/linked-accounts/save/`,
        payload
      )
      return res.data
    },

    // ── Terms ──────────────────────────────────────────────────
    async fetchTerms(vendorId) {
      const res = await api.get(`/purchase/vendors/${vendorId}/terms/`)
      return res.data
    },

    async saveTerms(vendorId, payload) {
      const res = await api.patch(`/purchase/vendors/${vendorId}/terms/`, payload)
      return res.data
    },

    // ── Contact Person ─────────────────────────────────────────
    async fetchContactPersons(vendorId) {
      const res = await api.get(`/purchase/vendors/${vendorId}/contact-persons/`)
      return res.data
    },

    async createContactPerson(vendorId, payload) {
      const res = await api.post(
        `/purchase/vendors/${vendorId}/contact-persons/`,
        payload
      )
      return res.data
    },

    async updateContactPerson(vendorId, id, payload) {
      const res = await api.patch(
        `/purchase/vendors/${vendorId}/contact-persons/${id}/`,
        payload
      )
      return res.data
    },

    async deleteContactPerson(vendorId, id) {
      await api.delete(
        `/purchase/vendors/${vendorId}/contact-persons/${id}/`
      )
    },

    // ── Master kecil ───────────────────────────────────────────
    async fetchCategories() {
      this.loading = true
      try {
        const res = await api.get('/purchase/vendor-categories/')
        this.categories = res.data.results ?? res.data
      } finally {
        this.loading = false
      }
    },

    async createCategory(payload) {
      const res = await api.post('/purchase/vendor-categories/', payload)
      return res.data
    },

    async updateCategory(id, payload) {
      const res = await api.put(`/purchase/vendor-categories/${id}/`, payload)
      return res.data
    },

    async deleteCategory(id) {
      const res = await api.delete(`/purchase/vendor-categories/${id}/`)
      return res.data
    },

    async fetchGroups() {
      const res = await api.get('/purchase/vendor-groups/')
      this.groups = res.data.results ?? res.data
    },

    async createGroup(payload) {
      const res = await api.post('/purchase/vendor-groups/', payload)
      return res.data
    },

    async updateGroup(id, payload) {
      const res = await api.put(`/purchase/vendor-groups/${id}/`, payload)
      return res.data
    },

    async deleteGroup(id) {
      const res = await api.delete(`/purchase/vendor-groups/${id}/`)
      return res.data
    },
  },
})
