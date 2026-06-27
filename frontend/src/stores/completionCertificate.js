import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useCompletionCertificateStore = defineStore('completionCertificate', {
  state: () => ({
    certificates: [],
    validVendors: [],
    validPOs: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchCertificates() {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/purchase/completion-certificates/')
        this.certificates = res.data.results || res.data
      } catch (err) {
        this.error = err.response?.data || err.message
      } finally {
        this.loading = false
      }
    },
    async fetchValidVendors() {
      try {
        const res = await api.get('/purchase/completion-certificates/get_valid_vendors/')
        this.validVendors = res.data
      } catch (err) {
        console.error('Error fetching valid vendors', err)
      }
    },
    async fetchValidPOs(vendorId) {
      if (!vendorId) {
        this.validPOs = []
        return
      }
      try {
        const res = await api.get(`/purchase/completion-certificates/get_valid_pos/?vendor_id=${vendorId}`)
        this.validPOs = res.data
      } catch (err) {
        console.error('Error fetching valid POs', err)
      }
    },
    async createCertificate(payload) {
      this.error = null
      try {
        await api.post('/purchase/completion-certificates/', payload)
        await this.fetchCertificates()
      } catch (err) {
        this.error = err.response?.data || err.message
      }
    },
    async updateCertificate(id, payload) {
      this.error = null
      try {
        await api.put(`/purchase/completion-certificates/${id}/`, payload)
        await this.fetchCertificates()
      } catch (err) {
        this.error = err.response?.data || err.message
      }
    }
  }
})
