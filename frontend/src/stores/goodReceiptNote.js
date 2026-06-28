import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useGoodReceiptNoteStore = defineStore('goodReceiptNote', {
  state: () => ({
    grns: [],
    validVendors: [],
    validPOs: [],
    validCCs: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchGRNs(params = {}) {
      this.loading = true
      this.error = null
      try {
        let qs = new URLSearchParams(params).toString()
        const res = await api.get(`/purchase/good-receipt-notes/?${qs}`)
        this.grns = res.data.results || res.data
      } catch (err) {
        this.error = err.response?.data || err.message
      } finally {
        this.loading = false
      }
    },
    async fetchValidVendors() {
      try {
        const res = await api.get('/purchase/good-receipt-notes/get_valid_vendors/')
        this.validVendors = res.data
        return this.validVendors
      } catch (err) {
        console.error(err)
        return []
      }
    },
    async fetchValidPOs(vendorId) {
      try {
        const res = await api.get(`/purchase/good-receipt-notes/get_valid_pos/?vendor_id=${vendorId}`)
        this.validPOs = res.data
        return this.validPOs
      } catch (err) {
        console.error(err)
        return []
      }
    },
    async fetchValidCCs(poId) {
      try {
        const res = await api.get(`/purchase/good-receipt-notes/get_valid_ccs/?po_id=${poId}`)
        this.validCCs = res.data
        return this.validCCs
      } catch (err) {
        console.error(err)
        return []
      }
    },
    async createGRN(data) {
      this.loading = true
      this.error = null
      try {
        const formData = new FormData()
        Object.keys(data).forEach(key => {
          if (key === 'documents') {
            const docs = data[key]
            docs.forEach((doc, idx) => {
              formData.append(`documents[${idx}]master_document`, doc.master_document)
              formData.append(`documents[${idx}]is_available`, doc.is_available)
              if (doc.document_number) formData.append(`documents[${idx}]document_number`, doc.document_number)
              if (doc.keterangan) formData.append(`documents[${idx}]keterangan`, doc.keterangan)
              if (doc.file instanceof File) {
                formData.append(`documents[${idx}]file`, doc.file)
              }
            })
          } else {
            formData.append(key, data[key])
          }
        })

        const res = await api.post('/purchase/good-receipt-notes/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        this.grns.unshift(res.data)
        return res.data
      } catch (err) {
        this.error = err.response?.data || err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    async updateGRN(id, data) {
      this.loading = true
      this.error = null
      try {
        const formData = new FormData()
        Object.keys(data).forEach(key => {
          if (key === 'documents') {
            const docs = data[key]
            docs.forEach((doc, idx) => {
              formData.append(`documents[${idx}]master_document`, doc.master_document)
              formData.append(`documents[${idx}]is_available`, doc.is_available)
              if (doc.document_number) formData.append(`documents[${idx}]document_number`, doc.document_number)
              if (doc.keterangan) formData.append(`documents[${idx}]keterangan`, doc.keterangan)
              if (doc.file instanceof File) {
                formData.append(`documents[${idx}]file`, doc.file)
              }
            })
          } else {
            formData.append(key, data[key])
          }
        })

        const res = await api.put(`/purchase/good-receipt-notes/${id}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        const index = this.grns.findIndex(g => g.id === id)
        if (index !== -1) {
          this.grns[index] = res.data
        }
        return res.data
      } catch (err) {
        this.error = err.response?.data || err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    async submitGRN(id) {
      this.loading = true
      this.error = null
      try {
        const res = await api.post(`/purchase/good-receipt-notes/${id}/submit/`)
        const index = this.grns.findIndex(g => g.id === id)
        if (index !== -1) {
          this.grns[index] = res.data
        }
        return res.data
      } catch (err) {
        this.error = err.response?.data || err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    async voidGRN(id, reason) {
      this.loading = true
      this.error = null
      try {
        const res = await api.post(`/purchase/good-receipt-notes/${id}/void_grn/`, { void_reason: reason })
        return res.data
      } catch (err) {
        this.error = err.response?.data || err.message
        throw err
      } finally {
        this.loading = false
      }
    }
  }
})
