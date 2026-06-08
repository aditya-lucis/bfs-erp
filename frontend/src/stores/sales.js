import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useSalesStore = defineStore('sales', {
  state: () => ({
    customers:        [],
    currentCustomer:  null,
    categories:       [],
    groups:           [],
    loading:          false,
    error:            null,
  }),

  actions: {

    // ── Customer list ──────────────────────────────────────────
    async fetchCustomers(params = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/sales/customers/', { params })
        this.customers = res.data.results ?? res.data
      } catch (e) {
        this.error = e
        this.customers = []
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchCustomer(id) {
      this.loading = true
      try {
        const res = await api.get(`/sales/customers/${id}/`)
        this.currentCustomer = res.data
      } catch (e) {
        this.error = e
      } finally {
        this.loading = false
      }
    },

    async createCustomer(payload) {
      const res = await api.post('/sales/customers/create/', payload)
      return res.data
    },

    async updateCustomer(id, payload) {
      const res = await api.patch(`/sales/customers/${id}/update/`, payload)
      return res.data
    },

    async deleteCustomer(id) {
      const res = await api.delete(`/sales/customers/${id}/delete/`)
      return res.data
    },

    // ── Linked Accounts ────────────────────────────────────────
    async saveLinkedAccounts(customerId, payload) {
      const res = await api.post(
        `/sales/customers/${customerId}/linked-accounts/save/`,
        payload
      )
      return res.data
    },

    // ── Terms ──────────────────────────────────────────────────
    async fetchTerms(customerId) {
      const res = await api.get(`/sales/customers/${customerId}/terms/`)
      return res.data
    },

    async saveTerms(customerId, payload) {
      const res = await api.patch(`/sales/customers/${customerId}/terms/`, payload)
      return res.data
    },

    // ── Contact Person ─────────────────────────────────────────
    async fetchContactPersons(customerId) {
      const res = await api.get(`/sales/customers/${customerId}/contact-persons/`)
      return res.data
    },

    async createContactPerson(customerId, payload) {
      const res = await api.post(
        `/sales/customers/${customerId}/contact-persons/`,
        payload
      )
      return res.data
    },

    async updateContactPerson(customerId, id, payload) {
      const res = await api.patch(
        `/sales/customers/${customerId}/contact-persons/${id}/`,
        payload
      )
      return res.data
    },

    async deleteContactPerson(customerId, id) {
      await api.delete(
        `/sales/customers/${customerId}/contact-persons/${id}/`
      )
    },

    // ── Master kecil ───────────────────────────────────────────
    async fetchCategories() {
      const res = await api.get('/sales/customer-categories/')
      this.categories = res.data.results ?? res.data
    },

    async fetchGroups() {
      const res = await api.get('/sales/customer-groups/')
      this.groups = res.data.results ?? res.data
    },
  },
})