import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useGrnSesDocumentStore = defineStore('grnSesDocument', {
  state: () => ({
    documents: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchDocuments() {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/purchase/grn-ses-documents/')
        this.documents = res.data.results || res.data
      } catch (err) {
        this.error = err.response?.data || err.message
      } finally {
        this.loading = false
      }
    },
    async createDocument(payload) {
      this.error = null
      try {
        await api.post('/purchase/grn-ses-documents/', payload)
        await this.fetchDocuments()
      } catch (err) {
        this.error = err.response?.data || err.message
      }
    },
    async updateDocument(id, payload) {
      this.error = null
      try {
        await api.put('/purchase/grn-ses-documents/' + id + '/', payload)
        await this.fetchDocuments()
      } catch (err) {
        this.error = err.response?.data || err.message
      }
    },
    async deleteDocument(id) {
      this.error = null
      try {
        await api.delete('/purchase/grn-ses-documents/' + id + '/')
        await this.fetchDocuments()
      } catch (err) {
        this.error = err.response?.data || err.message
      }
    }
  }
})

